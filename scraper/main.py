import asyncio
import json
import logging
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError


# Configure logging to stderr so stdout can remain clean JSON
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


FB_BASE = "https://www.facebook.com"
# Relaxed permalink regex: match common post types and allow non-digit ids/paths
PERMALINK_REGEX = re.compile(
    r"/groups/[^/]+/(?:permalink|posts|videos|photos|reels)/[^/?#]+",
    re.IGNORECASE,
)


def is_comment_permalink(url: str) -> bool:
    """Heuristic to detect comment permalinks (exclude from results)."""
    u = url.lower()
    return (
        "comment_id=" in u
        or "reply_comment_id=" in u
        or "/comment/" in u
    )


def build_group_url(raw_url: str) -> str:
    """Normalize the group URL to include chronological sorting."""
    raw_url = raw_url.strip()
    if not raw_url:
        return raw_url
    # Ensure we hit www instead of m.facebook
    if raw_url.startswith("http") and "facebook.com" in raw_url and "//m." in raw_url:
        raw_url = raw_url.replace("//m.", "//www.")
    if "?" in raw_url:
        return raw_url + "&sorting_setting=CHRONOLOGICAL"
    return raw_url + "?sorting_setting=CHRONOLOGICAL"


async def dismiss_login_popup(page: Page) -> None:
    """Try to close/dismiss login/signup popups or banners if present.

    This uses several heuristics and ignores failures.
    """
    candidates = [
        # Dialog close buttons
        'div[role="dialog"] [aria-label="Close"]',
        'div[aria-label="Close"]',
        'div[role="dialog"] svg[aria-label="Close"]',
        # Buttons that might defer login
        'div[role="dialog"] button:has-text("Not now")',
        'div[role="dialog"] button:has-text("Not Now")',
        # Cookie or login banners
        'div[role="dialog"] [data-testid="cookie-policy-dialog-accept-button"]',
    ]
    for sel in candidates:
        try:
            locator = page.locator(sel).first
            if await locator.is_visible(timeout=1000):
                await locator.click(timeout=1000)
                logger.debug("Dismissed popup via selector: %s", sel)
                await asyncio.sleep(0.2)
        except PlaywrightTimeoutError:
            continue
        except Exception as e:
            logger.debug("Ignoring popup dismiss error for %s: %s", sel, e)


async def expand_post_text(article) -> None:
    """Attempt to expand truncated post text (e.g., 'See more')."""
    expand_selectors = [
        "div[role='button']:has-text('See more')",
        "span:has-text('See more')",
        # Some locales may have different casing or phrasing; try generic 'See'
        "div[role='button']:has-text('See')",
    ]
    for sel in expand_selectors:
        try:
            btn = article.locator(sel).first
            if await btn.is_visible(timeout=700):
                await btn.click(timeout=700)
                await asyncio.sleep(0.1)
        except PlaywrightTimeoutError:
            continue
        except Exception:
            # Non-fatal
            continue


async def parse_post(article) -> Optional[Dict[str, str]]:
    """Parse a single post article locator to extract permalink and text content.

    Returns a dict {"permalink": str, "content": str} or None on failure.
    """
    try:
        # Expand any truncated text
        await expand_post_text(article)

        # Find permalink: scan links within the article for a canonical post URL
        links = article.locator("a[href*='/groups/']")
        href: Optional[str] = None
        try:
            count = await links.count()
        except Exception:
            count = 0
        for i in range(count):
            try:
                el = links.nth(i)
                url = await el.get_attribute("href")
                if not url:
                    continue
                if PERMALINK_REGEX.search(url):
                    href = url
                    break
            except Exception:
                continue

        if not href:
            # Some links are relative, or hidden inside nested elements
            # Fallback: look for timestamp style links
            ts_candidates = article.locator("a[aria-label*=' ago'], a[aria-label*='Yesterday'], a[aria-label*='mins'], a[aria-label*='hrs']")
            try:
                if await ts_candidates.count() > 0:
                    href = await ts_candidates.first.get_attribute("href")
            except Exception:
                pass

        if not href:
            logger.debug("No permalink found for a post; skipping")
            return None

        if href.startswith("/"):
            permalink = FB_BASE + href
        elif href.startswith("http"):
            permalink = href
        else:
            permalink = FB_BASE + "/" + href.lstrip("/")

        # Skip comment permalinks
        if is_comment_permalink(permalink):
            logger.debug("Comment permalink detected; skipping %s", permalink)
            return None

        # Extract content: prioritize the message container, fallback to a simpler text block selector
        content_text = ""
        # Primary selector used by FB for post message
        message_container = article.locator("div[data-ad-preview='message']")
        try:
            if await message_container.count() > 0:
                content_text = (await message_container.first.inner_text()).strip()
        except Exception:
            pass

        if not content_text:
            # Secondary simple selector often used for text blocks
            secondary = article.locator("div[data-ad-preview] > div > span")
            try:
                if await secondary.count() > 0:
                    content_text = (await secondary.first.inner_text()).strip()
            except Exception:
                pass

        # Final sanity
        if not content_text:
            logger.debug("Empty content for post %s; skipping", permalink)
            return None

        return {"permalink": permalink, "content": content_text}

    except Exception as e:
        logger.warning("Failed to parse a post: %s", e)
        return None


async def scrape_group(browser: Browser, group_url: str) -> List[Dict[str, str]]:
    """Scrape a Facebook group page (no-login) for visible posts and their permalinks."""
    context = await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 900},
        locale="en-US",
        java_script_enabled=True,
    )
    page = await context.new_page()

    try:
        # Navigate
        url = build_group_url(group_url)
        logger.info("Navigating to %s", url)
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)

        # Handle potential blocking popups
        await dismiss_login_popup(page)

        # Wait a bit for initial content to populate
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except PlaywrightTimeoutError:
            logger.debug("networkidle wait timed out; continuing")
        await asyncio.sleep(1.5)

        # Perform exactly one gentle scroll to load one more batch
        try:
            await page.mouse.wheel(0, 1500)
            # Give time for new posts to load
            try:
                await page.wait_for_load_state("networkidle", timeout=12000)
            except PlaywrightTimeoutError:
                pass
            await asyncio.sleep(2.0)
        except Exception as e:
            logger.debug("Scroll failed or not supported: %s", e)

        # Find visible posts
        articles = page.locator("div[role='article']")
        results: List[Dict[str, str]] = []
        seen = set()  # in-run deduplication by permalink
        count = 0
        try:
            count = await articles.count()
        except Exception:
            count = 0
        logger.info("Found approximately %d article nodes", count)

        # Iterate current set of posts
        limit = min(count, 20)  # safety cap
        for i in range(limit):
            art = articles.nth(i)
            try:
                if not await art.is_visible():
                    continue
            except Exception:
                pass
            parsed = await parse_post(art)
            if parsed:
                pl = parsed.get("permalink")
                if pl and pl not in seen:
                    seen.add(pl)
                    results.append(parsed)
                else:
                    logger.debug("Duplicate permalink skipped: %s", pl)

        return results

    finally:
        try:
            await page.close()
        except Exception:
            pass
        try:
            await context.close()
        except Exception:
            pass


async def main_async(group_url: str) -> int:
    """Entry point for async scraping job. Returns exit code."""
    # Launch Chromium with flags suitable for containers like Cloud Run
    launch_args = {
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
            "--no-zygote",
        ],
        # SlowMo can be helpful during debugging; keep it off in production
        # "slow_mo": 50,
    }

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(**launch_args)
        try:
            posts = await scrape_group(browser, group_url)
        except Exception as e:
            logger.error("Unhandled error during scrape: %s", e)
            posts = []
        finally:
            try:
                await browser.close()
            except Exception:
                pass

    # Print as JSON array to stdout
    print(json.dumps(posts, ensure_ascii=False))
    # Return success even if empty; the pipeline can decide how to handle it
    return 0


def parse_args(argv: List[str]) -> Optional[str]:
    if len(argv) < 2:
        logger.error("Usage: python -m scraper.main <facebook_group_url>")
        return None
    return argv[1]


def main() -> None:
    url = parse_args(sys.argv)
    if not url:
        # Don't print anything else to stdout; exit non-zero
        sys.exit(2)
    try:
        exit_code = asyncio.run(main_async(url))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

import asyncio
import json
import logging
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse  # added for permalink cleaning
from dataclasses import dataclass, asdict  # dataclass for structured posts

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


def clean_permalink(url: str) -> str:
    """Strip tracking / transient query parameters from a Facebook post URL.

    We keep only scheme + netloc + path. This helps deduplication and gives a
    stable canonical key for downstream processing.
    """
    try:
        parsed = urlparse(url)
        # Normalize host to www.facebook.com
        netloc = parsed.netloc
        if netloc.endswith("facebook.com") and not netloc.startswith("www."):
            netloc = "www.facebook.com"
        # Remove trailing slash (except root)
        path = re.sub(r"/$", "", parsed.path)
        cleaned = urlunparse((parsed.scheme or "https", netloc, path, "", "", ""))
        return cleaned
    except Exception:
        return url


# Patterns for images we want to exclude (emoji / decorative assets)
EXCLUDED_IMAGE_SUBSTRINGS = [
    "emoji.php",
    "/assets/?",  # generic, may refine later
]


@dataclass
class ScrapedPost:
    permalink: str
    content: str
    image_urls: List[str]
    video_thumbnail_url: Optional[str]


async def parse_post(article, media_enabled: bool) -> Optional[ScrapedPost]:
    """Parse a single post article locator to extract permalink, text content and media.

    Returns a ScrapedPost or None on failure.
    media_enabled controls whether images / video thumbnail are scraped.
    """
    try:
        await expand_post_text(article)

        # Consolidated permalink discovery
        href: Optional[str] = None
        try:
            link_loc = article.locator("a[href*='/groups/']")
            for i in range(await link_loc.count()):
                url = await link_loc.nth(i).get_attribute("href")
                if not url:
                    continue
                if PERMALINK_REGEX.search(url.split("?")[0]):
                    href = url
                    break
            if not href:
                ts_loc = article.locator(
                    "a[aria-label*=' ago'], a[aria-label*='Yesterday'], a[aria-label*='mins'], a[aria-label*='hrs']"
                )
                if await ts_loc.count() > 0:
                    href = await ts_loc.first.get_attribute("href")
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
        permalink = clean_permalink(permalink)

        if is_comment_permalink(permalink):
            logger.debug("Comment permalink detected; skipping %s", permalink)
            return None

        content_text = ""
        msg_loc = article.locator("div[data-ad-preview='message']")
        try:
            if await msg_loc.count() > 0:
                content_text = (await msg_loc.first.inner_text()).strip()
        except Exception:
            pass
        if not content_text:
            secondary = article.locator("div[data-ad-preview] > div > span")
            try:
                if await secondary.count() > 0:
                    content_text = (await secondary.first.inner_text()).strip()
            except Exception:
                pass
        if not content_text:
            logger.debug("Empty content for post %s; skipping", permalink)
            return None

        image_urls: List[str] = []
        video_thumbnail_url: Optional[str] = None
        if media_enabled:
            try:
                imgs = article.locator("img")
                for i in range(min(await imgs.count(), 40)):
                    try:
                        src = await imgs.nth(i).get_attribute("src")
                        if (
                            src
                            and src.startswith("http")
                            and not any(pat in src for pat in EXCLUDED_IMAGE_SUBSTRINGS)
                            and src not in image_urls
                        ):
                            image_urls.append(src)
                    except Exception:
                        continue
            except Exception:
                pass
            try:
                thumb_parent = article.locator("div[role='button']:has(svg[aria-label='Play'])")
                if await thumb_parent.count() > 0:
                    img_in = thumb_parent.first.locator("img").first
                    if await img_in.count() > 0:
                        src = await img_in.get_attribute("src")
                        if src and src.startswith("http") and not any(p in src for p in EXCLUDED_IMAGE_SUBSTRINGS):
                            video_thumbnail_url = src
            except Exception:
                pass

        return ScrapedPost(
            permalink=permalink,
            content=content_text,
            image_urls=image_urls,
            video_thumbnail_url=video_thumbnail_url,
        )

    except Exception as e:
        logger.warning("Failed to parse a post: %s", e)
        return None


async def scrape_group(browser: Browser, group_url: str, media_enabled: bool) -> List[ScrapedPost]:
    """Scrape a Facebook group page (no-login) for visible posts and their permalinks.

    media_enabled toggles media extraction.
    """
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

        # Wait for at least one article (more deterministic than only networkidle)
        try:
            await page.wait_for_selector("div[role='article']", timeout=15000)
        except PlaywrightTimeoutError:
            logger.debug("No article appeared within timeout after navigation")
        # Additional small delay to let initial batch populate
        await asyncio.sleep(1.0)

        # Also attempt network idle, but don't rely solely on it
        try:
            await page.wait_for_load_state("networkidle", timeout=8000)
        except PlaywrightTimeoutError:
            pass

        # Locate articles BEFORE scroll
        articles = page.locator("div[role='article']")
        try:
            initial_count = await articles.count()
        except Exception:
            initial_count = 0
        logger.debug("Initial article count before scroll: %d", initial_count)

        # Perform exactly one gentle scroll to load one more batch
        try:
            await page.mouse.wheel(0, 1500)
        except Exception as e:
            logger.debug("Scroll failed or not supported: %s", e)

        # Poll for growth in article count (up to 8s) after scroll
        poll_deadline = time.time() + 8.0
        last_count = initial_count
        while time.time() < poll_deadline:
            try:
                current = await articles.count()
            except Exception:
                break
            if current > last_count:
                logger.debug("Article count increased %d -> %d", last_count, current)
                last_count = current
                # Allow one more short cycle to capture any trailing loads
            await asyncio.sleep(0.6)
        final_count = last_count
        logger.info("Final article count after scroll/poll: %d", final_count)

        results: List[ScrapedPost] = []
        seen = set()  # in-run deduplication by permalink

        # Iterate current set of posts (cap at 40 now that we may have more)
        limit = min(final_count, 40)
        for i in range(limit):
            art = articles.nth(i)
            try:
                if not await art.is_visible():
                    continue
            except Exception:
                pass
            parsed = await parse_post(art, media_enabled=media_enabled)
            if parsed:
                pl = parsed.permalink
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


async def main_async(group_url: str, headless: bool, media_enabled: bool) -> int:
    """Entry point for async scraping job. Returns exit code."""
    launch_args = {
        "headless": headless,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
            "--no-zygote",
        ],
    }
    if not headless:
        logger.info("Running in headful (non-headless) mode for debugging")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(**launch_args)
        try:
            posts = await scrape_group(browser, group_url, media_enabled=media_enabled)
        except Exception as e:
            logger.error("Unhandled error during scrape: %s", e)
            posts: List[ScrapedPost] = []
        finally:
            try:
                await browser.close()
            except Exception:
                pass

    # Convert dataclasses to dicts for JSON serialization
    posts_json = [asdict(p) for p in posts]
    print(json.dumps(posts_json, ensure_ascii=False))
    # Return success even if empty; the pipeline can decide how to handle it
    return 0


def parse_args(argv: List[str]) -> Optional[Dict[str, Any]]:
    """Parse CLI args.

    Supports:
      --headful   run with a visible browser
      --no-media  disable image & video thumbnail scraping
    Returns dict with keys: url, headless, media_enabled
    """
    if len(argv) < 2:
        logger.error("Usage: python -m scraper.main [--headful] [--no-media] <facebook_group_url>")
        return None
    headless = True
    media_enabled = True
    positional: List[str] = []
    for arg in argv[1:]:
        if arg == "--headful":
            headless = False
        elif arg == "--no-media":
            media_enabled = False
        elif arg.startswith("--"):
            logger.warning("Unknown flag ignored: %s", arg)
        else:
            positional.append(arg)
    if not positional:
        logger.error("Group URL missing")
        return None
    return {"url": positional[-1], "headless": headless, "media_enabled": media_enabled}


def main() -> None:
    parsed = parse_args(sys.argv)
    if not parsed:
        sys.exit(2)
    try:
        exit_code = asyncio.run(main_async(parsed["url"], parsed["headless"], parsed["media_enabled"]))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

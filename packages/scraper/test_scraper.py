import time
from playwright.sync_api import sync_playwright

# URL của một group Facebook công khai để test
# Thay bằng group bạn muốn test
TARGET_URL = "https://www.facebook.com/groups/phongtrometrimydinhcaugiay/?sorting_setting=CHRONOLOGICAL"

def run_test_scrape():
    # sync_playwright() là trình quản lý ngữ cảnh, đảm bảo trình duyệt được đóng đúng cách
    with sync_playwright() as p:
        # Khởi chạy một trình duyệt Chromium (giống Chrome). headless=False để bạn có thể xem nó chạy.
        # Khi chạy trên server, bạn sẽ đổi thành headless=True
        browser = p.chromium.launch(headless=False, slow_mo=50)
        
        # Tạo một trang mới trong trình duyệt
        page = browser.new_page()
        
        print(f"Đang điều hướng đến: {TARGET_URL}")
        # Điều hướng đến URL mục tiêu. timeout=60000 tăng thời gian chờ lên 60 giây.
        page.goto(TARGET_URL, timeout=60000)
        
        print("Trang đã tải. Chờ xử lý popup đăng nhập (nếu có)...")
        # Facebook thường có popup đăng nhập. Chúng ta sẽ thử tìm nút "Đóng" và click vào nó.
        # Dấu 'div[aria-label="Đóng"]' là một CSS selector. Bạn có thể cần phải thay đổi nó.
        close_button_selector = 'div[aria-label="Close"]' # Tiếng Anh
        # close_button_selector = 'div[aria-label="Đóng"]' # Tiếng Việt
        
        try:
            # Chờ nút đóng xuất hiện trong tối đa 5 giây
            close_button = page.locator(close_button_selector).first
            if close_button.is_visible(timeout=5000):
                print("Phát hiện popup đăng nhập. Đang đóng...")
                close_button.click()
        except Exception as e:
            print("Không tìm thấy popup đăng nhập hoặc có lỗi, tiếp tục...")

        print("Đang cuộn xuống để tải thêm bài viết...")
        # Cuộn trang xuống một chút để kích hoạt tải thêm nội dung
        page.mouse.wheel(0, 1500)
        time.sleep(3) # Chờ một chút để nội dung tải
        
        # Đây là bước quan trọng: Chờ một selector đặc trưng của bài viết xuất hiện.
        # Selector này có thể thay đổi. Đây là ví dụ.
        post_selector = 'div[data-ad-preview="message"]'
        print(f"Đang chờ bài viết đầu tiên xuất hiện với selector: {post_selector}")
        page.wait_for_selector(post_selector, timeout=30000)
        
        print("Đã tìm thấy bài viết! Chụp ảnh màn hình...")
        # Chụp ảnh màn hình và lưu lại với tên 'facebook_test.png'
        page.screenshot(path="facebook_test.png", full_page=True)
        
        print("Hoàn thành! Đóng trình duyệt.")
        browser.close()

if __name__ == "__main__":
    run_test_scrape()
    print("\nKiểm tra file 'facebook_test.png' trong cùng thư mục để xem kết quả.")
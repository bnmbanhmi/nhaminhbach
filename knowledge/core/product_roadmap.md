# Product Roadmap
#core

### **Lộ Trình Xây Dựng Sản Phẩm V2 (The Battle-Tested Roadmap)**

*Đây là kế hoạch đã được tôi luyện qua thực tế. Nó tập trung vào việc xây dựng tài sản cốt lõi (dữ liệu sạch) và tạo ra giá trị cho người dùng một cách nhanh nhất.*

---

#### **Giai đoạn 1: Xây dựng Nền tảng & Nhà máy Dữ liệu (Foundation & Data Factory)**
*(Đây là giai đoạn chúng ta vừa hoàn thành. Nó lớn hơn nhiều so với dự tính ban đầu, nhưng bây giờ nó là một lợi thế cạnh tranh cực lớn.)*

*   **Mục tiêu:** Xây dựng một nền tảng kỹ thuật vững chắc và một quy trình bán tự động để thu thập và làm sạch dữ liệu.
*   **Trạng thái:** **ĐÃ HOÀN THÀNH.**
*   **Các thành phần chính đã xây dựng:**
    1.  **Hạ tầng Cloud (GCP):** Cloud SQL, Cloud Run, Pub/Sub, Scheduler, Artifact Registry, Secret Manager.
    2.  **API Backend:** Bộ API CRUD cho `listings` và `attributes`.
    3.  **Công cụ Scraper (Local):** Script Playwright mạnh mẽ để thu thập dữ liệu thô.
    4.  **"Buồng lái QC":** Giao diện nội bộ, thông minh, để Founder (là bạn) có thể làm sạch, cấu trúc hóa, và duyệt dữ liệu.
    5.  **Cầu nối Local-to-Cloud:** API `ingest_scraped_data` để nhận dữ liệu từ scraper.

---

#### **Giai đoạn 2: MVP Công khai - "Nguồn Thông tin Sạch nhất" (Public MVP)**
*(Đây là giai đoạn chúng ta đang ở. Nó tương đương với "Cái Rổ Thông Tin" nhưng đã được nâng cấp.)*

*   **Mục tiêu:** Ra mắt phiên bản đầu tiên cho người dùng, chứng minh giá trị cốt lõi là **sự tin cậy và tiết kiệm thời gian**.
*   **Trạng thái:** **ĐANG THỰC HIỆN.**
*   **Các tính năng CẦN HOÀN THÀNH:**
    1.  **Giao diện Hiển thị Danh sách & Chi tiết:** Đã xong.
    2.  **Bộ lọc Tối thiểu:**
        *   Lọc theo **Quận/Huyện** (Bắt buộc).
        *   Lọc theo **Khoảng giá** (Bắt buộc).
        *   Lọc theo một vài **Thuộc tính boolean quan trọng nhất** (ví dụ: "Điều hoà", "Nóng lạnh", "Chung chủ").
    3.  **Link trỏ về bài đăng gốc:** Đã có trong database, cần hiển thị trên UI.
    4.  **Thiết kế đáp ứng (Responsive Design):** Đảm bảo trang web hoạt động tốt trên cả máy tính và điện thoại.

*   **Tuyệt đối KHÔNG có (Giữ nguyên):** Đăng ký/Đăng nhập, Bình luận, AI, Chatbot, Đăng tin trực tiếp.

---

#### **Giai đoạn 3: Tối ưu hóa Trải nghiệm & Xây dựng Lòng tin (Experience & Trust)**
*(Đây là phiên bản thực tế hơn của "Công Cụ Cộng Đồng".)*

*   **Mục tiêu:** Dựa trên phản hồi từ người dùng đầu tiên, làm cho sản phẩm trở nên hữu ích và đáng tin cậy hơn một cách rõ rệt.
*   **Các tính năng tiềm năng (Ưu tiên từ trên xuống):**
    1.  **Cải thiện Tốc độ & Hiệu năng:** Tối ưu hóa việc tải trang, đặc biệt là hình ảnh.
    2.  **Bộ lọc Nâng cao:** Thêm khả năng lọc theo nhiều thuộc tính hơn (Loại phòng, Diện tích, Cho phép vật nuôi...).
    3.  **Tìm kiếm theo Từ khóa:** Một thanh tìm kiếm đơn giản để tìm trong `title` và `description`.
    4.  **Nút "Báo cáo Tin không chính xác / Đã cho thuê":** Đây là cơ chế thu thập phản hồi đầu tiên từ cộng đồng. Dữ liệu này sẽ được gửi về cho bạn để xem xét.
    5.  **Trang "Giới thiệu" & "Liên hệ":** Xây dựng sự tin tưởng bằng cách cho người dùng biết chúng ta là ai và tại sao chúng ta làm điều này.
    6.  **Lưu tin đã xem/yêu thích (dùng Local Storage):** Một tính năng đơn giản không cần đăng nhập, cho phép người dùng đánh dấu các tin họ quan tâm.

---

#### **Giai đoạn 4: Tầm nhìn Tương lai - "Nền tảng Giao dịch Tin cậy"**
*(Đây là phiên bản thực tế hơn của "Nền tảng Tin cậy".)*

*   **Mục tiêu:** Trở thành nơi không chỉ để tìm kiếm, mà còn để ra quyết định và thực hiện các bước tiếp theo một cách an toàn.
*   **Các tính năng tiềm năng:**
    1.  **Hệ thống Đánh giá & Huy hiệu (Trust System):**
        *   Huy hiệu "Chính chủ đã xác thực" (yêu cầu quy trình xác thực thủ công hoặc bán tự động).
        *   Hệ thống review ẩn danh (chỉ dành cho những người đã thực sự tương tác, có thể dựa trên một cơ chế nào đó).
    2.  **Tự động hóa "Nhà máy Lọc dầu" (AI-Powered QC):**
        *   Sử dụng dữ liệu từ "Buồng lái QC" để huấn luyện các mô hình AI nhỏ.
        *   **Mục tiêu:** Tự động **phân loại** (ví dụ: "cho thuê" vs. "bán đồ"), tự động **gán nhãn** (ví dụ: nhận diện "2n1k"), tự động **trích xuất** các thông tin cốt lõi (giá, diện tích, địa chỉ).
        *   *Alex's Note:* Mục tiêu của AI ở đây không phải là thay thế bạn, mà là trở thành một "trợ lý QC", xử lý 80% các trường hợp dễ, để bạn tập trung vào 20% các trường hợp khó.
    3.  **Cho phép "Chính chủ đã xác thực" Đăng tin:** Mở một "cánh cổng" chất lượng cao để giảm sự phụ thuộc vào scraping.
    4.  **Các Dịch vụ Giá trị Gia tăng:** Hợp đồng mẫu, kiểm tra pháp lý, dịch vụ chụp ảnh chuyên nghiệp...
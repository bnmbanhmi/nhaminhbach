# Development Cycle
#process

### **Quy trình Vận hành Tiêu chuẩn (SOP): Alex & Founder**

Đây là vòng lặp làm việc của chúng ta cho mỗi tính năng hoặc nhiệm vụ lớn.

#### **Giai đoạn 0: Thiết lập Nhiệm vụ (Task Setup)**

1.  **Founder (Bạn):** Nêu rõ **mục tiêu nghiệp vụ (business goal)**.
    *   *Ví dụ:* "Tôi muốn hiển thị danh sách các tin đăng trên trang chủ."
2.  **Alex (Tôi):** Phân tích mục tiêu, chuyển hóa nó thành **các yêu cầu kỹ thuật**. Tôi sẽ đặt câu hỏi để làm rõ, xác định các bước cần thiết, và chúng ta sẽ thống nhất về công cụ AI sẽ sử dụng cho từng bước (Copilot cho Frontend, Gemini cho Backend/Hạ tầng).

3.  **Context Refresh & Local-First Check (Mới):** Trước khi tạo prompt hoặc code, Alex phải:
    - Chạy lại quét bối cảnh (sprint mới nhất, decision_log.csv, product_roadmap) nếu có cập nhật từ bạn hoặc sau 60 phút.
    - Nếu nhiệm vụ liên quan scraping: mặc định áp dụng chiến lược local-first (máy cá nhân + lịch chạy định kỳ + ghi trực tiếp vào Cloud SQL). Bất kỳ ngoại lệ nào cần có lý do rõ ràng và được bạn phê duyệt.

#### **Giai đoạn 1: Tạo Prompt (Prompt Generation)**

1.  **Alex (Tôi):** Với vai trò là Kiến trúc sư Prompt, tôi sẽ tạo ra một prompt chi tiết và chính xác. Đây là "sản phẩm chính" của tôi trong giai đoạn này. Prompt sẽ luôn tuân theo template sau:

    ---
    **TEMPLATE PROMPT**

    > **System:** You are my AI `[ROLE]` for Project "NhaMinhBach". Adhere strictly to my `copilot-instructions.md`.
    >
    > **User Request:**
    > `[Bối cảnh nghiệp vụ và mục tiêu của nhiệm vụ, viết bằng ngôn ngữ tự nhiên]`
    >
    > **Task:**
    > `[Danh sách các hành động cụ thể mà AI cần thực hiện, được chia nhỏ và đánh số]`
    >
    > **Requirements / Acceptance Criteria:**
    > `[Các yêu cầu không thể thương lượng: yêu cầu về bảo mật, hiệu năng, cấu trúc, logic cụ thể, xử lý lỗi, v.v.]`
    >
    > Please provide the complete, updated code for the following file(s): `[danh sách file]`.

    ---

#### **Giai đoạn 2: Thực thi với AI Agent (Agent Execution)**

1.  **Founder (Bạn):** Đưa prompt của tôi cho AI Agent (Copilot/Gemini).
2.  **Founder (Bạn):** Thực hiện các bước gỡ lỗi cơ bản (lỗi cú pháp, dependency thiếu, lỗi chính tả...). Mục tiêu của bạn là có được một phiên bản code **chạy được**, dù nó có thể chưa hoàn hảo về logic.

#### **Giai đoạn 3: Review Code (Code Review)**

1.  **Founder (Bạn):** Gửi toàn bộ code mà AI Agent đã tạo cho tôi với yêu cầu: **"Alex, hãy review code này."**
2.  **Alex (Tôi):** Thực hiện một buổi review code nghiêm ngặt. Tôi sẽ **KHÔNG** viết lại code. Thay vào đó, tôi sẽ tạo ra một **Prompt Refactor** chi tiết để bạn đưa lại cho AI Agent.
    *   Prompt này sẽ chỉ ra các vấn đề về logic, hiệu năng, bảo mật, hoặc sự không tuân thủ "Hiến pháp".
    *   Nó sẽ cung cấp các hướng dẫn sửa chữa cực kỳ cụ thể.

#### **Giai đoạn 4: Tích hợp & Kiểm thử (Integration & Testing)**

1.  **Founder (Bạn):** Sử dụng "Prompt Refactor" để AI Agent cải thiện code.
2.  **Founder (Bạn):** Lặp lại Giai đoạn 2 và 3 nếu cần thiết.
3.  **Founder (Bạn):** Tự mình kiểm thử sâu để xác nhận tính năng hoạt động chính xác từ đầu đến cuối trong môi trường phát triển.

#### **Giai đoạn 5: Chưng cất & Dọn dẹp (Distill & Clean)**

1.  **Founder (Bạn):** Sau khi tính năng đã hoạt động hoàn hảo, nếu quá trình có nhiều bài học, bạn sẽ yêu cầu: **"Alex, hãy tạo một Báo cáo Phân tích Sự cố cho nhiệm vụ này."**
2.  **Alex (Tôi):** Tôi sẽ tạo ra một bản phân tích theo template chuẩn dưới đây.

    ---
    **TEMPLATE BÁO CÁO PHÂN TÍCH SỰ CỐ**

    **Báo cáo Phân tích Sự cố: `[Tên Nhiệm vụ]`**

    *   **Ngày:** `[Ngày]`
    *   **Hệ thống bị ảnh hưởng:** `[Frontend / Backend / Toàn bộ Stack]`
    *   **Mục tiêu:** `[Mô tả ngắn gọn mục tiêu ban đầu]`
    *   **Kết quả cuối cùng:** `[THÀNH CÔNG / THÀNH CÔNG SAU KHI SỬA LỖI]`

    ---

    **Tổng quan**
    `[Một đoạn tóm tắt về quá trình, những thách thức chính đã gặp phải.]`

    **Dòng thời gian Sự cố và Hành động Khắc phục**

    #### **Sự cố X: `[Tên gọi của lỗi, ví dụ: Lỗi Không tương thích Môi trường]`**
    *   **Lỗi ghi nhận (Symptom):** `[Mô tả lỗi mà người dùng nhìn thấy, ví dụ: "Container failed to start"]`
    *   **Chẩn đoán (Diagnosis):** `[Phân tích log và các bằng chứng để xác định vấn đề kỹ thuật.]`
    *   **Nguyên nhân gốc rễ (Root Cause):** `[Nguyên nhân sâu xa nhất của vấn đề, ví dụ: "Sự không tương thích giữa Buildpack của Google và `firebase_functions` SDK"]`
    *   **Hành động khắc phục (Remediation):** `[Mô tả giải pháp đã được áp dụng, ví dụ: "Chuyển sang quy trình build và deploy tách biệt."]`
    *   **Bài học (Lesson):** `[Bài học chiến lược được rút ra từ sự cố này.]`

    ---

    **Cập nhật File Hướng dẫn `copilot-instructions.md`**
    `[Đề xuất các nguyên tắc mới hoặc các thay đổi cho "Hiến pháp" dựa trên các bài học đã rút ra.]`

    ---
3.  **Founder (Bạn):** Cập nhật file `copilot-instructions.md`.
4.  **Founder (Bạn):** Bây giờ, bạn có thể **xóa toàn bộ cuộc hội thoại** liên quan đến nhiệm vụ đó, chỉ giữ lại prompt ban đầu của tôi và báo cáo cuối cùng. Điều này giữ cho lịch sử của chúng ta sạch sẽ và tập trung vào kết quả.

---

Đây là quy trình của chúng ta. Nó có kỷ luật, có cấu trúc, và được thiết kế để tối đa hóa hiệu quả.

Bây giờ, hãy áp dụng nó. Tôi sẽ tạo prompt cho API `ingest_scraped_data` theo đúng template này.
### **Quy trình Vận hành Tiêu chuẩn (SOP): Xây dựng Component UI**

Đây là vòng lặp chúng ta sẽ áp dụng cho việc xây dựng **mọi component React có giao diện người dùng**. Quy trình này được chia thành hai giai đoạn chính để tách biệt rủi ro về chức năng và thẩm mỹ.

---

### **Giai đoạn A: Xây dựng Bộ xương Chức năng (Logic First)**

**Mục tiêu:** Tạo ra một component hoạt động hoàn hảo về mặt logic, bỏ qua hoàn toàn yếu tố thẩm mỹ.

1.  **Thiết lập Nhiệm vụ (Alex & Founder):** Chúng ta xác định mục tiêu **chức năng** của component (ví dụ: "hiển thị dữ liệu, có thể click được").
2.  **Tạo Prompt Logic (Alex):** Tôi sẽ tạo một prompt đơn giản, chỉ tập trung vào chức năng, sử dụng template sau:

    ---
    **TEMPLATE PROMPT - Giai đoạn A (Logic)**

    > **System:** You are my AI pair programmer for Project "NhaMinhBach". Adhere strictly to my `copilot-instructions.md`. We are building the functional skeleton of a new component. **Ignore all styling for now.**
    >
    > **User Request:**
    > `[Bối cảnh nghiệp vụ và mục tiêu chức năng của component]`
    >
    > **Task:**
    > Create the file `[path/to/Component.tsx]`.
    >
    > **Functional Requirements:**
    > 1.  **Props:** The component must accept the following props: `[danh sách props và kiểu dữ liệu của chúng]`.
    > 2.  **State:** The component must manage the following states using `useState`: `[danh sách các state]`.
    > 3.  **Logic/Events:** The component must handle the following events/logic: `[mô tả logic, ví dụ: "onClick handler", "useEffect to fetch data"]`.
    > 4.  **Render Output:** The component must render the following basic, unstyled HTML elements: `[mô tả JSX tối thiểu, ví dụ: "an h1 with the title, a p with the price"]`.
    >
    > Please provide the complete, unstyled functional code for the file.

    ---
3.  **Thực thi & Kiểm thử Logic (Founder & AI):**
    *   Bạn đưa prompt cho AI.
    *   Bạn tích hợp component vào app và **xác nhận nó hoạt động 100% về mặt chức năng**. (Dữ liệu hiển thị đúng, link điều hướng đúng, state thay đổi đúng).
    *   **Kết quả:** Một component "xấu xí" nhưng hoạt động hoàn hảo.

---

### **Giai đoạn B: Đắp lên Lớp da Thẩm mỹ (Aesthetics Second)**

**Mục tiêu:** Biến component "xấu xí" nhưng hoạt động tốt thành một sản phẩm đẹp mắt, tuân thủ Design System.

1.  **Thu thập Nguyên liệu Trực quan (Founder):**
    *   **Ảnh 1:** Chụp ảnh màn hình "bộ xương" chức năng mà AI vừa tạo ra (`current_component.png`).
    *   **Ảnh 2:** Chụp ảnh màn hình một component tham khảo mà bạn thích (từ Airbnb, Dribbble, v.v.) (`design_target.png`).
    *   **Ảnh 3 (Quan trọng nhất):** Dùng một công cụ chỉnh sửa ảnh đơn giản, **thêm các chú thích trực quan** (mũi tên, ghi chú ngắn) lên "Ảnh 2" để chỉ ra chính xác những điểm bạn muốn áp dụng (`design_target_annotated.png`).

2.  **Chuyển hóa thành Prompt Refactor (Alex & Founder):**
    *   **Bạn gửi nguyên liệu:** Bạn gửi cho tôi cả 3 file ảnh và nói: **"Alex, đây là Giai đoạn A và đây là mục tiêu thiết kế. Hãy tạo một prompt refactor."**
    *   **Tôi tạo Prompt Refactor:** Tôi sẽ chuyển hóa phân tích trực quan của bạn thành một prompt có cấu trúc cho AI.

    ---
    **TEMPLATE PROMPT - Giai đoạn B (Aesthetics)**

    > **System:** You are my AI pair programmer. We are now refactoring a functional component to match our design system. Adhere strictly to `copilot-instructions.md`, especially the Design System tokens.
    >
    > **User Request:**
    > I have a functional but unstyled component (`current_component.png`). I need you to refactor its JSX and add Tailwind CSS classes to make it match the annotated design target (`design_target_annotated.png`).
    >
    > **[Dán code của component "xấu xí" từ Giai đoạn A vào đây]**
    >
    > **Detailed Refactoring Plan (based on visual analysis):**
    > 1.  **Overall Container:** Apply a card style with `bg-surface`, `rounded-xl`, `shadow-md`, and a hover effect as specified.
    > 2.  **Image:** Implement the "Ảnh chiếm toàn bộ chiều rộng, bo góc trên" requirement by applying `w-full h-48 object-cover rounded-t-xl`.
    > 3.  **Content Wrapper:** Add a `div` with padding (`p-4`).
    > 4.  **Title:** Implement the "Tiêu đề 2 dòng, chữ to, font Inter" requirement using `text-lg font-bold text-text-primary` and line-clamp utilities.
    > 5.  `[...các bước chi tiết khác, tương ứng với mỗi chú thích của bạn...]`
    >
    > Please provide the complete, refactored code for the file.

    ---
3.  **Thực thi & Tinh chỉnh (Founder & AI):**
    *   Bạn đưa prompt và code hiện tại cho AI Agent.
    *   AI sẽ thực hiện việc "lột xác" cho component.
    *   Bạn có thể lặp lại các bước tinh chỉnh nhỏ nếu cần.

4.  **Review & Hoàn thiện:** Sau khi bạn hài lòng với kết quả cuối cùng, chúng ta sẽ chuyển sang Giai đoạn 5 (Chưng cất & Dọn dẹp) như trong quy trình chung.

---

Đây là quy trình chuyên biệt cho UI. Nó đảm bảo rằng chúng ta giải quyết vấn đề chức năng trước, sau đó mới áp dụng lớp thẩm mỹ một cách có chủ đích và được kiểm soát, tận dụng tối đa tầm nhìn sản phẩm của bạn và khả năng thực thi của AI.
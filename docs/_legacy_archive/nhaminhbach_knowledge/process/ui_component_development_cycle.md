# UI Component Development

tag: #process 

### **Quy trình Vận hành Tiêu chuẩn (SOP): Xây dựng Component UI**

Đây là vòng lặp chúng ta sẽ áp dụng cho việc xây dựng **mọi component React có giao diện người dùng**. Quy trình này được chia thành hai giai đoạn chính để tách biệt rủi ro về chức năng và thẩm mỹ. CTO Alex sẽ thực hiện trực tiếp cả hai giai đoạn.

---

### **Giai đoạn A: Xây dựng Bộ xương Chức năng (Logic First)**

**Mục tiêu:** Tạo ra một component hoạt động hoàn hảo về mặt logic, bỏ qua hoàn toàn yếu tố thẩm mỹ.

1.  **Thiết lập Nhiệm vụ (Alex & Founder):** Chúng ta xác định mục tiêu **chức năng** của component (ví dụ: "hiển thị dữ liệu, có thể click được").
2.  **Thực hiện Logic trực tiếp (Alex):** Alex sẽ tạo component focusing chỉ vào chức năng, tuân theo các yêu cầu:

    
    **Functional Requirements:**
    - **Props:** Component accepts required props with proper TypeScript definitions
    - **State:** Component manages state using `useState` where needed
    - **Logic/Events:** Component handles required events and business logic
    - **Render Output:** Component renders basic, unstyled HTML elements focusing only on structure

3.  **Kiểm thử Logic (Founder & Alex):**
    *   Alex integrates component into app
    *   Founder **xác nhận nó hoạt động 100% về mặt chức năng** (Dữ liệu hiển thị đúng, link điều hướng đúng, state thay đổi đúng)
    *   **Kết quả:** Một component "xấu xí" nhưng hoạt động hoàn hảo

---

### **Giai đoạn B: Đắp lên Lớp da Thẩm mỹ (Aesthetics Second)**

**Mục tiêu:** Biến component "xấu xí" nhưng hoạt động tốt thành một sản phẩm đẹp mắt, tuân thủ Design System.

1.  **Thu thập Nguyên liệu Trực quan (Founder):**
    *   **Ảnh 1:** Chụp ảnh màn hình "bộ xương" chức năng hiện tại (`current_component.png`)
    *   **Ảnh 2:** Chụp ảnh màn hình component tham khảo từ Airbnb, Dribbble, etc. (`design_target.png`)  
    *   **Ảnh 3:** Thêm chú thích trực quan (mũi tên, ghi chú) lên Ảnh 2 để chỉ ra điểm cần áp dụng (`design_target_annotated.png`)

2.  **Phân tích & Thực hiện Refactor (Alex):**
    *   Founder gửi 3 file ảnh với feedback: "Alex, đây là hiện tại và đây là mục tiêu thiết kế. Hãy refactor."
    *   Alex phân tích visual feedback và thực hiện refactor trực tiếp:
        - Apply design system tokens (colors, spacing, typography)
        - Implement responsive layout patterns  
        - Add hover states and interaction feedback
        - Ensure accessibility compliance

3.  **Iterative Refinement (Founder & Alex):**
    *   Alex implements the aesthetic improvements
    *   Founder provides real-time feedback on the visual result
    *   Alex makes incremental adjustments until Founder is satisfied
    *   Focus on design system compliance and responsive behavior

4.  **Final Review & Integration:** 
    *   Confirm component meets both functional and aesthetic requirements
    *   Verify responsive design across devices
    *   Ensure accessibility standards are met
    *   Integration into larger application context

---

**Key Advantages of Direct Collaboration:**
- **Real-time feedback:** Immediate iteration based on visual results
- **Context preservation:** Alex maintains full technical context throughout both phases  
- **Faster iteration:** No prompt generation overhead, direct implementation
- **Quality control:** CTO Alex ensures engineering principles compliance at every step
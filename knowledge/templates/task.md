---
tags: tasks
status: #status/done
id: 20250814
owner: Minh
epic: [[epic]]
sprint: [[sprint]]
---

# Task: #templates

### 1. Goal & Acceptance Criteria
-   **Goal:** _Xây dựng một hệ thống có thể tự động thu thập tin đăng từ 10 group Facebook và lưu vào database._
-   **AC 1:** _Script chạy thành công không lỗi._
-   **AC 2:** _Dữ liệu được lưu vào Cloud SQL đúng schema._

### 2. Decision Chronicle & Work Log
_Đây là nơi toàn bộ quá trình diễn ra: các cuộc trò chuyện, tóm tắt, quyết định..._

#### **2.1. Initial Brainstorming (with CTO Alex)**
> **USER:** Activate: CTO Alex. Let's design the scraping pipeline.
> **MODEL (CTO Alex):** Acknowledged. CTO Alex is now active... I see two main options: 1. A complex, scalable system with Cloud Run, or 2. A simple, local script...

#### **2.2. Key Decision**
_Sau khi thảo luận, chúng tôi quyết định theo hướng #2 để tối ưu hóa tốc độ theo nguyên tắc [[PR-04_YAGNI_Principle]]._

#### **2.3. Implementation Log**
...

### 3. Final Retrospective (Chưng cất tri thức)
-   **Trigger:** Cần xây dựng pipeline scraping.
-   **Final Outcome:** Hoàn thành script chạy local.
-   **The "Aha!" Moment:** Nhận ra việc xây hệ thống scale-up ngay từ đầu là một cái bẫy.
-   **Core Principle Learned:** Củng cố thêm niềm tin vào [[PR-04_YAGNI_Principle]].
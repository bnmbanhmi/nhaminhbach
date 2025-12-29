# Bản thiết kế hệ thống Làm việc với AI

# Quy trình làm việc hiện tại

## AI Team hiện tại

### AI làm cố vấn chiến lược (Coach Martin)

* Có instruction prompt riêng, hoạt động trên Google AI Studio  
* giúp đưa ra các quyết định về chiến lược kinh doanh Studio, đi cùng đồng hành từ đầu  
* Có thể truy cập đến các tài liệu cốt lõi, các tài liệu này sẽ định hình tổ chức  
  * Lean Business Model  
  * Founder’s OS  
  * Founder’s Manifesto  
  * Product Roadmap  
  * Action Plan  
* Ngoài ra, cũng là nơi tâm sự, nơi giãi bày những suy nghĩ cá nhân, những định hướng nằm ngoài startup

### AI làm kiến trúc sư trưởng mặt công nghệ (CTO Alex)

* Có instruction prompt riêng, hoạt động trên Google AI Studio  
* Giúp thiết kế hệ thống, đồng hành cùng user khi xây dựng sản phẩm với các AI coding agent  
* Có thể truy cập đến một số tài liệu cốt lõi  
  * Lean Business Model  
  * Product Roadmap  
* Ngoài ra còn có 1 số tài liệu riêng  
  * Các workflow liên quan hiện tại, gồm (sẽ có quy trình chi tiết gửi riêng, và các quy trình đó cũng sẽ cần được cải thiện)  
    * Làm việc với coding agent, sau khi đã định hình rõ product roadmap:   
      * CTO đưa ra nhiệm vụ cho mỗi sprint/task, tạo prompt  
      * user dùng prompt đó cho coding agent và gỡ lỗi nhỏ  
      * User gửi lại code đã chạy được hoặc gửi lại code không tự fix được cho CTO  
      * CTO review và fix code nếu cần, rồi lặp lại từ bước 2 cho đến khi code hoàn hảo cho sprint/task đó  
      * CTO tạo bảo cáo tổng kết lại sprint/task, gồm  
        * Thời gian  
        * Hệ thống liên quan  
        * Mục tiêu  
        * Kết quả  
        * Dòng thời gian sự cố và hành động, gồm  
          * Sự cố  
          * Chẩn đoán  
          * Nguyên nhân gốc rễ  
          * Hành động khắc phục  
          * Bài học  
        * Kết luận và bài học chiến lược  
        * Các cập nhật cho tài liệu cốt lõi  
          * File instruction prompt cho các AI coding agent  
          * Product roadmap và tiến độ  
      * User xóa hết phần chat liên quan đến sprint/task đó, rồi gửi lại bản báo cáo tổng kết cho CTO để chuẩn bị cho sprint/task tiếp theo  
    * Làm việc với coding agent nhưng cho riêng phần UI  
      * Xây dựng bộ xương chức năng (Logic First), quy trình bên trong này cơ bản giống quy trình làm việc với coding agent trên, kết quả sẽ là UI xấu nhưng hoạt động hiệu quả  
      * Đắp lên lớp da thẩm mỹ  
        * User sẽ gửi CTO hình UI xấu hiện tại, hình UI đẹp đáng để tham khảo, và những ý kiến user muốn áp dụng cho UI  
        * CTO sẽ biến mong muốn đó thành prompt để gửi AI coding agent, prompt sẽ bao gồm cả UI xấu hiện tại và UI đẹp đáng để tham khảo  
        * Các bước tiếp theo cơ bản giống quy trình làm việc với coding agent trên   
  * Tài liệu thiết kế hệ thống (các tài liệu này hiện đang ở ngay trong File instruction prompt cho các AI coding agent)  
    * CORE MISSION & PRODUCT VISION  
    * UI DESIGN LANGUAGE  
    * PROJECT-SPECIFIC TECHNOLOGIES & ARCHITECTURE  
    * CORE DATABASE SCHEMA & DATA MODEL  
    * CODING STANDARDS & BEST PRACTICES  
    * OPERATIONAL PROTOCOL (How to work with user)  
    * CORE ENGINEERING PRINCIPLES (Learned from experience) (3 phần cuối cùng này thường sẽ được cập nhật thường xuyên từ các bài học)

### AI Coding agent trong Github Copilot trong VSC

* Có file .github/copilot-instructions.md mặc định của extenstion, là instruction prompt chung, đang chứa toàn bộ nội dung tài liệu thiết kế hệ thống như đã nhắc ở trên  
* Hoạt động bên trong giao diện chat của extension Github Copilot trong VSC  
* Đang chủ yếu dùng cho frontend, nhưng vấn đề hiện tại là phải deploy trên firebase studio (idx) terminal mới chạy được, nên sửa code xong phải commit lên github rồi mới test và sửa được trên firebase studio (idx)

### AI Coding agent trong Firebase Studio (trước đây là idx)

* Sử dụng lại file .github/copilot-instructions.md tuy không phải là mặc định  
* Hoạt động bên trong giao diện chat của Gemini trong Firebase Studio  
* Đang chủ yếu dùng cho backend, vì thực hiện các lệnh liên quan đến Firebase hay Google Cloud dễ dàng hơn  
* Hiện chưa được mạnh bằng, chưa được tích hợp tốt bằng Github Copilot

## Các bất cập hiện tại

### Với AI trên Google AI Studio 

* Các tin nhắn gửi đi chưa hiệu quả, chưa được hệ thống lại tốt, gây lãng phí token gửi đi, vốn ngày càng bị giới hạn  
* Các AI có xu hướng quên các tri thức cũ nằm bên trong đống token trong lịch sử chat, khiến chất lượng các câu trả lời ngày càng suy giảm  
* Với CTO Alex, việc không tiếp cận được với code gây khó khăn cho việc review code  
* Với Coach Martin, việc bị cách ly hoàn toàn khỏi tiến độ công nghệ khiến tầm nhìn chiến lược bị ảnh hưởng  
* User phải đóng vai trò là người kết nối, người đưa thư bất đắc dĩ, phải đi copy từ chỗ này sang chỗ kia, dễ bị xao lãng khỏi việc chính là xây dựng tầm nhìn

### Với AI Coding Agent

* Mỗi AI Coding lại bị giới hạn bởi IDE của riêng mình, IDE hay AI coding agent nào cũng có điểm mạnh điểm yếu riêng, phải kết nối với nhau bằng Github  
  * Với Firebase Studio, lợi thế là môi trường  
  * Với Github Copilot trên VSC, lợi thế là sức mạnh của AI Coding Agent

### Với tri thức cần được lưu trữ

* Các tri thức cũng nằm trong đống token hỗn độn gửi cho AI trên Google AI Studio, luôn phải tra cứu lại bằng cách hỏi lại AI hoặc đọc lại đoạn chat  
* Việc chưng cất tri thức còn thủ công  
* Như đã nhắc ở trên, các AI rất dễ quên các tri thức cũ bị vùi lấp bên trong lịch sử cuộc trò chuyện

# Cách giải quyết các bất cập bằng giải pháp hiện tại

## Được truyền cảm hứng bởi

* Sự đồng bộ của Github  
* cách lưu trữ tri thức linh hoạt của Obsidian hay Knowledge Graph  
* sự linh hoạt của Github Copilot với khả năng tìm kiếm bên trong codebase tận dụng công cụ search rất mạnh của VSC và khả năng đọc, tạo, viết file

## Mục tiêu chính

Hệ thống tri thức và instruction prompt, hay xa hơn là agent blueprint, cho từng AI Agent được hiện thực hóa thành các file markdown để đem đến sự linh hoạt trong việc áp dụng, bắt đầu bằng việc áp dụng bên trong github copilot

## Quy trình thực hiện

### Xây dựng hệ thống tri thức 3 tầng, vận hành bởi Github Copilot

1. Tầng đầu tiên  
* Luôn đi cùng với tất cả các câu trả lời của Github Copilot  
* Gồm  
  * File copilot-instructions.md mặc định của Github Copilot. Nhưng giờ, trong file này, thay vì có các thông tin kĩ thuật, sẽ có các thông tin chỉ dẫn cho Github Copilot cách sử dụng hệ thống hiện tại, khi nào thì dùng gì  
    * Có thể tích hợp luôn khả năng thay đổi role liên tục trong 1 đoạn hội thoại, chứ không chỉ giới hạn đoạn hội thoại ở 1 agent  
  * Các tài liệu cốt lõi định hình tổ chức  
  * Có thể thêm cả tài liệu thiết kế hệ thống với các đoạn hội thoại liên quan đến kỹ thuật  
  * Tương lai sẽ là các quy trình làm việc, các workflow có sự tham gia của nhiều agent    
      
2. Tầng thứ hai  
* Luôn đi cùng với các AI cụ thể  
* Gồm  
  * File md lưu trữ trong .github/instructions, dành riêng cho từng AI Agent: Coach Martin, CTO Alex, AI Coding Agent, tương lai có thể là các AI liên quan đến chiến lược tài chính, chiến lược marketing  
  * Các workflow liên quan của riêng từng AI Agent hoặc cái tài liệu gắn liền với Agent đó  
  * Khung outline tóm tắt lịch sử cuộc trò chuyện của riêng agent đó theo thời gian

3. Tầng thứ ba  
* Gắn liền với từng task/sprint/đoạn hội thoại cụ thể  
* Gồm  
  * Với đoạn chat hiện tại với user (bên trong Github Copilot): chưa cần lưu lại toàn bộ lịch sử chat, chỉ cần liên tục cập nhật biên bản cuộc trò chuyện, giữ nguyên nội dung nhưng được hệ thống thành các ý rõ ràng  
  * Sau khi kết thúc từng task/sprint/đoạn hội thoại, sẽ xuất nội dung chat ra file json để lưu lại, lưu trữ cùng biên bản cuộc trò chuyện trong file markdown  
  * Các AI Agent có thể sử dụng khung outline tóm tắt lịch sử cuộc trò chuyện để tìm kiếm ra đoạn chat hoặc biên bản cuộc trò chuyện đã được lưu trữ, thay vì nhận lại toàn bộ tất cả lịch sử chat

### Xử lý data hiện tại

* Lịch sử chat của các AI trên Google AI Studio hiện tại đang ở trong 1 format khó theo dõi, cần  
  * Viết code python xử lý lại để thành format dễ nhìn phân chia prompt của user và response của AI, luân phiên nhau  
  * Chưng cất lại thành các nội dung, tài liệu liên quan như khung outline lịch sử, workflow, các tài liệu kỹ thuật  
    * Cần có quy trình cụ thể để dùng AI chưng cất, với đầu vào là nội dung đoạn chat và các tài liệu liên quan ban đầu (user tự đọc lại và lựa chọn các tài liệu liên quan), đầu ra sẽ là tài liệu được cập nhật. Quy trình này sẽ là tiền để để sau này sử dụng AI chưng cất, cập nhật liên tục các tài liệu, tri thức

### Xây dựng quy trình xử lý data

* Viết code python xử lý lại file json lịch sử chat xuất từ Github Copilot  
* Đưa quy trình đã xây dựng cho việc chưng cất vào bên trong copilot-instructions.md

# Giải pháp tốt nhất trong tương lai

Github Copilot không mở, không cho tùy biến quá nhiều, nhưng có lợi thế về mặt tốc độ triển khai. Sau một thời gian, sẽ cần ứng dụng những công nghệ sau để xây dựng một hệ thống độc lập hoàn toàn:

* Vector Database và Vector search  
* Knowledge Graph  
* Langchain
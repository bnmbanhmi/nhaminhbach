### **The NhaMinhBach Data Factory Blueprint - V1**

**Mục tiêu:** Xây dựng một hệ thống tự động, có khả năng mở rộng trên Google Cloud Platform (GCP) để thu thập, xử lý và hiển thị dữ liệu phòng trọ từ các nguồn công khai.

**Kiến trúc Tổng thể:**

  
*(Alex's Note: Chúng ta sẽ tạo ra một sơ đồ kiến trúc thực sự sau này. Bây giờ hãy tập trung vào các bước.)*

**Yêu cầu Tiên quyết:**
1.  Một tài khoản Google Cloud với quyền Owner.
2.  Đã cài đặt `gcloud` CLI trên máy tính và đã đăng nhập (`gcloud auth login`).
3.  Một repository GitHub cho dự án.
4.  Đã cài đặt Docker trên máy tính.

---

### **Giai đoạn 1: Thiết lập Nền tảng (The Foundation)**

**Mục tiêu:** Chuẩn bị tất cả các dịch vụ GCP cần thiết, bao gồm database, kho chứa code, và các quyền hạn cơ bản.

#### **Phần 1.1: Kích hoạt các API cần thiết**

Mọi dịch vụ trên GCP đều cần được kích hoạt trước khi sử dụng.
*   **Hành động:** Mở Cloud Shell (hoặc terminal của bạn) và chạy lệnh sau. Lệnh này sẽ kích hoạt tất cả các API chúng ta sẽ cần cho toàn bộ dự án.

```bash
gcloud services enable \
  sqladmin.googleapis.com \
  iam.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  pubsub.googleapis.com \
  secretmanager.googleapis.com \
  cloudfunctions.googleapis.com \
  --project=<YOUR_PROJECT_ID>
```
*   **Thay thế:** `<YOUR_PROJECT_ID>` bằng Project ID thực tế của bạn (ví dụ: `omega-sorter-467514-q6`).

#### **Phần 1.2: Tạo Cơ sở dữ liệu (Cloud SQL)**

Đây sẽ là "kho thành phẩm" chứa tất cả dữ liệu sạch của chúng ta.
1.  **Tạo Instance:** Chạy lệnh sau để tạo một instance PostgreSQL. Quá trình này sẽ mất vài phút.

    ```bash
    gcloud sql instances create nhaminhbach-db-prod \
      --database-version=POSTGRES_14 \
      --region=asia-southeast1 \
      --cpu=1 \
      --memory=3840MB \
      --project=<YOUR_PROJECT_ID>
    ```
    *   *Alex's Note:* `--cpu=1 --memory=3840MB` là một cấu hình tốt để bắt đầu. Bạn có thể hạ cấp xuống "shared-core" sau này để tiết kiệm chi phí.

2.  **Thiết lập Mật khẩu cho User `postgres`:**
    ```bash
    gcloud sql users set-password postgres \
      --instance=nhaminhbach-db-prod \
      --password="<YOUR_STRONG_PASSWORD>" \
      --project=<YOUR_PROJECT_ID>
    ```
    *   **Hành động:** Thay `<YOUR_STRONG_PASSWORD>` bằng một mật khẩu mạnh và **lưu nó vào một trình quản lý mật khẩu an toàn.**

3.  **Kích hoạt Kết nối IP Public:** Mặc dù không phải là lựa chọn an toàn nhất cho production dài hạn, việc sử dụng IP Public với các biện pháp bảo vệ khác là cách thực dụng và dễ gỡ lỗi nhất cho MVP.
    ```bash
    gcloud sql instances patch nhaminhbach-db-prod \
      --assign-ip \
      --project=<YOUR_PROJECT_ID>
    ```

4.  **Tạo Schema và Bảng:**
    *   **Hành động:** Chuẩn bị các file `.sql` chứa các lệnh `CREATE TABLE` cho `listings`, `attributes`, `listing_attributes`, và `groups`.
    *   Kết nối đến instance bằng Cloud Shell hoặc một client SQL bất kỳ và chạy các file script đó để tạo cấu trúc cho database.
    *   *Alex's Note: Đây là một bước thủ công nhưng cực kỳ quan trọng. Không có bảng, không có gì hoạt động cả.*

#### **Phần 1.3: Tạo Kho chứa Container (Artifact Registry)**

Đây là nơi chúng ta sẽ lưu trữ các Docker image đã được build.
```bash
gcloud artifacts repositories create nhaminhbach-repo \
  --repository-format=docker \
  --location=asia-southeast1 \
  --description="Docker repository for NhaMinhBach project" \
  --project=<YOUR_PROJECT_ID>
```

#### **Phần 1.4: Lưu trữ các Bí mật (Secret Manager)**

Chúng ta sẽ không bao giờ lưu mật khẩu trong code.
1.  **Lưu Mật khẩu Database:**
    ```bash
    # Tạo secret
    gcloud secrets create db-password --replication-policy="automatic" --project=<YOUR_PROJECT_ID>

    # Thêm phiên bản đầu tiên của secret với giá trị là mật khẩu của bạn
    printf "<YOUR_STRONG_PASSWORD>" | gcloud secrets versions add db-password --data-file=- --project=<YOUR_PROJECT_ID>
    ```
    *   **Hành động:** Thay `<YOUR_STRONG_PASSWORD>` bằng mật khẩu bạn đã tạo ở Phần 1.2.

2.  **Tạo một Secret Key cho "Nhạc trưởng":** (Chúng ta đã loại bỏ nó khỏi code, nhưng việc tạo ra nó là một thực hành tốt).
    ```bash
    # Tạo một chuỗi ngẫu nhiên an toàn
    ORCHESTRATOR_KEY=$(openssl rand -base64 32)

    # Tạo secret
    gcloud secrets create orchestrator-secret-key --replication-policy="automatic" --project=<YOUR_PROJECT_ID>

    # Thêm phiên bản đầu tiên của secret
    printf "$ORCHESTRATOR_KEY" | gcloud secrets versions add orchestrator-secret-key --data-file=- --project=<YOUR_PROJECT_ID>
    ```

#### **Phần 1.5: Cấp Quyền Ban đầu cho các Service Account**

Chúng ta sẽ cấp tất cả các quyền cần thiết cho Service Account mặc định ngay từ đầu.

1.  **Tìm Project Number và Service Account Email:**
    ```bash
    PROJECT_NUMBER=$(gcloud projects describe <YOUR_PROJECT_ID> --format='value(projectNumber)')
    SERVICE_ACCOUNT_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
    ```

2.  **Cấp quyền cho Service Account:** Chạy các lệnh sau để cấp cho Service Account mặc định (sẽ được sử dụng bởi Cloud Scheduler, Functions, và Run) tất cả các vai trò nó cần.
    ```bash
    # Quyền để build và lưu trữ image
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
      --role="roles/storage.admin"
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
      --role="roles/artifactregistry.writer"

    # Quyền để chạy các dịch vụ và job
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
      --role="roles/run.invoker"

    # Quyền để gọi các Cloud Function được bảo vệ
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
      --role="roles/cloudfunctions.invoker"

    # Quyền để đọc các secret
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
      --role="roles/secretmanager.secretAccessor"

    # Quyền để publish tin nhắn Pub/Sub
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
      --role="roles/pubsub.publisher"
    ```
    *   *Alex's Note: Bằng cách cấp tất cả các quyền này cho một Service Account duy nhất ngay từ đầu, chúng ta loại bỏ hoàn toàn các lỗi về quyền hạn sau này.*

Các dịch vụ của Google cần quyền để tương tác với nhau.
1.  **Tìm Project Number của bạn:**
    ```bash
    gcloud projects describe <YOUR_PROJECT_ID> --format='value(projectNumber)'
    ```
    *   Copy lại con số này.

2.  **Cấp quyền cho Cloud Build:**
    *   **`Logs Writer`:** Để ghi log.
    *   **`Service Account User`:** Để hoạt động với tư cách của các service account khác.
    *   **`Secret Manager Secret Accessor`:** Để truy cập các secret trong quá trình build (nếu cần).

    ```bash
    PROJECT_NUMBER=$(gcloud projects describe <YOUR_PROJECT_ID> --format='value(projectNumber)')

    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
      --role="roles/logging.logWriter"

    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
      --role="roles/iam.serviceAccountUser"
      
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
      --role="roles/secretmanager.secretAccessor"
    ```

---
**Kết thúc Giai đoạn 1**

Sau khi hoàn thành các bước trên, bạn đã có một nền tảng vững chắc:
*   Một database sẵn sàng nhận dữ liệu.
*   Một nơi an toàn để lưu trữ Docker image.
*   Một nơi bảo mật để lưu trữ các thông tin nhạy cảm.
*   Hệ thống build đã được cấp các quyền hạn cơ bản.

Được rồi, chúng ta tiếp tục xây dựng "Nhà máy". Nền tảng đã vững chắc. Bây giờ là lúc chúng ta tạo ra các bộ phận chuyển động.

---

### **Giai đoạn 2: Tạo "Công nhân" (The Scraper Worker)**

**Mục tiêu:** Xây dựng một Docker container có thể thực thi script scraper của chúng ta, và thiết lập một quy trình CI/CD để tự động build và lưu trữ nó.

#### **Phần 2.1: Chuẩn bị Cấu trúc Dự án**

1.  **Cấu trúc Thư mục:** Đảm bảo dự án của bạn có cấu trúc thư mục tối thiểu như sau:
    ```
    nhaminhbach/
    ├── Dockerfile             <-- File này sẽ ở thư mục gốc
    ├── packages/
    │   ├── scraper/
    │   │   ├── main.py
    │   │   └── requirements.txt
    │   └── ... (các package khác)
    └── ...
    ```

2.  **Code Scraper (`packages/scraper/main.py`):**
    *   **Hành động:** Đặt phiên bản code scraper đã được gỡ lỗi cuối cùng của bạn vào file này (phiên bản không có Canary Screenshot, nhưng đã có logic lấy ảnh và "Xem thêm").
    *   *Alex's Note: Code này chúng ta đã hoàn thiện ở các bước trước.*

3.  **Dependencies Scraper (`packages/scraper/requirements.txt`):**
    *   **Hành động:** File này phải chứa tất cả các thư viện Python mà `main.py` cần. Tối thiểu phải có:
        ```
        playwright
        google-cloud-storage
        ```

#### **Phần 2.2: Viết "Bản thiết kế Công nhân" (The Scraper `Dockerfile`)**

*   **Hành động:** Tạo một file tên là `Dockerfile` (không có đuôi file) ở **thư mục gốc** của dự án với nội dung chính xác như sau.

```dockerfile
# Giai đoạn 1: Base Image & Dependencies
# Sử dụng một base image Python chính thức và gọn nhẹ.
FROM python:3.11-slim as base

# Đặt thư mục làm việc bên trong container.
WORKDIR /app

# Sao chép file requirements trước để tận dụng Docker layer caching.
COPY packages/scraper/requirements.txt .

# Cài đặt các thư viện Python.
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt trình duyệt Playwright VÀ các dependency hệ thống cần thiết.
# Lệnh --with-deps là cực kỳ quan trọng.
RUN playwright install --with-deps chromium


# Giai đoạn 2: Production Image
# Bắt đầu lại từ một base image sạch để giữ image cuối cùng nhỏ gọn.
FROM python:3.11-slim as final

WORKDIR /app

# Sao chép các dependency hệ thống đã được cài đặt từ giai đoạn 'base'.
# Đây là một kỹ thuật tối ưu hóa.
COPY --from=base /usr/bin/ /usr/bin/
COPY --from=base /lib/ /lib/
COPY --from=base /usr/lib/ /usr/lib/
COPY --from=base /etc/alternatives/ /etc/alternatives/

# Sao chép môi trường Python đã được cài đặt từ giai đoạn 'base'.
COPY --from=base /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=base /usr/local/bin/ /usr/local/bin/

# Sao chép trình duyệt Playwright đã được cài đặt từ giai đoạn 'base'.
COPY --from=base /ms-playwright/ /ms-playwright/

# Bây giờ, chỉ cần sao chép code scraper của chúng ta.
COPY packages/scraper/ .

# Container này không có ENTRYPOINT mặc định.
# Nó là một môi trường thực thi "câm", chờ lệnh từ bên ngoài.
# Điều này tuân thủ "Giao thức Không Ma thuật".
```
*   *Alex's Note:* `Dockerfile` này sử dụng một kỹ thuật gọi là "multi-stage build". Nó giúp image cuối cùng nhỏ hơn đáng kể, tiết kiệm chi phí lưu trữ và tăng tốc độ khởi động của Cloud Run Job.

#### **Phần 2.3: Viết "Bản hướng dẫn Lắp ráp" (The `cloudbuild.yaml` file)**

*   **Hành động:** Tạo một file tên là `cloudbuild.yaml` ở **thư mục gốc** của dự án với nội dung sau.

```yaml
steps:
  # Bước 1: Build image của Scraper
  - name: 'gcr.io/cloud-builders/docker'
    id: 'Build Scraper Image'
    args:
      - 'build'
      - '-t'
      - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/scraper:latest'
      - '-t'
      - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/scraper:$SHORT_SHA'
      - '.' # Build từ Dockerfile ở thư mục gốc
    
  # (Chúng ta sẽ thêm các bước build cho Executor sau)

# Sau khi build thành công, đẩy cả hai tag vào Artifact Registry.
images:
  - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/scraper:latest'
  - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/scraper:$SHORT_SHA'

# Tùy chọn: Ghi log trực tiếp vào Cloud Logging.
options:
  logging: CLOUD_LOGGING_ONLY
```
*   *Alex's Note:* Chúng ta tag image với cả `latest` và `$SHORT_SHA` (mã hash của commit). `latest` tiện cho việc phát triển, trong khi `$SHORT_SHA` là cực kỳ quan trọng cho việc quản lý phiên bản trong môi trường production.

#### **Phần 2.4: Kết nối "Nhà máy" với "Nguồn cung" (Cloud Build Trigger)**

*   **Hành động:** Lặp lại các bước chúng ta đã làm để thiết lập một trigger trong Cloud Build.
    1.  Commit và đẩy 3 file mới (`main.py`, `Dockerfile`, `cloudbuild.yaml`) lên repository GitHub của bạn.
    2.  Vào Google Cloud Console -> **Cloud Build** -> **Triggers**.
    3.  Nhấn **"Connect repository"** và kết nối đến repo GitHub của bạn (nếu chưa làm).
    4.  Nhấn **"Create trigger"**.
    5.  **Name:** `build-main-branch`
    6.  **Event:** `Push to a branch`
    7.  **Branch:** `^main$`
    8.  **Configuration:** `Cloud Build configuration file (yaml or json)`
    9.  **Cloud Build file location:** `/cloudbuild.yaml`
    10. Nhấn **"Create"**.

#### **Phần 2.5: Chạy Build lần đầu**
*   **Hành động:** Để kiểm tra, hãy đẩy một commit nhỏ lên nhánh `main` của bạn, hoặc nhấn nút **"RUN"** trên trigger trong giao diện Cloud Build.
*   **Xác minh:** Sau khi build thành công, hãy vào **Artifact Registry** -> `nhaminhbach-repo`. Bạn sẽ thấy một image mới tên là `scraper` với hai tag: `latest` và một tag hash.

---
**Kết thúc Giai đoạn 2**

Bây giờ bạn đã có:
*   Một "Công nhân" (`scraper` image) được đóng gói chuyên nghiệp, sẵn sàng làm việc.
*   Một dây chuyền CI/CD tự động để mỗi khi bạn cải tiến "Công nhân", một phiên bản mới sẽ được tự động sản xuất và lưu vào kho.

Tuyệt vời. "Công nhân" đã được sản xuất hàng loạt và nằm trong kho. Bây giờ, chúng ta sẽ xây dựng hệ thống quản lý để điều phối và ra lệnh cho chúng.

---

### **Giai đoạn 3: Tạo "Người giám sát" & "Nhạc trưởng" (The Management Layer)**

**Mục tiêu:** Xây dựng và triển khai các Cloud Functions sẽ đóng vai trò là "Nhạc trưởng" (quyết định khi nào cần scrape) và "Người giám sát" (ra lệnh cho từng scraper hoạt động).

#### **Phần 3.1: Chuẩn bị Cấu trúc Dự án**

1.  **Cấu trúc Thư mục:** Đảm bảo dự án của bạn có thư mục `packages/functions`.
    ```
    nhaminhbach/
    ├── Dockerfile             
    ├── cloudbuild.yaml
    ├── packages/
    │   ├── scraper/
    │   │   ├── ...
    │   ├── functions/
    │   │   ├── Dockerfile         <-- Dockerfile mới, chỉ cho Functions
    │   │   ├── main.py            <-- File này sẽ chứa Orchestrator
    │   │   ├── executor.py        <-- File này sẽ chứa Executor
    │   │   └── requirements.txt
    └── ...
    ```

2.  **Dependencies cho Functions (`packages/functions/requirements.txt`):**
    *   **Hành động:** File này phải chứa tất cả các thư viện cần thiết cho cả "Nhạc trưởng" và "Người giám sát".
        ```
        Flask>=3.0.0
        gunicorn>=21.2.0
        firebase-functions
        firebase-admin
        google-cloud-sql-connector[pg8000]
        SQLAlchemy>=2.0.0
        google-cloud-pubsub>=2.18.0
        google-cloud-run>=0.9.0
        ```

#### **Phần 3.2: Viết "Bản thiết kế Người giám sát" (`Dockerfile` cho Functions)**

*   **Hành động:** Tạo một file tên là `Dockerfile` **bên trong thư mục `packages/functions`** với nội dung chính xác như sau.

```dockerfile
# Giai đoạn 1: Base Image & Dependencies
FROM python:3.11-slim as base

# Đặt thư mục làm việc.
WORKDIR /srv

# Cài đặt các dependency hệ thống cần thiết cho PostgreSQL connector.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Sao chép file requirements trước để tận dụng caching.
COPY requirements.txt .

# Cài đặt các thư viện Python.
RUN pip install --no-cache-dir -r requirements.txt


# Giai đoạn 2: Production Image
FROM python:3.11-slim as final

WORKDIR /srv

# Sao chép môi trường Python đã được cài đặt từ giai đoạn 'base'.
COPY --from=base /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=base /usr/local/bin/ /usr/local/bin/

# Sao chép code ứng dụng của chúng ta (main.py và executor.py).
COPY . .

# Cloud Run yêu cầu một web server phải chạy trên cổng được cung cấp.
# Gunicorn là một web server production-ready cho Flask.
# Chúng ta sẽ chạy ứng dụng Flask trong file executor.py.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 executor:app
```

#### **Phần 3.3: Viết Code cho "Nhạc trưởng" và "Người giám sát"**

*   **Hành động:**
    1.  Đặt code cho "Nhạc trưởng" (`orchestrate_scrapes`) và các hàm API khác vào file `packages/functions/main.py`.
    2.  Đặt code cho "Người giám sát" (`scrape_job_executor`) vào file `packages/functions/executor.py`.
    *   *Alex's Note: Chúng ta sẽ sử dụng các phiên bản code cuối cùng, đã được gỡ lỗi hoàn chỉnh từ các bước trước.*
    *   Sử dụng các phiên bản code cuối cùng của `main.py` và `executor.py`.
    *   **Ghi chú Quan trọng (Alex's Note):** Phải đảm bảo logic kết nối database trong `main.py` (hàm `get_db_engine`) được cấu hình để **chỉ sử dụng IP Public và tắt IAM Auth**: `ip_type=IPTypes.PUBLIC` và `enable_iam_auth=False`. Đây là bài học quan trọng nhất chúng ta đã rút ra.

#### **Phần 3.4: Cập nhật "Bản hướng dẫn Lắp ráp" (`cloudbuild.yaml`)**

*   **Hành động:** Mở file `cloudbuild.yaml` ở thư mục gốc và **thêm vào bước build thứ hai** cho "Người giám sát".

```yaml
steps:
  # Bước 1: Build image của Scraper (giữ nguyên)
  - name: 'gcr.io/cloud-builders/docker'
    id: 'Build Scraper Image'
    args:
      - 'build'
      - '-t'
      - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/scraper:latest'
      - '-t'
      - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/scraper:$SHORT_SHA'
      - '.' # Dockerfile ở thư mục gốc

  # Bước 2: Build image của Executor/Functions (THÊM MỚI)
  - name: 'gcr.io/cloud-builders/docker'
    id: 'Build Executor Service Image'
    args:
      - 'build'
      - '-t'
      - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/executor-service:latest'
      - '-f' # Chỉ định rõ file Dockerfile cần dùng
      - 'packages/functions/Dockerfile'
      - 'packages/functions' # Context cho việc build là thư mục functions

# Cập nhật danh sách images để đẩy cả hai lên Artifact Registry.
images:
  - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/scraper:latest'
  - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/scraper:$SHORT_SHA'
  - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/nhaminhbach-repo/executor-service:latest'

options:
  logging: CLOUD_LOGGING_ONLY
```

#### **Phần 3.5: Triển khai các Dịch vụ và Job**

Bây giờ chúng ta đã có image, chúng ta sẽ triển khai chúng. Các lệnh này chỉ cần chạy **một lần** để thiết lập.

1.  **Triển khai "Công nhân" (`scrape-job`):**
    ```bash
    gcloud run jobs create scrape-job \
      --image="asia-southeast1-docker.pkg.dev/<YOUR_PROJECT_ID>/nhaminhbach-repo/scraper:latest" \
      --region=asia-southeast1 \
      --task-timeout=10m \
      --max-retries=1 \
      --project=<YOUR_PROJECT_ID>
    ```

2.  **Triển khai "Người giám sát" (`scrape-job-executor`):**
    ```bash
    gcloud run deploy scrape-job-executor \
      --image="asia-southeast1-docker.pkg.dev/<YOUR_PROJECT_ID>/nhaminhbach-repo/executor-service:latest" \
      --region=asia-southeast1 \
      --set-env-vars="GCP_PROJECT=<YOUR_PROJECT_ID>,GCP_REGION=asia-southeast1" \
      --allow-unauthenticated \
      --min-instances=0 \
      --max-instances=5 \
      --service-account="<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
      --project=<YOUR_PROJECT_ID>
    ```

3.  **Triển khai "Nhạc trưởng" (`orchestrate_scrapes`):**
    ```bash
    gcloud functions deploy orchestrate_scrapes \
      --gen2 \
      --runtime=python311 \
      --region=asia-southeast1 \
      --source=packages/functions \
      --entry-point=orchestrate_scrapes \
      --trigger-http \
      --no-allow-unauthenticated \
      --set-secrets="DB_PASS=db-password:latest,ORCHESTRATOR_SECRET_KEY=orchestrator-secret-key:latest" \
      --set-env-vars="INSTANCE_CONNECTION_NAME=<YOUR_PROJECT_ID>:asia-southeast1:nhaminhbach-db-prod,DB_USER=postgres,DB_NAME=postgres" \
      --project=<YOUR_PROJECT_ID>
    ```

**(Cải tiến - Chuẩn hóa)**

Chúng ta sẽ **KHÔNG** sử dụng `gcloud functions deploy`. Chúng ta sẽ tuân thủ quy trình **Build riêng -> Deploy riêng** một cách nhất quán cho tất cả các dịch vụ để loại bỏ mọi sự mơ hồ.

1.  **Triển khai "Công nhân" (`scrape-job`):** (Giữ nguyên)
2.  **Triển khai "Người giám sát" (`scrape-job-executor`):**
    *   *Alex's Note: Lệnh này phải sử dụng `--image`, không phải `--source`.*
    ```bash
    gcloud run deploy scrape-job-executor \
      --image="asia-southeast1-docker.pkg.dev/<YOUR_PROJECT_ID>/nhaminhbach-repo/executor-service:latest" \
      --region=asia-southeast1 \
      --set-env-vars="GCP_PROJECT=<YOUR_PROJECT_ID>,GCP_REGION=asia-southeast1" \
      --allow-unauthenticated \
      --min-instances=0 \
      --max-instances=5 \
      --service-account="<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
      --project=<YOUR_PROJECT_ID>
    ```

3.  **Triển khai "Nhạc trưởng" (`orchestrate_scrapes`):**
    *   *Alex's Note: Chúng ta sẽ coi "Nhạc trưởng" là một dịch vụ Cloud Run, giống hệt "Người giám sát", để đảm bảo tính nhất quán. Nó sẽ sử dụng cùng một Docker image `executor-service` vì chúng nằm trong cùng một codebase.*
    ```bash
    gcloud run deploy orchestrate-scrapes \
      --image="asia-southeast1-docker.pkg.dev/<YOUR_PROJECT_ID>/nhaminhbach-repo/executor-service:latest" \
      --region=asia-southeast1 \
      --no-allow-unauthenticated \
      --service-account="<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
      --set-secrets="DB_PASS=db-password:latest,ORCHESTRATOR_SECRET_KEY=orchestrator-secret-key:latest" \
      --set-env-vars="INSTANCE_CONNECTION_NAME=<YOUR_PROJECT_ID>:asia-southeast1:nhaminhbach-db-prod,DB_USER=postgres,DB_NAME=postgres" \
      --project=<YOUR_PROJECT_ID>
    ```
    *   **Quan trọng:** Sau khi triển khai, `cloudbuild.yaml` cần được cập nhật để nó có thể tìm và chạy đúng hàm (`orchestrate_scrapes` hoặc `scrape_job_executor`) trong cùng một image. Điều này đòi hỏi phải sửa `CMD` trong Dockerfile của functions để nó có thể chọn entrypoint, ví dụ dùng `gunicorn --bind :$PORT "main:create_app('${ENTRYPOINT}')"`. Đây là một bước nâng cao, nhưng nó đảm bảo tính nhất quán.

---
**Kết thúc Giai đoạn 3**

Sau giai đoạn này, tất cả các bộ phận phần mềm đã được triển khai và đang chạy trên Google Cloud.
*   "Công nhân" (`scrape-job`) sẵn sàng nhận lệnh.
*   "Người giám sát" (`scrape-job-executor`) sẵn sàng nhận các phiếu lệnh từ "băng chuyền".
*   "Nhạc trưởng" (`orchestrate_scrapes`) sẵn sàng để được kích hoạt.

Tuyệt vời. Tất cả các bộ phận của "Nh-à máy" đã được sản xuất và đặt vào vị trí. Bây giờ là lúc chúng ta kết nối chúng lại bằng hệ thống dây điện và băng chuyền để dây chuyền sản xuất có thể hoạt động.

---

### **Giai đoạn 4: Kết nối Dây chuyền (Wiring the Factory)**

**Mục tiêu:** Thiết lập các dịch vụ "vô hình" — Pub/Sub và Cloud Scheduler — để tạo ra một luồng dữ liệu tự động, theo lịch trình.

#### **Phần 4.1: Tạo "Băng chuyền" (Pub/Sub Topic)**

Đây là kênh giao tiếp giữa "Nhạc trưởng" và "Người giám sát".

*   **Hành động:** Chạy lệnh sau trong Cloud Shell để tạo topic.

```bash
gcloud pubsub topics create scrape-requests \
  --project=<YOUR_PROJECT_ID>
```

#### **Phần 4.2: Kết nối "Băng chuyền" với "Người giám sát" (Pub/Sub Push Subscription)**

Chúng ta sẽ ra lệnh cho Pub/Sub tự động "đẩy" mỗi phiếu lệnh đến cho "Người giám sát" ngay khi nó xuất hiện.

1.  **Lấy URL của "Người giám sát":**
    ```bash
    EXECUTOR_URL=$(gcloud run services describe scrape-job-executor --region=asia-southeast1 --project=<YOUR_PROJECT_ID> --format 'value(status.url)')
    ```

2.  **Tạo Push Subscription:**
    ```bash
    gcloud pubsub subscriptions create scrape-requests-sub \
      --topic=scrape-requests \
      --push-endpoint="$EXECUTOR_URL" \
      --push-auth-service-account="<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
      --project=<YOUR_PROJECT_ID>
    ```
    *   **Thay thế:** `<PROJECT_NUMBER>` bằng Project Number của bạn.
    *   *Alex's Note:* Tham số `--push-auth-service-account` là cực kỳ quan trọng. Nó tạo ra một OIDC token đã được xác thực, cho phép Pub/Sub gọi đến dịch vụ `scrape-job-executor` (vốn dĩ không công khai).

#### **Phần 4.3: Thiết lập "Đồng hồ Báo thức" (Cloud Scheduler)**

Đây là bộ phận sẽ khởi động toàn bộ dây chuyền theo lịch trình.

1.  **Lấy URL của "Nhạc trưởng":**
    ```bash
    ORCHESTRATOR_URL=$(gcloud functions describe orchestrate_scrapes --region=asia-southeast1 --project=<YOUR_PROJECT_ID> --gen2 --format 'value(serviceConfig.uri)')
    ```

2.  **Tạo Cloud Scheduler Job:**
    ```bash
    gcloud scheduler jobs create http orchestrate-scraper-schedule \
      --location=asia-southeast1 \
      --schedule="0 */1 * * *" \
      --uri="$ORCHESTRATOR_URL" \
      --http-method=POST \
      --oidc-service-account-email="<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
      --oidc-token-audience="$ORCHESTRATOR_URL" \
      --project=<YOUR_PROJECT_ID>
    ```
    *   **Lưu ý:** Lịch trình `0 */1 * * *` có nghĩa là "chạy vào phút thứ 0 của mỗi giờ" (tức là mỗi giờ một lần).

#### **Phần 4.4: Cấp Quyền Hoạt động Cuối cùng**

Các dịch vụ cần được cấp quyền để tương tác với nhau.

1.  **Cấp quyền cho "Nhạc trưởng" được phép publish lên "Băng chuyền":**
    ```bash
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
      --role="roles/pubsub.publisher"
    ```

2.  **Cấp quyền cho "Người giám sát" được phép ra lệnh cho "Công nhân":**
    ```bash
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
      --role="roles/run.invoker"
    ```

3.  **Cấp quyền cho "Đồng hồ Báo thức" được phép gọi "Nhạc trưởng":**
    ```bash
    gcloud functions add-iam-policy-binding orchestrate_scrapes \
      --region=asia-southeast1 \
      --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
      --role="roles/cloudfunctions.invoker" \
      --project=<YOUR_PROJECT_ID> \
      --gen2
    ```

---
**Kết thúc Giai đoạn 4 - Nhà máy đã Hoàn thiện!**

Chúc mừng! Bạn đã hoàn thành việc xây dựng và kết nối toàn bộ "Nhà máy Dữ liệu".

*   Mỗi giờ một lần, Cloud Scheduler sẽ kích hoạt `orchestrate_scrapes`.
*   `orchestrate_scrapes` sẽ đọc database và gửi các mệnh lệnh scrape vào Pub/Sub.
*   Pub/Sub sẽ đẩy các mệnh lệnh này đến `scrape-job-executor`.
*   `scrape-job-executor` sẽ kích hoạt các `scrape-job` trên Cloud Run.
*   `scrape-job` sẽ thực thi việc scraping.

**Bước cuối cùng:**
Chạy một bài kiểm tra cuối cùng để đảm bảo mọi thứ hoạt động.
```bash
gcloud scheduler jobs run orchestrate-scraper-schedule --location=asia-southeast1
```
Sau đó, hãy vào **Cloud Run -> JOBS -> `scrape-job` -> EXECUTIONS** để xem các "Công nhân" bắt đầu làm việc.
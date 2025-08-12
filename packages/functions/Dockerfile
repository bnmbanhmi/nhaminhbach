# 1. Base Image
FROM python:3.11-slim

# 2. Set APP_HOME
ENV APP_HOME /srv
WORKDIR $APP_HOME

# Cài đặt các dependency hệ thống cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy Requirements
COPY requirements.txt .

# 4. Install Dependencies
# Thêm gunicorn vào requirements.txt hoặc cài đặt trực tiếp ở đây
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 5. Copy Application Code
# Chỉ copy file executor.py, vì chúng ta không cần main.py nữa
COPY executor.py .

# 6. Expose Port
EXPOSE 8080

# 7. Start the server
# Dùng gunicorn để chạy ứng dụng Flask trong file executor.py
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 executor:app
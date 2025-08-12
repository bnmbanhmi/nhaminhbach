import os
import json
import base64
import logging
from flask import Flask, request, Response

from google.cloud import run_v2

# Cấu hình logging cơ bản
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Khởi tạo client một cách an toàn
run_client: run_v2.JobsClient = None

def get_run_client() -> run_v2.JobsClient:
    global run_client
    if run_client is None:
        run_client = run_v2.JobsClient()
        logger.info("Executor: Cloud Run Jobs client initialized.")
    return run_client

@app.route("/", methods=["POST"])
def execute_scrape_job_handler():
    """
    Đây là một endpoint HTTP mà Pub/Sub sẽ gọi.
    Nó giải nén payload của Pub/Sub và kích hoạt Cloud Run Job.
    """
    envelope = request.get_json(silent=True)
    if not envelope or "message" not in envelope:
        logger.error("Bad Request: Invalid Pub/Sub envelope")
        return "Bad Request", 400

    try:
        message = envelope["message"]
        encoded_data = message.get("data")
        if not encoded_data:
            logger.error("Executor: Received Pub/Sub message with no data.")
            # Trả về 204 No Content để Pub/Sub không thử lại tin nhắn này
            return "", 204

        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        message_payload = json.loads(decoded_data)
        url = message_payload.get("url")

        if not url:
            logger.error(f"Executor: No 'url' found in message payload: {message_payload}")
            return "", 204

        logger.info(f"Executor: Received request to execute scrape job for URL: {url}")

        client = get_run_client()
        gcp_project = os.environ.get("GCP_PROJECT")
        gcp_region = os.environ.get("GCP_REGION")
        job_name = f"projects/{gcp_project}/locations/{gcp_region}/jobs/scrape-job"

        run_job_request = run_v2.RunJobRequest(
            name=job_name,
            overrides=run_v2.types.RunJobRequest.Overrides(
                container_overrides=[
                    run_v2.types.RunJobRequest.Overrides.ContainerOverride(
                        command=["python"],
                        args=["main.py", url]
                    )
                ]
            ),
        )

        operation = client.run_job(request=run_job_request)
        logger.info(f"Executor: Successfully triggered job for URL: {url}. Operation: {operation.metadata.name}")

        # Trả về 204 No Content để báo cho Pub/Sub rằng chúng ta đã xử lý thành công
        return "", 204

    except Exception as e:
        logger.error(f"Executor: An unexpected error occurred: {e}", exc_info=True)
        # Trả về lỗi 500 để Pub/Sub có thể thử lại tin nhắn này sau
        return "Internal Server Error", 500

if __name__ == "__main__":
    # Lấy cổng từ biến môi trường PORT, mặc định là 8080
    server_port = os.environ.get("PORT", 8080)
    # Chạy web server Flask
    app.run(debug=False, host="0.0.0.0", port=server_port)
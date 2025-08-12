import os
import json
import base64
from firebase_functions import pubsub_fn, logger
from google.cloud import run_v2

# Chỉ khởi tạo client cần thiết cho hàm này
run_client: run_v2.JobsClient = None

def get_run_client() -> run_v2.JobsClient:
    global run_client
    if run_client is None:
        run_client = run_v2.JobsClient()
        logger.info("Executor: Cloud Run Jobs client initialized.")
    return run_client

@pubsub_fn.on_message_published(topic="scrape-requests", region="asia-southeast1")
def scrape_job_executor(event: pubsub_fn.CloudEvent[pubsub_fn.Message]) -> None:
    """
    Hàm này được thiết kế riêng để lắng nghe Pub/Sub và chỉ làm một việc:
    Kích hoạt Cloud Run Job.
    """
    try:
        # Truy cập dữ liệu một cách an toàn và đúng đắn
        encoded_data = event.data.message.data
        if not encoded_data:
            logger.error("Executor: Received Pub/Sub message with no data.")
            return

        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        message_payload = json.loads(decoded_data)
        url = message_payload.get("url")

        if not url:
            logger.error(f"Executor: No 'url' found in message payload: {message_payload}")
            return

        logger.info(f"Executor: Received request to execute scrape job for URL: {url}")

        client = get_run_client()
        gcp_project = os.environ.get("GCP_PROJECT")
        gcp_region = os.environ.get("GCP_REGION")
        job_name = f"projects/{gcp_project}/locations/{gcp_region}/jobs/scrape-job"

        request = run_v2.RunJobRequest(
            name=job_name,
            overrides=run_v2.types.RunJobRequest.Overrides(
                container_overrides=[
                    run_v2.types.RunJobRequest.Overrides.ContainerOverride(
                        args=[url]
                    )
                ]
            ),
        )

        operation = client.run_job(request=request)
        logger.info(f"Executor: Successfully triggered job for URL: {url}. Operation: {operation.metadata.name}")

    except Exception as e:
        logger.error(f"Executor: An unexpected error occurred: {e}", exc_info=True)
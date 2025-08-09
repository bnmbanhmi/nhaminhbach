import os
import json
import uuid
import base64
import concurrent.futures
from decimal import Decimal
from typing import Any
from datetime import datetime

from firebase_functions import https_fn, options, logger, pubsub_fn
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import pubsub_v1, run_v2
from google.api_core import gapic_v1
import sqlalchemy

# =================================================================================
#  1. GLOBAL SETUP & CONFIGURATION
# =================================================================================
# Tải cấu hình từ biến môi trường
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
ORCHESTRATOR_SECRET_KEY = os.environ.get("ORCHESTRATOR_SECRET_KEY")
GCP_PROJECT = os.environ.get("GCP_PROJECT")
GCP_REGION = "asia-southeast1"


IS_EMULATOR = os.environ.get("FUNCTIONS_EMULATOR") == "true"

# Cài đặt toàn cục cho tất cả các function trong region này
options.set_global_options(region=GCP_REGION, max_instances=5)

# Biến toàn cục cho SQLAlchemy Engine, được khởi tạo một cách "lười biếng"
db_engine: sqlalchemy.engine.Engine = None
publisher_client: pubsub_v1.PublisherClient = None
run_client: run_v2.JobsClient = None


# Thống nhất cấu hình CORS cho tất cả các endpoint
# Cho phép tất cả các nguồn gốc trong môi trường dev để dễ dàng kiểm thử
CORS_CONFIG = options.CorsOptions(
    cors_origins=["*"],
    cors_methods=["get", "post"]
)

# =================================================================================
#  2. CLIENT INITIALIZATION (Refactored into helper functions)
# =================================================================================

def get_db_engine() -> sqlalchemy.engine.Engine:
    global db_engine
    if db_engine is not None:
        return db_engine

    def getconn() -> Any:
        # Sử dụng IS_EMULATOR đã được định nghĩa ở global
        enable_iam_auth = not IS_EMULATOR
        conn = Connector().connect(
            INSTANCE_CONNECTION_NAME, "pg8000", user=DB_USER, password=DB_PASS,
            db=DB_NAME, ip_type=IPTypes.PUBLIC if IS_EMULATOR else IPTypes.PRIVATE,
            enable_iam_auth=enable_iam_auth
        )
        return conn

    db_engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)
    logger.info("Database engine initialized.")
    return db_engine

def get_publisher_client() -> pubsub_v1.PublisherClient:
    """Initializes and returns a global Pub/Sub client with a timeout."""
    global publisher_client
    if publisher_client is None:
        # Configure transport with custom channel options for timeout
        transport = pubsub_v1.services.publisher.transports.PublisherGrpcTransport(
            channel=pubsub_v1.services.publisher.transports.PublisherGrpcTransport.create_channel(
                client_options={"api_endpoint": "pubsub.googleapis.com:443"}
            )
        )
        # Configure publisher options with a 60-second timeout
        publisher_options = pubsub_v1.types.PublisherOptions(
            enable_message_ordering=False,
            timeout=60.0,  # 60 second timeout for publish requests
        )
        # Initialize the client with the custom transport and options
        publisher_client = pubsub_v1.PublisherClient(
            transport=transport, publisher_options=publisher_options
        )
        logger.info("Pub/Sub publisher client initialized with custom timeout.")
    return publisher_client

def get_run_client() -> run_v2.JobsClient:
    """Initializes and returns a global Cloud Run Jobs client."""
    global run_client
    if run_client is None:
        run_client = run_v2.JobsClient()
        logger.info("Cloud Run Jobs client initialized.")
    return run_client


# =================================================================================
#  3. UTILITY FUNCTIONS
# =================================================================================

def default_json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default."""
    if isinstance(obj, (datetime, uuid.UUID)):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


# =================================================================================
#  4. API ENDPOINTS
# =================================================================================

@https_fn.on_request(cors=CORS_CONFIG)
def create_listing(req: https_fn.Request) -> https_fn.Response:
    """
    API Endpoint to create a new listing with dynamic attributes.
    Refactored for clarity and correctness using named parameters.
    """
    if req.method != "POST":
        return https_fn.Response(f"Method {req.method} not allowed.", status=405)

    try:
        data = req.get_json(silent=True)
        if not data:
            return https_fn.Response("Invalid JSON payload.", status=400)

        listing_data = data.get("listing")
        attributes_data = data.get("attributes")

        if not listing_data or not isinstance(attributes_data, list):
            return https_fn.Response("Missing or malformed 'listing' or 'attributes' data.", status=400)

        engine = get_db_engine()
        new_listing_id = None

        with engine.connect() as conn:
            with conn.begin() as tx:
                try:
                    # 1. Chèn vào bảng 'listings' sử dụng tham số có tên
                    insert_listing_stmt = sqlalchemy.text("""
                        INSERT INTO listings (title, description, price_monthly_vnd, area_m2, address_ward, address_district, source_url)
                        VALUES (:title, :description, :price, :area, :ward, :district, :source)
                        RETURNING id
                    """)
                    result = conn.execute(
                        insert_listing_stmt,
                        {
                            "title": listing_data.get("title"),
                            "description": listing_data.get("description"),
                            "price": int(listing_data.get("price_monthly_vnd", 0)),
                            "area": float(listing_data.get("area_m2", 0)),
                            "ward": listing_data.get("address_ward"),
                            "district": listing_data.get("address_district"),
                            "source": f"qc-form-{uuid.uuid4()}" # Tạo source_url duy nhất
                        }
                    )
                    new_listing_id = result.scalar_one()

                    # 2. Chuẩn bị và chèn vào bảng 'listing_attributes'
                    if attributes_data:
                        attrs_to_insert = []
                        for attr in attributes_data:
                            # Tạo một dictionary rõ ràng cho mỗi hàng
                            row = {
                                "listing_id": new_listing_id,
                                "attribute_id": attr.get("attribute_id"),
                                "value_boolean": None,
                                "value_integer": None,
                                "value_string": None,
                            }
                            
                            value = attr.get("value")
                            
                            # Phân loại và gán vào đúng key trong dictionary
                            if isinstance(value, bool):
                                row["value_boolean"] = value
                            elif isinstance(value, int):
                                row["value_integer"] = value
                            else:
                                row["value_string"] = str(value)
                            
                            attrs_to_insert.append(row)
                        
                        # Sử dụng tham số có tên để chèn hàng loạt
                        if attrs_to_insert:
                            insert_attrs_stmt = sqlalchemy.text("""
                                INSERT INTO listing_attributes (listing_id, attribute_id, value_boolean, value_integer, value_string)
                                VALUES (:listing_id, :attribute_id, :value_boolean, :value_integer, :value_string)
                            """)
                            conn.execute(insert_attrs_stmt, attrs_to_insert)
                    
                    tx.commit()
                except Exception as e:
                    logger.error(f"Transaction failed, rolling back. Error: {e}")
                    tx.rollback()
                    raise

        return https_fn.Response(
            json.dumps({"message": "Listing created successfully", "id": new_listing_id}, default=default_json_serializer),
            status=201, headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        logger.error(f"Error in create_listing: {e}")
        return https_fn.Response("An internal server error occurred.", status=500)


@https_fn.on_request(cors=CORS_CONFIG)
def get_listings(req: https_fn.Request) -> https_fn.Response:
    """API Endpoint để lấy tất cả các tin đăng 'available'."""
    if req.method != "GET":
        return https_fn.Response(f"Method {req.method} not allowed.", status=405)

    sql_query = sqlalchemy.text("""
        SELECT l.*, (
            SELECT json_agg(json_build_object(
                'name', a.name,
                'slug', a.slug,
                'value', COALESCE(la.value_boolean::text, la.value_integer::text, la.value_string)
            ))
            FROM listing_attributes la JOIN attributes a ON la.attribute_id = a.id
            WHERE la.listing_id = l.id
        ) as attributes
        FROM listings l WHERE l.status = 'available'
    """)

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sql_query).fetchall()
        
        listings_data = [dict(row._mapping) for row in result]
        json_response = json.dumps(listings_data, default=default_json_serializer)

        return https_fn.Response(json_response, status=200, headers={"Content-Type": "application/json"})

    except Exception as e:
        logger.error(f"Error in get_listings: {e}")
        return https_fn.Response("An internal server error occurred.", status=500)


@https_fn.on_request(cors=CORS_CONFIG)
def get_listing_by_id(req: https_fn.Request) -> https_fn.Response:
    """Lấy thông tin một tin đăng cụ thể bằng ID (UUID)."""
    if req.method != "GET":
        return https_fn.Response(f"Method {req.method} not allowed.", status=405)

    listing_id_str = req.args.get("id")
    if not listing_id_str:
        return https_fn.Response("Missing 'id' query parameter.", status=400)

    try:
        listing_id = uuid.UUID(listing_id_str)
    except ValueError:
        return https_fn.Response(f"Invalid 'id' format. Must be a valid UUID.", status=400)

    sql_query = sqlalchemy.text("""
        SELECT l.*, (
            SELECT json_agg(json_build_object(
                'name', a.name,
                'slug', a.slug,
                'value', COALESCE(la.value_boolean::text, la.value_integer::text, la.value_string)
            ))
            FROM listing_attributes la JOIN attributes a ON la.attribute_id = a.id
            WHERE la.listing_id = l.id
        ) as attributes
        FROM listings l WHERE l.id = :listing_id
    """)

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sql_query, {"listing_id": listing_id}).fetchone()

        if not result:
            return https_fn.Response(f"Listing with ID {listing_id} not found.", status=404)

        listing_data = dict(result._mapping)
        json_response = json.dumps(listing_data, default=default_json_serializer)

        return https_fn.Response(json_response, status=200, headers={"Content-Type": "application/json"})

    except Exception as e:
        logger.error(f"Error fetching listing ID {listing_id}: {e}")
        return https_fn.Response("An internal server error occurred.", status=500)


@https_fn.on_request(cors=CORS_CONFIG)
def get_all_attributes(req: https_fn.Request) -> https_fn.Response:
    """
    API Endpoint to get all possible attributes for a listing.
    This is used by the frontend to build the QC form.
    """
    if req.method != "GET":
        return https_fn.Response(f"Method {req.method} not allowed.", status=405)

    sql_query = sqlalchemy.text("SELECT * FROM attributes ORDER BY type, id;")

    try:
        # Lấy engine. Việc khởi tạo chỉ xảy ra ở lần gọi đầu tiên.
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sql_query).fetchall()
        
        attributes_data = [dict(row._mapping) for row in result]
        json_response = json.dumps(attributes_data, default=default_json_serializer)

        return https_fn.Response(json_response, status=200, headers={"Content-Type": "application/json"})

    except Exception as e:
        logger.error(f"Error in get_all_attributes: {e}")
        return https_fn.Response("An internal server error occurred.", status=500)

# =================================================================================
#  5. ORCHESTRATION & BACKGROUND FUNCTIONS
# =================================================================================
@pubsub_fn.on_message_published(topic="scrape-requests")
def execute_scrape_job(event: pubsub_fn.CloudEvent) -> None:
    """
    Triggered by a message on 'scrape-requests' topic.
    Executes the Cloud Run 'scrape-job' with the URL from the message.
    """
    try:
        # 1. Decode the message payload
        encoded_data = event.data.get("message", {}).get("data")
        if not encoded_data:
            logger.error("Received Pub/Sub message with no data.")
            return

        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        message_payload = json.loads(decoded_data)
        url = message_payload.get("url")

        if not url:
            logger.error(f"No 'url' found in message payload: {message_payload}")
            return

        logger.info(f"Received request to execute scrape job for URL: {url}")

        # 2. Get the Cloud Run client
        client = get_run_client()
        job_name = f"projects/{GCP_PROJECT}/locations/{GCP_REGION}/jobs/scrape-job"

        # 3. Prepare and run the job
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
        logger.info(f"Successfully triggered job for URL: {url}. Operation: {operation.metadata.name}")

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from Pub/Sub message: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred in execute_scrape_job: {e}")


@https_fn.on_request(cors=CORS_CONFIG)
def orchestrate_scrapes(req: https_fn.Request) -> https_fn.Response:
    """
    Reads active groups from the DB, publishes scrape jobs to Pub/Sub,
    and updates their last_scraped_at timestamp.
    Refactored for resilience, workload management, and performance.
    Triggered securely by Cloud Scheduler.
    """
    # 1. Security Check
    auth_header = req.headers.get("Authorization")
    expected_token = f"Bearer {ORCHESTRATOR_SECRET_KEY}"
    if not ORCHESTRATOR_SECRET_KEY or auth_header != expected_token:
        logger.error("Unauthorized access attempt to orchestrate_scrapes.")
        return https_fn.Response("Unauthorized", status=401)

    project_id = os.environ.get("GCP_PROJECT")
    if not project_id:
        logger.error("GCP_PROJECT environment variable not set.")
        return https_fn.Response("Server configuration error: GCP_PROJECT not set.", status=500)

    # Workload limit per invocation
    MAX_JOBS_PER_RUN = 30

    try:
        # 2. Get lazily-initialized clients
        publisher = get_publisher_client()
        engine = get_db_engine()

        topic_name = "scrape-requests"
        topic_path = publisher.topic_path(project_id, topic_name)
        
        urls_to_update = []
        results = []

        # 3. Use a transaction to fetch groups and update them atomically
        with engine.connect() as conn:
            with conn.begin() as tx:
                try:
                    # Fetch groups that need scraping, prioritizing new/old ones
                    query = sqlalchemy.text("""
                        SELECT url FROM groups
                        WHERE is_active = TRUE
                        ORDER BY last_scraped_at ASC NULLS FIRST
                        LIMIT :limit;
                    """)
                    results = conn.execute(query, {"limit": MAX_JOBS_PER_RUN}).fetchall()

                    if not results:
                        logger.info("No active groups found to scrape in this run.")
                        # We still commit the (empty) transaction and return success
                        tx.commit()
                        return https_fn.Response(
                            json.dumps({"message": "No active groups to process."}),
                            status=200, headers={"Content-Type": "application/json"}
                        )

                    # 4. Publish jobs and collect futures
                    publish_futures = []
                    urls_to_publish = [row.url for row in results]
                    
                    for i, url in enumerate(urls_to_publish):
                        payload = {"url": url}
                        encoded_payload = json.dumps(payload).encode("utf-8")
                        # The client-level timeout of 60s applies to each publish call
                        future = publisher.publish(topic_path, encoded_payload)
                        # Associate future with its URL for error reporting
                        publish_futures.append((future, url))

                    # 5. Wait for publish operations to complete and collect results
                    for future, url in publish_futures:
                        try:
                            # result() will block until the message is published or the timeout occurs
                            future.result()
                            # If it didn't raise an exception, it was successful
                            urls_to_update.append(url)
                        except Exception as e:
                            logger.error(f"Failed to publish job for URL {url}. Error: {e}")

                    # 6. Update the database for the successfully published jobs
                    if urls_to_update:
                        update_stmt = sqlalchemy.text("""
                            UPDATE groups
                            SET last_scraped_at = NOW()
                            WHERE url = ANY(:urls);
                        """)
                        conn.execute(update_stmt, {"urls": urls_to_update})
                        logger.info(f"Updated last_scraped_at for {len(urls_to_update)} groups.")

                    tx.commit()

                except Exception as e:
                    logger.error(f"Transaction failed, rolling back. Error: {e}")
                    tx.rollback()
                    raise # Re-raise the exception to be caught by the outer block

        total_targets = len(results)
        published_jobs = len(urls_to_update)
        
        return https_fn.Response(
            json.dumps({
                "message": f"Orchestration complete. Successfully published {published_jobs}/{total_targets} jobs.",
                "published_jobs": published_jobs,
                "total_targets": total_targets,
            }),
            status=200,
            headers={"Content-Type": "application/json"}
        )

    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(f"Database error during scrape orchestration: {e}")
        return https_fn.Response("A database error occurred.", status=500)
    except Exception as e:
        logger.error(f"An unexpected error occurred during scrape orchestration: {e}")
        return https_fn.Response("An internal server error occurred.", status=500)

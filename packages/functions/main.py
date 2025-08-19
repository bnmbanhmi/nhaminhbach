import os
import json
import time
import uuid
import base64
import concurrent.futures
import requests
from decimal import Decimal
from typing import Any
from datetime import datetime

from firebase_functions import https_fn, options, logger, pubsub_fn, scheduler_fn
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import pubsub_v1, run_v2
from google.api_core import gapic_v1
import sqlalchemy
from sqlalchemy import text
from utils import get_secret

# Import transformation logic for LLM processing
try:
    from transformation_engine import transform_raw_post
    from data_contracts import Listing, Attribute
    TRANSFORMATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Transformation modules not available: {e}")
    TRANSFORMATION_AVAILABLE = False

# =================================================================================
#  1. GLOBAL SETUP & CONFIGURATION
# =================================================================================

# Cài đặt toàn cục cho tất cả các function trong region này
options.set_global_options(region="asia-southeast1", max_instances=5)

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

    # Các biến môi trường này sẽ được cung cấp bởi cấu hình `run_with`
    INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_NAME = os.environ.get("DB_NAME")
    IS_EMULATOR = os.environ.get("FUNCTIONS_EMULATOR") == "true"
    
    # Get database password from Secret Manager
    GCP_PROJECT = os.environ.get("GCP_PROJECT")
    if not GCP_PROJECT:
        raise RuntimeError("GCP_PROJECT environment variable must be set")
    DB_PASS = get_secret(GCP_PROJECT, "db-password")

    def getconn() -> Any:
        # Sử dụng IS_EMULATOR đã được định nghĩa ở global
        enable_iam_auth = not IS_EMULATOR
        conn = Connector().connect(
            INSTANCE_CONNECTION_NAME, "pg8000", user=DB_USER, password=DB_PASS,
            db=DB_NAME, ip_type=IPTypes.PUBLIC,
            enable_iam_auth=False
        )
        return conn

    db_engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)
    logger.info("Database engine initialized.")
    return db_engine

def get_publisher_client() -> pubsub_v1.PublisherClient:
    """Initializes and returns a global Pub/Sub client."""
    global publisher_client
    if publisher_client is None:
        # Initialize the client with default settings.
        # Timeouts can be handled on the publish() call itself if needed.
        publisher_client = pubsub_v1.PublisherClient()
        logger.info("Pub/Sub publisher client initialized.")
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


def _get_ingest_api_key() -> str:
    GCP_PROJECT = os.environ.get("GCP_PROJECT")
    if not GCP_PROJECT:
        raise RuntimeError("GCP_PROJECT environment variable must be set")
    return get_secret(GCP_PROJECT, "ingest-api-key")


# =================================================================================
#  4. API ENDPOINTS
# =================================================================================

@https_fn.on_request(
    cors=CORS_CONFIG
)
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


@https_fn.on_request(
    cors=CORS_CONFIG
)
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


@https_fn.on_request(
    cors=CORS_CONFIG
)
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


@https_fn.on_request(
    cors=CORS_CONFIG
)
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


@https_fn.on_request(
    cors=CORS_CONFIG
)
def ingest_scraped_data(req: https_fn.Request) -> https_fn.Response:
    """
    Secure endpoint for local scraper to submit scraped posts into the listings table.
    - Auth: X-API-Key header must match INGEST_API_KEY env var.
    - Dedup: Check listings by source_url (permalink). Skip existing.
    - Insert: New rows into listings with status='pending_review' and placeholder values.
    Payloads supported:
      - { "posts": [ {content, image_urls[], permalink}, ... ] }
      - [ {content, image_urls[], permalink}, ... ]
      - {content, image_urls[], permalink} (single)
    """
    if req.method != "POST":
        return https_fn.Response(f"Method {req.method} not allowed.", status=405)

    # API Key check
    api_key_header = req.headers.get("X-API-Key") or req.headers.get("x-api-key")
    if not api_key_header or api_key_header != _get_ingest_api_key():
        return https_fn.Response("Unauthorized", status=401)

    try:
        logger.info("Starting ingest_scraped_data processing")
        
        # Add detailed logging for payload parsing
        try:
            logger.info("Attempting to parse JSON payload")
            payload = req.get_json(silent=True)
            logger.info("JSON parsing successful")
        except Exception as json_error:
            logger.error(f"JSON parsing failed: {json_error}")
            raise json_error
        if payload is None:
            return https_fn.Response("Invalid JSON payload.", status=400)

        logger.info(f"Received payload: {json.dumps(payload, default=str)}")

        # Normalize posts array from supported payload shapes
        posts = []
        if isinstance(payload, dict) and isinstance(payload.get("posts"), list):
            posts = payload.get("posts", [])
        elif isinstance(payload, list):
            posts = payload
        elif isinstance(payload, dict) and ("permalink" in payload or "content" in payload):
            posts = [payload]
        else:
            return https_fn.Response("Unsupported payload shape. Provide {posts: [...]}, an array, or a single post object.", status=400)

        logger.info(f"Processing {len(posts)} posts")

        new_count = 0
        dup_count = 0

        engine = get_db_engine()
        logger.info("About to connect to database")
        with engine.connect() as conn:
            logger.info("Database connection established")
            with conn.begin() as tx:
                logger.info("Transaction started")
                try:
                    # Prepare statements
                    logger.info("Preparing SQL statements")
                    dup_check_sql = text("SELECT 1 FROM listings WHERE source_url = :source_url LIMIT 1")
                    insert_sql = text(
                        """
                        INSERT INTO listings (
                            status, title, description, price_monthly_vnd, area_m2,
                            address_ward, address_district, source_url, image_urls
                        )
                        VALUES (
                            :status, :title, :description, :price, :area,
                            :ward, :district, :source_url, :image_urls
                        )
                        """
                    )
                    logger.info("SQL statements prepared")

                    logger.info(f"Starting loop over {len(posts)} posts")
                    for i, p in enumerate(posts):
                        logger.info(f"=== Processing post {i} ===")
                        try:
                            logger.info(f"Post data: {json.dumps(p, default=str)}")
                            
                            logger.info("Getting permalink")
                            permalink = (p.get("permalink") if isinstance(p, dict) else None) or ""
                            logger.info(f"Permalink: {permalink}")
                            if not isinstance(permalink, str) or not permalink:
                                # If no permalink, skip as we cannot dedup/anchor this post
                                logger.info(f"Skipping post {i}: no valid permalink")
                                dup_count += 1
                                continue

                            logger.info("Checking for duplicates")
                            # Duplicate check
                            if conn.execute(dup_check_sql, {"source_url": permalink}).fetchone():
                                logger.info(f"Skipping post {i}: duplicate permalink {permalink}")
                                dup_count += 1
                                continue

                            logger.info("Getting content and image_urls")
                            content = p.get("content") if isinstance(p, dict) else None
                            logger.info(f"Content: {content}")
                            image_urls = p.get("image_urls") if isinstance(p, dict) else None
                            logger.info(f"Image URLs (before processing): {image_urls}")
                            if not isinstance(image_urls, list):
                                image_urls = []
                            logger.info(f"Image URLs (after processing): {image_urls}")

                            logger.info(f"About to insert post {i} with permalink: {permalink}")
                            
                            # Insert with placeholders for NOT NULL fields
                            conn.execute(
                                insert_sql,
                                {
                                    "status": "pending_review",
                                    "title": "Pending QC",
                                    "description": content or "Pending QC",
                                    "price": 1000000,  # Use 1M VND as minimum valid price
                                    "area": 1.0,  # Use 1.0 instead of 0.0 to satisfy constraint
                                    "ward": "Unknown",
                                    "district": "Unknown",
                                    "source_url": permalink,
                                    "image_urls": image_urls,
                                },
                            )
                            new_count += 1
                            logger.info(f"Successfully inserted post {i}")
                        except Exception as inner_e:
                            # Log and continue with next post, but keep transaction consistent
                            logger.error(f"Failed to ingest post {i}: {inner_e}")
                            logger.error(f"Exception type: {type(inner_e)}")
                            import traceback
                            logger.error(f"Full traceback: {traceback.format_exc()}")

                    logger.info("Loop completed, about to commit")
                    tx.commit()
                    logger.info(f"Transaction committed: {new_count} new, {dup_count} duplicates")
                except Exception as e:
                    logger.error(f"Batch ingest failed, rolling back. Error: {e}")
                    logger.error(f"Exception type: {type(e)}")
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    tx.rollback()
                    raise

        return https_fn.Response(
            json.dumps({
                "message": "Ingestion complete",
                "new_listings_created": new_count,
                "skipped_duplicates": dup_count
            }),
            status=200,
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        logger.error(f"Error in ingest_scraped_data: {e}")
        return https_fn.Response("An internal server error occurred.", status=500)

# =================================================================================
#  5. ORCHESTRATION & BACKGROUND FUNCTIONS
# =================================================================================
@pubsub_fn.on_message_published(
    topic="scrape-requests",
    region="asia-southeast1" # Explicitly define the region
)
def execute_scrape_job(event: pubsub_fn.CloudEvent[pubsub_fn.Message], *args, **kwargs) -> None:
    """
    Triggered by a message on 'scrape-requests' topic.
    Executes the Cloud Run 'scrape-job' with the URL from the message.
    """
    try:
        # 1. Decode the message payload
        encoded_data = event.data.message.data
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
        gcp_project = os.environ.get("GCP_PROJECT")
        gcp_region = os.environ.get("GCP_REGION")
        job_name = f"projects/{gcp_project}/locations/{gcp_region}/jobs/scrape-job"

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


@https_fn.on_request(
    cors=CORS_CONFIG
)
def orchestrate_scrapes(req: https_fn.Request) -> https_fn.Response:
    """
    Reads active groups from the DB, publishes scrape jobs to Pub/Sub,
    and updates their last_scraped_at timestamp.
    Refactored for resilience, workload management, and performance.
    Triggered securely by Cloud Scheduler.
    """
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

                        # Add a small delay to avoid hitting Pub/Sub publish rate limits.
                        time.sleep(0.05)
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


@https_fn.on_request(
    cors=CORS_CONFIG,
    memory=1024,
    timeout_sec=300
)
def transform_property_post(req: https_fn.Request) -> https_fn.Response:
    """
    Transform raw Vietnamese rental property post into structured data using LLM
    
    Accepts POST requests with JSON body:
    {
        "raw_text": "string",
        "source": "string (optional)",
        "metadata": "object (optional)"
    }
    
    Returns structured listing data or error details
    """
    if not TRANSFORMATION_AVAILABLE:
        return https_fn.Response(
            json.dumps({"error": "Transformation engine not available"}),
            status=503,
            headers={"Content-Type": "application/json"}
        )
    
    start_time = datetime.utcnow()
    
    try:
        # Only accept POST requests
        if req.method != "POST":
            return https_fn.Response(
                json.dumps({"error": "Method not allowed"}),
                status=405,
                headers={"Content-Type": "application/json"}
            )
        
        # Parse request body
        try:
            request_data = req.get_json(force=True)
        except Exception:
            return https_fn.Response(
                json.dumps({"error": "Invalid JSON in request body"}),
                status=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Validate required fields
        raw_text = request_data.get("raw_text")
        if not raw_text or len(raw_text.strip()) < 10:
            return https_fn.Response(
                json.dumps({"error": "Raw text must contain at least 10 characters"}),
                status=400,
                headers={"Content-Type": "application/json"}
            )
        
        source = request_data.get("source")
        metadata = request_data.get("metadata", {})
        
        logger.info(f"Processing transformation request for {len(raw_text)} characters of text")
        
        # Call transformation engine
        source_url = metadata.get('source_url', 'api-request') if metadata else 'api-request'
        result = transform_raw_post(raw_text, source_url)
        
        if not result:
            return https_fn.Response(
                json.dumps({"error": "Transformation failed - no result returned"}),
                status=500,
                headers={"Content-Type": "application/json"}
            )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        logger.info(f"Transformation completed successfully in {processing_time:.2f}ms")
        
        response_data = {
            "success": True,
            "data": {
                "listing": result.model_dump() if hasattr(result, 'model_dump') else result,
                "status": "pending_review",
                "source": source,
                "metadata": metadata
            },
            "processing_time_ms": processing_time
        }
        
        return https_fn.Response(
            json.dumps(response_data, default=default_json_serializer),
            status=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        error_msg = f"Transformation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        error_response = {
            "success": False,
            "error": error_msg,
            "processing_time_ms": processing_time
        }
        
        return https_fn.Response(
            json.dumps(error_response, default=default_json_serializer),
            status=500,
            headers={"Content-Type": "application/json"}
        )


# =================================================================================
#  7. TRANSFORMATION TRIGGER (Sprint S7 Task 4)
# =================================================================================

def _process_pending_transformations_logic() -> dict:
    """
    Core logic for processing pending transformations.
    Returns a dictionary with processing results.
    """
    logger.info("Starting transformation processing logic")
    
    engine = get_db_engine()
    transformation_url = "https://transform-property-post-kbmvflixza-as.a.run.app"
    processed_count = 0
    error_count = 0
    
    with engine.connect() as conn:
        # Find pending listings with placeholder data (limit to 10 per run)
        pending_query = text("""
            SELECT id, description, source_url, created_at
            FROM listings 
            WHERE status = 'pending_review' 
            AND title = 'Pending QC'
            ORDER BY created_at ASC
            LIMIT 10
        """)
        
        pending_listings = conn.execute(pending_query).fetchall()
        logger.info(f"Found {len(pending_listings)} pending listings to process")
        
        for listing in pending_listings:
            try:
                listing_id = listing.id
                raw_content = listing.description
                source_url = listing.source_url
                created_at = listing.created_at
                
                logger.info(f"Processing listing {listing_id}")
                
                # Prepare transformation request
                transform_payload = {
                    "raw_text": raw_content,
                    "source": "transformation_trigger", 
                    "metadata": {
                        "listing_id": str(listing_id),
                        "source_url": source_url,
                        "ingested_at": created_at.isoformat() if created_at else None
                    }
                }
                
                # Call transformation function
                logger.info(f"Calling transformation function for listing {listing_id}")
                response = requests.post(
                    transformation_url,
                    json=transform_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=60  # 60 second timeout
                )
                
                if response.status_code == 200:
                    # Parse transformation result
                    result = response.json()
                    
                    if result.get("success"):
                        # Extract structured data
                        transformed_data = result.get("data", {})
                        listing_data = transformed_data.get("listing", {})
                        
                        # Update listing with transformed data
                        update_query = text("""
                            UPDATE listings SET
                                title = COALESCE(:title, title),
                                price_monthly_vnd = COALESCE(:price, price_monthly_vnd), 
                                area_m2 = COALESCE(:area, area_m2),
                                address_ward = COALESCE(:ward, address_ward),
                                address_district = COALESCE(:district, address_district),
                                contact_phone = :phone,
                                status = 'pending_review'
                            WHERE id = :listing_id
                        """)
                        
                        conn.execute(update_query, {
                            "listing_id": listing_id,
                            "title": listing_data.get("title"),
                            "price": listing_data.get("price_monthly_vnd"),
                            "area": listing_data.get("area_m2"), 
                            "ward": listing_data.get("address_ward"),
                            "district": listing_data.get("address_district"),
                            "phone": listing_data.get("contact_phone")
                        })
                        
                        conn.commit()
                        processed_count += 1
                        logger.info(f"Successfully transformed listing {listing_id}")
                        
                    else:
                        error_msg = result.get("error", "Unknown transformation error")
                        logger.error(f"Transformation failed for listing {listing_id}: {error_msg}")
                        error_count += 1
                        
                else:
                    logger.error(f"HTTP error calling transformation function for listing {listing_id}: {response.status_code}")
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing listing {listing_id if 'listing_id' in locals() else 'unknown'}: {e}")
                error_count += 1
                
    return {
        "processed_count": processed_count,
        "error_count": error_count,
        "total_found": len(pending_listings) if 'pending_listings' in locals() else 0
    }


@scheduler_fn.on_schedule(
    schedule="*/30 * * * * *",  # Every 30 seconds
    timezone="UTC"
)
def process_pending_transformations(event) -> None:
    """
    Scheduled function that polls for pending_review listings and triggers transformation.
    """
    try:
        result = _process_pending_transformations_logic()
        logger.info(f"Scheduled transformation batch complete: {result['processed_count']} processed, {result['error_count']} errors")
        
    except Exception as e:
        logger.error(f"Error in scheduled process_pending_transformations: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")


@https_fn.on_request()
def trigger_transformation_batch(req: https_fn.Request) -> https_fn.Response:
    """
    Manual HTTP endpoint to trigger transformation processing (for testing)
    """
    if req.method != "POST":
        return https_fn.Response("Method not allowed", status=405)
        
    try:
        # Call the core transformation logic
        result = _process_pending_transformations_logic()
        
        return https_fn.Response(
            json.dumps({
                "message": "Transformation batch triggered successfully",
                "processed_count": result["processed_count"], 
                "error_count": result["error_count"],
                "total_found": result["total_found"]
            }),
            status=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"Error in trigger_transformation_batch: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return https_fn.Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status=500,
            headers={"Content-Type": "application/json"}
        )

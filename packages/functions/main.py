import os
import json
import uuid
from decimal import Decimal
from typing import Any
from datetime import datetime

from firebase_functions import https_fn, options, logger
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

# =================================================================================
#  1. GLOBAL SETUP & CONFIGURATION
# =================================================================================
# Tải cấu hình từ biến môi trường
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")

# Cài đặt toàn cục cho tất cả các function trong region này
options.set_global_options(region="asia-southeast1", max_instances=5)

# Biến toàn cục cho SQLAlchemy Engine, được khởi tạo một cách "lười biếng"
db_engine: sqlalchemy.engine.Engine = None

# Thống nhất cấu hình CORS cho tất cả các endpoint
# Cho phép tất cả các nguồn gốc trong môi trường dev để dễ dàng kiểm thử
CORS_CONFIG = options.CorsOptions(
    cors_origins=["*"],
    cors_methods=["get", "post"]
)

# =================================================================================
#  2. DATABASE INITIALIZATION (Refactored into a single function)
# =================================================================================

def get_db_engine() -> sqlalchemy.engine.Engine:
    """
    Quản lý việc khởi tạo và tái sử dụng DB engine một cách an toàn.
    Sử dụng pattern "lazy initialization" trên biến toàn cục.
    """
    global db_engine
    if db_engine is None:
        logger.info("Database engine is not initialized. Initializing...")
        try:
            # KIỂM TRA MÔI TRƯỜNG
            is_emulator = os.environ.get("IS_EMULATOR", "false").lower() == "true"

            # Nếu không phải emulator, chúng ta không cần xác thực rõ ràng
            # Nó sẽ tự động dùng Service Account của Cloud Function
            if not is_emulator:
                connector = Connector()
            else:
                # NẾU LÀ EMULATOR, chúng ta tắt tính năng tự động tìm kiếm xác thực
                # và chỉ dựa vào mật khẩu.
                logger.info("Emulator detected. Disabling automatic IAM authentication.")
                connector = Connector(enable_iam_auth=False)

            def getconn() -> Any:
                # Hàm này giờ đây sẽ hoạt động nhất quán trên cả hai môi trường
                return connector.connect(
                    INSTANCE_CONNECTION_NAME, "pg8000",
                    user=DB_USER, password=DB_PASS, db=DB_NAME,
                    ip_type=IPTypes.PUBLIC
                )

            db_engine = sqlalchemy.create_engine(
                "postgresql+pg8000://",
                creator=getconn,
                pool_size=5, max_overflow=2, pool_timeout=30, pool_recycle=1800,
            )
            logger.info("Database engine initialized successfully.")
        except Exception as e:
            logger.critical(f"FATAL: Could not initialize database engine: {e}")
            raise
    return db_engine

# =================================================================================
#  3. UTILITY FUNCTIONS
# =================================================================================

def default_json_serializer(obj):
    """
    Hàm tùy chỉnh để chuyển đổi các kiểu dữ liệu không-JSON-serializable,
    bao gồm cả datetime, UUID, và Decimal.
    """
    if isinstance(obj, datetime):
        # Chuyển đổi datetime thành chuỗi theo định dạng ISO 8601,
        # đây là một tiêu chuẩn phổ biến cho các API.
        return obj.isoformat()
    if isinstance(obj, (uuid.UUID, Decimal)):
        return str(obj)
    
    # Nếu không phải là các kiểu trên, báo lỗi như bình thường.
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# =================================================================================
#  4. API ENDPOINTS
# =================================================================================

@https_fn.on_request(cors=CORS_CONFIG)
def create_listing(req: https_fn.Request) -> https_fn.Response:
    """API Endpoint để tạo một tin đăng mới."""
    if req.method != "POST":
        return https_fn.Response(f"Method {req.method} not allowed.", status=405)

    try:
        engine = get_db_engine()
        data = req.get_json(silent=True)
        if not data: return https_fn.Response("Invalid JSON payload.", status=400)

        listing_data = data.get("listing")
        attributes_data = data.get("attributes", []) # Mặc định là list rỗng
        
        if not listing_data:
            return https_fn.Response("Missing 'listing' data.", status=400)

        with engine.connect() as conn:
            with conn.begin() as tx:
                result = conn.execute(
                    sqlalchemy.text("""
                        INSERT INTO listings (title, description, price_monthly_vnd, area_m2, address_ward, address_district, source_url)
                        VALUES (:title, :desc, :price, :area, :ward, :district, :source) RETURNING id
                    """),
                    {
                        "title": listing_data.get("title"), "desc": listing_data.get("description"),
                        "price": listing_data.get("price_monthly_vnd"), "area": listing_data.get("area_m2"),
                        "ward": listing_data.get("address_ward"), "district": listing_data.get("address_district"),
                        "source": f"manual-entry-{os.urandom(4).hex()}"
                    }
                )
                new_listing_id = result.scalar_one()

                if attributes_data:
                    attrs_to_insert = [
                        {
                            "listing_id": new_listing_id,
                            "attribute_id": attr.get("attribute_id"),
                            "value_boolean": attr.get("value") if isinstance(attr.get("value"), bool) else None,
                            "value_integer": attr.get("value") if isinstance(attr.get("value"), int) else None,
                            "value_string": str(attr.get("value")) if not isinstance(attr.get("value"), (bool, int)) else None,
                        }
                        for attr in attributes_data
                    ]
                    conn.execute(sqlalchemy.text("""
                        INSERT INTO listing_attributes (listing_id, attribute_id, value_boolean, value_integer, value_string)
                        VALUES (:listing_id, :attribute_id, :value_boolean, :value_integer, :value_string)
                    """), attrs_to_insert)
                
                tx.commit()
        
        response_data = {"message": "Listing created successfully", "id": str(new_listing_id)}
        return https_fn.Response(json.dumps(response_data), status=201, headers={"Content-Type": "application/json"})

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
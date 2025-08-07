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

IS_EMULATOR = os.environ.get("FUNCTIONS_EMULATOR") == "true"

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

# =================================================================================
#  3. UTILITY FUNCTIONS
# =================================================================================

def default_json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default."""
    if isinstance(obj, (datetime, uuid.UUID)):
        return str(obj)
    # *** THÊM LOGIC XỬ LÝ DECIMAL VÀO ĐÂY ***
    if isinstance(obj, Decimal):
        # Chuyển đổi Decimal thành float hoặc string. Float là lựa chọn phổ biến
        # cho JSON, nhưng string an toàn hơn nếu cần độ chính xác tuyệt đối.
        # Ở đây, float là đủ tốt cho diện tích.
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
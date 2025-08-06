import os
from typing import Any, Dict, List

from firebase_functions import https_fn, options
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
import json

# =================================================================================
#  GLOBAL SETUP (Synchronous)
# =================================================================================
options.set_global_options(region="asia-southeast1", max_instances=5)

INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")

# Biến toàn cục cho SQLAlchemy Engine (quản lý pool kết nối)
db_engine: sqlalchemy.engine.Engine = None

def init_db_engine() -> sqlalchemy.engine.Engine:
    """Khởi tạo SQLAlchemy Engine, quản lý pool kết nối một cách an toàn."""
    connector = Connector()
    
    def getconn() -> Any:
        # Hàm này trả về một kết nối DB thô
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
            ip_type=IPTypes.PUBLIC,
        )
        return conn

    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return engine

# =================================================================================
#  API ENDPOINT (Synchronous)
# =================================================================================

frontend_url="https://5173-firebase-nhaminhbach-1754197535766.cluster-ikxjzjhlifcwuroomfkjrx437g.cloudworkstations.dev"


@https_fn.on_request(cors=options.CorsOptions(cors_origins=[frontend_url, "http://localhost:5173"], cors_methods=["get", "post"]))
def create_listing(req: https_fn.Request) -> https_fn.Response:
    """
    API Endpoint ĐỒNG BỘ để tạo một tin đăng mới.
    Không còn async/await, không còn coroutine.
    """
    global db_engine

    # Khởi tạo engine nếu chưa có
    if db_engine is None:
        try:
            db_engine = init_db_engine()
        except Exception as e:
            print(f"FATAL: Could not initialize database engine: {e}")
            return https_fn.Response("Internal Server Error: DB connection failed.", status=500)

    if req.method != "POST":
        return https_fn.Response(f"Method {req.method} not allowed.", status=405)

    try:
        data = req.get_json(silent=True)
        if not data: return https_fn.Response("Invalid JSON payload.", status=400)

        listing_data = data.get("listing")
        attributes_data = data.get("attributes")
        if not listing_data or not isinstance(attributes_data, list):
            return https_fn.Response("Missing or malformed data.", status=400)

        # Sử dụng 'with' để tự động quản lý kết nối và transaction
        with db_engine.connect() as conn:
            with conn.begin() as tx: # Bắt đầu transaction
                try:
                    # 1. Chèn vào bảng 'listings'
                    result = conn.execute(
                        sqlalchemy.text("""
                            INSERT INTO listings (title, description, price_monthly_vnd, area_m2, address_ward, address_district, source_url)
                            VALUES (:title, :desc, :price, :area, :ward, :district, :source)
                            RETURNING id
                        """),
                        {
                            "title": listing_data.get("title"), "desc": listing_data.get("description"),
                            "price": listing_data.get("price_monthly_vnd"), "area": listing_data.get("area_m2"),
                            "ward": listing_data.get("address_ward"), "district": listing_data.get("address_district"),
                            "source": f"manual-test-{os.urandom(4).hex()}"
                        }
                    )
                    new_listing_id = result.scalar_one()

                    # 2. Chèn vào bảng 'listing_attributes'
                    if attributes_data:
                        attrs_to_insert = []
                        for attr in attributes_data:
                            # === THAY THẾ BẮT ĐẦU TỪ ĐÂY ===
                            
                            # Khởi tạo tất cả các giá trị là None
                            value_bool, value_int, value_str = None, None, None
                            
                            # Lấy giá trị từ request
                            current_value = attr.get("value")

                            # Phân loại và gán vào đúng cột
                            if isinstance(current_value, bool):
                                value_bool = current_value
                            elif isinstance(current_value, int):
                                value_int = current_value
                            else:
                                # Bất cứ thứ gì khác đều được coi là string
                                value_str = str(current_value)

                            # Thêm vào danh sách để chèn
                            attrs_to_insert.append({
                                "listing_id": new_listing_id,
                                "attribute_id": attr.get("attribute_id"),
                                "value_boolean": value_bool,
                                "value_integer": value_int,
                                "value_string": value_str,
                            })
                            # === KẾT THÚC THAY THẾ ===
                        
                        if attrs_to_insert:
                            conn.execute(sqlalchemy.text("""
                                INSERT INTO listing_attributes (listing_id, attribute_id, value_boolean, value_integer, value_string)
                                VALUES (:listing_id, :attribute_id, :value_boolean, :value_integer, :value_string)
                            """), attrs_to_insert)
                    
                    tx.commit() # Hoàn thành transaction
                except Exception:
                    tx.rollback() # Nếu có lỗi, hủy bỏ tất cả
                    raise
        
        return https_fn.Response(
            f'{{"message": "Listing created successfully", "id": "{new_listing_id}"}}',
            status=201, headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        print(f"An error occurred during request processing: {e}")
        return https_fn.Response("An internal server error occurred.", status=500)

# Hàm này sẽ giúp chúng ta chuyển đổi các kiểu dữ liệu từ DB một cách an toàn
def alchemy_row_to_dict(row):
    d = dict(row._mapping)
    # Chuyển đổi các kiểu dữ liệu không phải là JSON serializable
    for key, value in d.items():
        if isinstance(value, (Decimal, uuid.UUID)):
            d[key] = str(value)
    return d

@https_fn.on_request(cors=options.CorsOptions(cors_origins=["*"], cors_methods=["get"]))
def get_listings(req: https_fn.Request) -> https_fn.Response:
    """
    API Endpoint TỐI ƯU để lấy tất cả các tin đăng 'available'.
    Sử dụng một truy vấn JOIN duy nhất và trả về JSON hợp lệ.
    """
    global db_engine
    if db_engine is None:
        try: db_engine = init_db_engine()
        except Exception as e:
            print(f"FATAL: Could not initialize database engine: {e}")
            return https_fn.Response("Internal Server Error: DB connection failed.", status=500)

    if req.method != "GET":
        return https_fn.Response(f"Method {req.method} not allowed.", status=405)

    # Câu lệnh SQL với JOIN và tập hợp thuộc tính bằng JSON
    # Đây là một kỹ thuật cực kỳ mạnh mẽ của PostgreSQL
    sql_query = sqlalchemy.text("""
        SELECT
            l.*,
            (
                SELECT json_agg(json_build_object(
                    'name', a.name,
                    'value', COALESCE(
                        la.value_boolean::text, -- Ép kiểu boolean thành text
                        la.value_integer::text, -- Đã là text
                        la.value_string         -- Đã là text
                    )
                ))
                FROM listing_attributes la
                JOIN attributes a ON la.attribute_id = a.id
                WHERE la.listing_id = l.id
            ) as attributes
        FROM listings l
        WHERE l.status = 'available'
    """)

    try:
        with db_engine.connect() as conn:
            result = conn.execute(sql_query).fetchall()
            
            # Chuyển đổi kết quả (Row objects) thành một danh sách các dict
            listings_data = [dict(row._mapping) for row in result]

            # Chuyển đổi danh sách Python thành một chuỗi JSON hợp lệ
            json_response = json.dumps(listings_data, default=str) # default=str để xử lý UUID, Decimal...

        return https_fn.Response(
            json_response,
            status=200,
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        print(f"An error occurred during listing retrieval: {e}")
        return https_fn.Response("An internal server error occurred.", status=500)
"""
GeoID System Utilities for NhaMinhBach
======================================
Implements Base36 ID generation, fingerprinting, and house/room management.

Format: 29CG.HHHRR
- 29: City code (Hà Nội)
- CG: District code (2 chars)
- HHH: House ID (3 chars Base36, expandable)
- RR: Room ID (2 chars Base36, 00=whole house)

Author: CTO Alex + AI Agent
Date: 2025-12-01
"""

import hashlib
import string
import re
from typing import Tuple, Optional, Dict
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

# Base36 alphabet: 0-9, A-Z
BASE36 = string.digits + string.ascii_uppercase

# Ward code mapping (Hà Nội - Complete list)
WARD_CODES = {
    "An Khánh": "AK", "Bất Bạt": "BB", "Ba Đình": "BD", "Bình Minh": "BI", "Bạch Mai": "BM",
    "Bồ Đề": "BO", "Bát Tràng": "BT", "Ba Vì": "BV", "Chương Dương": "CD", "Cầu Giấy": "CG",
    "Chương Mỹ": "CM", "Cửa Nam": "CN", "Cổ Đô": "CO", "Chuyên Mỹ": "CY", "Đông Anh": "DA",
    "Định Công": "DC", "Đống Đa": "DD", "Đa Phúc": "DF", "Đoài Phương": "DG", "Dân Hòa": "DH",
    "Dương Nội": "DI", "Đông Ngạc": "DN", "Đại Mỗ": "DO", "Đan Phượng": "DP", "Đại Thanh": "DT",
    "Dương Hòa": "DU", "Đại Xuyên": "DX", "Phúc Thọ": "FT", "Gia Lâm": "GL", "Giảng Võ": "GV",
    "Hát Môn": "HA", "Hạ Bằng": "HB", "Hà Đông": "HD", "Hồng Hà": "HH", "Hoàng Liệt": "HI",
    "Hoàn Kiếm": "HK", "Hòa Lạc": "HL", "Hoàng Mai": "HM", "Hồng Sơn": "HN", "Hưng Đạo": "HO",
    "Hòa Phú": "HP", "Hương Sơn": "HS", "Hai Bà Trưng": "HT", "Hoài Đức": "HU", "Hồng Vân": "HV",
    "Hòa Xá": "HX", "Kim Anh": "KA", "Khương Đình": "KD", "Kiến Hưng": "KH", "Kim Liên": "KL",
    "Kiều Phú": "KP", "Láng": "LA", "Long Biên": "LB", "Liên Minh": "LM", "Lĩnh Nam": "LN",
    "Minh Châu": "MC", "Mỹ Đức": "MD", "Mê Linh": "ML", "Ngọc Hà": "NA", "Nội Bài": "NB",
    "Nghĩa Đô": "ND", "Ngọc Hồi": "NH", "Nam Phù": "NP", "Ô Chợ Dừa": "OC", "Ô Diên": "OD",
    "Phú Cát": "PC", "Phù Đổng": "PD", "Phú Diễn": "PE", "Phú Lương": "PG", "Phúc Thịnh": "PH",
    "Phúc Lợi": "PI", "Phương Liệt": "PL", "Phú Nghĩa": "PN", "Phúc Lộc": "PO", "Phúc Sơn": "PS",
    "Phú Thượng": "PT", "Phượng Dực": "PU", "Phú Xuyên": "PX", "Quảng Oai": "QA", "Quảng Bị": "QB",
    "Quang Minh": "QM", "Quốc Oai": "QO", "Sơn Đồng": "SD", "Suối Hai": "SH", "Sóc Sơn": "SS",
    "Sơn Tây": "ST", "Thuận An": "TA", "Tùng Thiện": "TB", "Thượng Cát": "TC", "Thiên Lộc": "TD",
    "Từ Liêm": "TL", "Tây Phương": "TF", "Tiến Thắng": "TG", "Tây Hồ": "TH", "Thanh Liệt": "TI",
    "Thượng Phúc": "TK", "Thư Lâm": "TJ", "Tương Mai": "TM", "Tam Hưng": "TN", "Thanh Oai": "TO",
    "Trần Phú": "TP", "Trung Giã": "TR", "Thạch Thất": "TS", "Thanh Trì": "TT", "Thường Tín": "TU",
    "Tây Tựu": "TV", "Thanh Xuân": "TX", "Tây Mỗ": "TY", "Ứng Hòa": "UH", "Ứng Thiên": "UT",
    "Vĩnh Thanh": "VA", "Vân Đình": "VD", "Vĩnh Hưng": "VH", "Việt Hưng": "VE", "Vật Lại": "VL",
    "Văn Miếu - Quốc Tử Giám": "VM", "Vĩnh Tuy": "VT", "Xuân Đỉnh": "XD", "Xuân Mai": "XM",
    "Xuân Phương": "XP", "Yên Bài": "YB", "Yên Hòa": "YH", "Yên Lãng": "YL", "Yên Nghĩa": "YN",
    "Yên Sở": "YS", "Yên Xuân": "YX",
}

# Reverse mapping
CODE_TO_WARD = {v: k for k, v in WARD_CODES.items()}


# =========================================================================
# BASE36 CONVERSION
# =========================================================================

def to_base36(num: int, width: int = 3) -> str:
    """
    Convert integer to Base36 string with zero-padding.
    
    Args:
        num: Integer to convert (0 to 36^width - 1)
        width: Output string width (default 3 for house IDs)
    
    Returns:
        Base36 string, e.g., to_base36(10, 3) → "00A"
    
    Examples:
        >>> to_base36(0, 3)
        '000'
        >>> to_base36(10, 3)
        '00A'
        >>> to_base36(36, 3)
        '010'
        >>> to_base36(1295, 3)
        'ZZZ'
    """
    if num == 0:
        return '0' * width
    
    if num < 0:
        raise ValueError(f"Cannot convert negative number {num} to Base36")
    
    max_val = 36 ** width - 1
    if num > max_val:
        raise ValueError(f"Number {num} exceeds max value {max_val} for width {width}")
    
    result = ''
    while num:
        result = BASE36[num % 36] + result
        num //= 36
    
    return result.zfill(width)


def from_base36(s: str) -> int:
    """
    Convert Base36 string to integer.
    
    Args:
        s: Base36 string (e.g., "00A", "ZZZ")
    
    Returns:
        Integer value
    
    Examples:
        >>> from_base36("00A")
        10
        >>> from_base36("ZZZ")
        46655
    """
    return int(s.upper(), 36)


def format_geoid_display(full_geoid: str) -> str:
    """
    Format GeoID for display with elastic padding removal.
    
    Args:
        full_geoid: Full GeoID like "29CG.0AB01"
    
    Returns:
        Compressed display format like "29CGAB1"
    
    Examples:
        >>> format_geoid_display("29CG.0AB01")
        '29CGAB1'
        >>> format_geoid_display("29CG.00A0R")
        '29CGA.R'
        >>> format_geoid_display("29CG.W8K00")
        '29CGW8K'
    """
    # Parse: 29CG.HHHRR
    match = re.match(r'(\d{2})([A-Z]{2})\.([0-9A-Z]{3})([0-9A-Z]{2})', full_geoid.upper())
    if not match:
        return full_geoid  # Return as-is if format doesn't match
    
    city, district, house, room = match.groups()
    
    # Remove leading zeros from house
    house_compact = house.lstrip('0') or '0'
    
    # Remove leading zeros from room
    room_compact = room.lstrip('0') or '0'
    
    # Special case: room=00 means whole house, omit it
    if room == '00':
        return f"{city}{district}{house_compact}"
    
    # If both are single char and at least one is alpha, keep separator for clarity
    # Example: 29CGA.R (house=A, room=R) is clearer than 29CGAR
    if len(house_compact) == 1 and len(room_compact) == 1:
        # Only use separator if at least one is non-numeric (to avoid ambiguity)
        if not (house_compact.isdigit() and room_compact.isdigit()):
            return f"{city}{district}{house_compact}.{room_compact}"
    
    # Otherwise concatenate
    return f"{city}{district}{house_compact}{room_compact}"


# =========================================================================
# FINGERPRINTING FOR DEDUPLICATION
# =========================================================================

def normalize_text(text: str) -> str:
    """
    Normalize Vietnamese text for consistent hashing.
    
    - Lowercase
    - Strip whitespace
    - Remove Vietnamese diacritics
    - Remove punctuation
    - Keep only alphanumeric + space
    """
    if not text:
        return ""
    
    text = text.lower().strip()
    
    # Remove Vietnamese diacritics (basic mapping)
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
    }
    
    for vn_char, ascii_char in vietnamese_map.items():
        text = text.replace(vn_char, ascii_char)
    
    # Remove remaining non-alphanumeric characters except spaces
    text = re.sub(r'[^\w\s]', '', text)
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_address_fingerprint(
    city: str,
    ward: str,
    street: str,
    house_number: Optional[str] = None
) -> Optional[str]:
    """
    Generate address fingerprint for deduplication.
    
    Priority 1: Full address with house number
    Hash of: city|ward|street|house_number
    
    Args:
        city: City name (e.g., "Hà Nội")
        ward: Ward name (e.g., "Dịch Vọng")
        street: Street name (e.g., "Phạm Hùng")
        house_number: Optional house number (e.g., "123", "45A")
    
    Returns:
        SHA256 hash string or None if insufficient data
    """
    # Need at least city, ward, street
    if not all([city, ward, street]):
        return None
    
    # Normalize all components
    parts = [
        normalize_text(city),
        normalize_text(ward),
        normalize_text(street),
    ]
    
    if house_number:
        parts.append(normalize_text(house_number))
    
    # Create fingerprint
    fingerprint_str = "|".join(parts)
    return hashlib.sha256(fingerprint_str.encode('utf-8')).hexdigest()


def generate_phone_fingerprint(
    phone: str,
    street: str
) -> Optional[str]:
    """
    Generate phone-based fingerprint for anonymous posts.
    
    Priority 2: Phone + Street (when full address not available)
    Hash of: phone|street
    
    Args:
        phone: Contact phone number
        street: Street name
    
    Returns:
        SHA256 hash string or None if insufficient data
    """
    if not phone or not street:
        return None
    
    # Normalize phone (remove spaces, dashes)
    phone_clean = re.sub(r'[^\d]', '', phone)
    street_clean = normalize_text(street)
    
    fingerprint_str = f"{phone_clean}|{street_clean}"
    return hashlib.sha256(fingerprint_str.encode('utf-8')).hexdigest()


# =========================================================================
# WARD CODE UTILITIES
# =========================================================================

def get_ward_code(ward_name: str) -> Optional[str]:
    """
    Get 2-char ward code from full ward name.
    
    Args:
        ward_name: Full ward name (e.g., "Cầu Giấy", "Phường Cầu Giấy")
    
    Returns:
        2-char code (e.g., "CG") or None if not found
    
    Examples:
        >>> get_ward_code("Cầu Giấy")
        'CG'
        >>> get_ward_code("Phường Cầu Giấy")
        'CG'
        >>> get_ward_code("Đống Đa")
        'DD'
    """
    if not ward_name:
        return None
    
    # Normalize: remove "Phường" / "Xã" / "Thị trấn" prefix if present
    ward_clean = ward_name.strip()
    ward_clean = re.sub(r'^(Phường|Xã|Thị trấn)\s+', '', ward_clean, flags=re.IGNORECASE)
    
    return WARD_CODES.get(ward_clean)


def get_ward_name(ward_code: str) -> Optional[str]:
    """
    Get full ward name from 2-char code.
    
    Args:
        ward_code: 2-char code (e.g., "CG")
    
    Returns:
        Full ward name (e.g., "Cầu Giấy") or None if not found
    """
    return CODE_TO_WARD.get(ward_code.upper())


# =========================================================================
# HOUSE & ROOM MANAGEMENT
# =========================================================================

def find_house_by_fingerprint(
    conn,
    address_hash: Optional[str] = None,
    phone_hash: Optional[str] = None
) -> Optional[int]:
    """
    Find existing house by fingerprint.
    
    Args:
        conn: SQLAlchemy connection
        address_hash: Address fingerprint
        phone_hash: Phone fingerprint
    
    Returns:
        house_id (integer) or None if not found
    """
    if address_hash:
        result = conn.execute(
            text("SELECT id FROM houses WHERE address_hash = :hash LIMIT 1"),
            {"hash": address_hash}
        ).fetchone()
        if result:
            logger.info(f"Found existing house by address_hash: {result[0]}")
            return result[0]
    
    if phone_hash:
        result = conn.execute(
            text("SELECT id FROM houses WHERE phone_hash = :hash LIMIT 1"),
            {"hash": phone_hash}
        ).fetchone()
        if result:
            logger.info(f"Found existing house by phone_hash: {result[0]}")
            return result[0]
    
    return None


def create_house(
    conn,
    ward_code: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    address_street: Optional[str] = None,
    address_ward: Optional[str] = None,
    address_district: Optional[str] = None,
    address_hash: Optional[str] = None,
    phone_hash: Optional[str] = None,
    accuracy_level: int = 2
) -> Tuple[int, str]:
    """
    Create new house with next available HHH ID.
    
    Args:
        conn: SQLAlchemy connection
        ward_code: 2-char ward code (e.g., "CG")
        latitude: Optional latitude
        longitude: Optional longitude
        address_street: Street name
        address_ward: Ward name
        address_district: District name (deprecated, kept for migration)
        address_hash: Precomputed address fingerprint
        phone_hash: Precomputed phone fingerprint
        accuracy_level: 1=Verified, 2=Fuzzy (default)
    
    Returns:
        Tuple of (house_id, full_geo_id)
        Example: (123, "29CG.0AB")
    """
    # Allocate next available HHH (3-char Base36) with retry to avoid race collisions
    base_count = conn.execute(
        text("SELECT COUNT(*) FROM houses WHERE ward_code = :ward"),
        {"ward": ward_code}
    ).scalar()

    max_attempts = 16  # allows quick fallback through next 16 slots
    attempt = 0
    last_error: Optional[Exception] = None

    while attempt < max_attempts:
        geo_id = to_base36(base_count + attempt, 3)
        logger.info(f"Creating new house: ward={ward_code}, geo_id={geo_id} (attempt {attempt+1})")
        try:
            result = conn.execute(
                text("""
                    INSERT INTO houses 
                    (geo_id, ward_code, latitude, longitude, 
                     address_street, address_ward, address_district,
                     address_hash, phone_hash, accuracy_level)
                    VALUES (:geo_id, :ward, :lat, :lng, :street, :ward_name, :district_name, :addr_hash, :phone_hash, :accuracy)
                    RETURNING id, full_geo_id
                """),
                {
                    "geo_id": geo_id,
                    "ward": ward_code,
                    "lat": latitude,
                    "lng": longitude,
                    "street": address_street,
                    "ward_name": address_ward,
                    "district_name": address_district,
                    "addr_hash": address_hash,
                    "phone_hash": phone_hash,
                    "accuracy": accuracy_level
                }
            )
            row = result.fetchone()
            house_id = row[0]
            full_geo_id = row[1]
            logger.info(f"Created house: id={house_id}, full_geo_id={full_geo_id}")
            return house_id, full_geo_id
        except IntegrityError as e:
            # Likely duplicate (ward_code, geo_id) due to concurrent insert. Try next slot.
            logger.warning(f"GeoID collision for {ward_code}.{geo_id}, retrying with next slot... ({e.__class__.__name__})")
            last_error = e
            attempt += 1
            continue

    # Exhausted attempts
    raise RuntimeError(f"Failed to allocate unique house geo_id in ward {ward_code} after {max_attempts} attempts") from last_error


def find_or_create_house(
    conn,
    ward_code: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    address_street: Optional[str] = None,
    address_ward: Optional[str] = None,
    address_district: Optional[str] = None,
    contact_phone: Optional[str] = None,
    accuracy_level: int = 2
) -> Tuple[int, str, bool]:
    """
    Find existing house or create new one with fingerprinting.
    
    Args:
        conn: SQLAlchemy connection
        ward_code: 2-char ward code
        latitude: Optional latitude
        longitude: Optional longitude
        address_street: Street name
        address_ward: Ward name
        address_district: District name (deprecated, kept for migration)
        contact_phone: Contact phone for fingerprinting
        accuracy_level: 1=Verified, 2=Fuzzy
    
    Returns:
        Tuple of (house_id, full_geo_id, created)
        - created: True if new house was created, False if existing found
    """
    # Generate fingerprints
    addr_hash = generate_address_fingerprint(
        city="Hà Nội",
        ward=address_ward or "",
        street=address_street or "",
        house_number=None  # TODO: Extract from street if available
    )
    
    phone_hash = generate_phone_fingerprint(
        phone=contact_phone or "",
        street=address_street or ""
    )
    
    # Try to find existing house
    existing_house_id = find_house_by_fingerprint(conn, addr_hash, phone_hash)
    
    if existing_house_id:
        # Get full_geo_id of existing house
        result = conn.execute(
            text("SELECT full_geo_id FROM houses WHERE id = :house_id"),
            {"house_id": existing_house_id}
        ).fetchone()
        full_geo_id = result[0]
        logger.info(f"Using existing house: id={existing_house_id}, geo_id={full_geo_id}")
        return existing_house_id, full_geo_id, False
    
    # Create new house
    house_id, full_geo_id = create_house(
        conn=conn,
        ward_code=ward_code,
        latitude=latitude,
        longitude=longitude,
        address_street=address_street,
        address_ward=address_ward,
        address_district=address_district,
        address_hash=addr_hash,
        phone_hash=phone_hash,
        accuracy_level=accuracy_level
    )
    
    return house_id, full_geo_id, True


def create_room(
    conn,
    house_id: int,
    room_number: Optional[str] = None,
    status: str = 'pending_review'
) -> Tuple[int, str]:
    """
    Create new room under a house.
    
    Args:
        conn: SQLAlchemy connection
        house_id: Parent house ID
        room_number: Optional room number (e.g., "301", "A12", "P2")
        status: Initial status (default: 'pending_review')
    
    Returns:
        Tuple of (room_id, full_geo_id)
        Example: (456, "29CG.0AB01")
    """
    # Count existing rooms for this house
    room_count = conn.execute(
        text("SELECT COUNT(*) FROM rooms WHERE house_id = :house_id"),
        {"house_id": house_id}
    ).scalar()
    
    # Generate room_id (RR portion)
    if room_number:
        # Try to extract numeric part from room number
        # Examples: "301" → 301, "P12" → 12, "A5" → 5
        numeric_part = re.search(r'\d+', room_number)
        if numeric_part:
            room_num = int(numeric_part.group())
            room_id = to_base36(room_num, 2)
        else:
            # Fallback: use room count
            room_id = to_base36(room_count + 1, 2)
    else:
        # Default: 00 for first room (whole house), then 01, 02, ...
        room_id = "00" if room_count == 0 else to_base36(room_count, 2)
    
    logger.info(f"Creating room: house_id={house_id}, room_id={room_id}")
    
    # Insert room
    result = conn.execute(
        text("""
            INSERT INTO rooms (house_id, room_id, current_status)
            VALUES (:house_id, :room_id, :status)
            RETURNING id, full_geo_id
        """),
        {"house_id": house_id, "room_id": room_id, "status": status}
    )
    
    row = result.fetchone()
    db_room_id = row[0]
    full_geo_id = row[1]
    
    logger.info(f"Created room: id={db_room_id}, full_geo_id={full_geo_id}")
    return db_room_id, full_geo_id


def create_room_history(
    conn,
    room_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    price_monthly_vnd: Optional[int] = None,
    area_m2: Optional[float] = None,
    contact_phone: Optional[str] = None,
    image_urls: Optional[list] = None,
    source_url: Optional[str] = None,
    attributes: Optional[dict] = None,
    status: str = 'pending_review',
    is_current: bool = True
) -> int:
    """
    Create new room_history entry (snapshot).
    
    Args:
        conn: SQLAlchemy connection
        room_id: Foreign key to rooms table
        title: Listing title
        description: Listing description
        price_monthly_vnd: Monthly rent in VND
        area_m2: Area in square meters
        contact_phone: Contact phone
        image_urls: List of image URLs
        source_url: Original post URL
        attributes: Dict of amenities (will be stored as JSONB)
        status: Listing status
        is_current: True if this is the active version
    
    Returns:
        room_history.id (integer)
    """
    import json
    
    logger.info(f"Creating room_history: room_id={room_id}, status={status}, is_current={is_current}")
    
    result = conn.execute(
        text("""
            INSERT INTO room_history 
            (room_id, title, description, price_monthly_vnd, area_m2,
             contact_phone, image_urls, source_url, attributes, status, is_current)
            VALUES (:room_id, :title, :description, :price, :area,
                    :phone, :images, :source, :attrs::jsonb, :status, :is_current)
            RETURNING id
        """),
        {
            "room_id": room_id,
            "title": title,
            "description": description,
            "price": price_monthly_vnd,
            "area": area_m2,
            "phone": contact_phone,
            "images": image_urls or [],
            "source": source_url,
            "attrs": json.dumps(attributes or {}),
            "status": status,
            "is_current": is_current
        }
    )
    
    history_id = result.scalar()
    logger.info(f"Created room_history: id={history_id}")
    return history_id

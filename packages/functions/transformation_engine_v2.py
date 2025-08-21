"""
Core LLM Transformation Logic for NhaMinhBach

This module implements the central transformation pipeline that converts raw scraped
Facebook posts into structured rental listing data using Gemma LLM for 
validated output.

Key Features:
- Dynamic attribute mapping from database schema
- Vietnamese rental property text analysis
- Robust validation and error handling
- Batch processing capabilities

Author: CTO Alex
Created: 2025-08-19
Task: 25081914_build_core_transformation_logic
"""

import os
import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from google import genai
from google.genai import types
from pydantic import ValidationError

from data_contracts import (
    TransformationInput,
    TransformationOutput,
    Listing,
    ExtractedAttribute,
    validate_transformation_output
)

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

# Vertex AI Gemini model configuration - Updated to recommended Google Gen AI SDK
GEMINI_MODEL = "gemini-2.5-flash-lite"

# =============================================================================
# DYNAMIC ATTRIBUTE SYSTEM
# =============================================================================

def get_available_attributes(engine=None) -> Dict[str, Dict[str, Any]]:
    """
    Fetch available attributes from the database dynamically.
    
    Args:
        engine: Optional SQLAlchemy engine. If None, will create one.
        
    Returns:
        Dict[slug, attribute_info]: Mapping of attribute slugs to their definitions
    """
    if engine is None:
        from main import get_db_engine
        engine = get_db_engine()
    
    import sqlalchemy
    
    attribute_map = {}
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                sqlalchemy.text("SELECT id, type, name, slug, possible_values FROM attributes ORDER BY id")
            ).fetchall()
            
            for row in result:
                attribute_map[row.slug] = {
                    "id": row.id,
                    "type": row.type,
                    "name": row.name,
                    "slug": row.slug,
                    "possible_values": row.possible_values
                }
                
    except Exception as e:
        logger.error(f"Failed to fetch attributes from database: {e}")
        # Fallback to common Vietnamese rental attributes
        return get_fallback_attributes()
    
    return attribute_map


def get_fallback_attributes() -> Dict[str, Dict[str, Any]]:
    """
    Fallback attributes when database is unavailable.
    These represent common Vietnamese rental property attributes.
    
    Returns:
        Dict[slug, attribute_info]: Fallback attribute definitions
    """
    return {
        "air_conditioner": {"type": "boolean", "name": "Điều hòa", "slug": "air_conditioner"},
        "washing_machine": {"type": "boolean", "name": "Máy giặt", "slug": "washing_machine"},
        "refrigerator": {"type": "boolean", "name": "Tủ lạnh", "slug": "refrigerator"},
        "water_heater": {"type": "boolean", "name": "Nóng lạnh", "slug": "water_heater"},
        "wifi": {"type": "boolean", "name": "WiFi", "slug": "wifi"},
        "parking": {"type": "boolean", "name": "Chỗ để xe", "slug": "parking"},
        "furnished": {"type": "boolean", "name": "Nội thất", "slug": "furnished"},
        "pet_allowed": {"type": "boolean", "name": "Cho phép thú cưng", "slug": "pet_allowed"},
        "cooking_allowed": {"type": "boolean", "name": "Cho phép nấu ăn", "slug": "cooking_allowed"},
        "shared_bathroom": {"type": "boolean", "name": "WC chung", "slug": "shared_bathroom"},
        "private_bathroom": {"type": "boolean", "name": "WC riêng", "slug": "private_bathroom"},
        "balcony": {"type": "boolean", "name": "Ban công", "slug": "balcony"},
        "elevator": {"type": "boolean", "name": "Thang máy", "slug": "elevator"},
        "security": {"type": "boolean", "name": "Bảo vệ", "slug": "security"},
        "near_university": {"type": "boolean", "name": "Gần trường đại học", "slug": "near_university"},
        "near_metro": {"type": "boolean", "name": "Gần tàu điện", "slug": "near_metro"}
    }


def build_dynamic_prompt(available_attributes: Dict[str, Dict[str, Any]]) -> str:
    """
    Build prompt section that describes available attributes based on database schema.
    
    Args:
        available_attributes: Current attribute definitions from database
        
    Returns:
        str: Formatted attribute description for LLM prompt
    """
    if not available_attributes:
        return "Không có thuộc tính nào được định nghĩa."
    
    attr_descriptions = []
    
    for slug, attr_info in available_attributes.items():
        attr_type = attr_info["type"]
        attr_name = attr_info["name"]
        
        if attr_type == "boolean":
            desc = f"- {slug}: {attr_name} (có/không - boolean)"
        elif attr_type == "integer":
            desc = f"- {slug}: {attr_name} (số nguyên - integer)"
        elif attr_type == "string":
            desc = f"- {slug}: {attr_name} (văn bản - string)"
        elif attr_type == "enum":
            possible_vals = attr_info.get("possible_values", [])
            vals_str = ", ".join(possible_vals) if possible_vals else "không xác định"
            desc = f"- {slug}: {attr_name} (chọn từ: {vals_str})"
        else:
            desc = f"- {slug}: {attr_name} ({attr_type})"
        
        attr_descriptions.append(desc)
    
    return "\n".join(attr_descriptions)

# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

SYSTEM_PROMPT_TEMPLATE = """Bạn là một AI chuyên gia trong việc phân tích và trích xuất thông tin từ các bài đăng cho thuê phòng trọ trên Facebook tại Việt Nam.

Nhiệm vụ của bạn là đọc văn bản từ bài đăng và trích xuất thông tin có cấu trúc theo định dạng JSON chính xác.

NGUYÊN TẮC QUAN TRỌNG:
1. Chỉ trích xuất thông tin được đề cập rõ ràng trong bài đăng
2. KHÔNG tự suy đoán hoặc bịa thông tin không có
3. Giá cả phải được quy đổi về VND (Việt Nam Đồng) nếu có đơn vị khác
4. Địa chỉ phải được chuẩn hóa theo format: phường/xã, quận/huyện
5. Số điện thoại phải bỏ dấu cách và ký tự đặc biệt
6. Diện tích phải là số thực (float), đơn vị m²

THUỘC TÍNH CÓ THỂ TRÍCH XUẤT:
{available_attributes}

Hãy phân tích cẩn thận và trả về kết quả chính xác theo cấu trúc JSON được yêu cầu.

Định dạng JSON output:
{{
  "listing": {{
    "status": "pending_review",
    "source_url": "URL của bài đăng",
    "title": "Tiêu đề phòng trọ",
    "description": "Mô tả chi tiết",
    "price_monthly_vnd": 2500000,
    "area_m2": 15.0,
    "address_ward": "Tên phường/xã",
    "address_district": "Tên quận/huyện",
    "contact_phone": "0987654321",
    "image_urls": []
  }},
  "attributes": [
    {{
      "attribute_slug": "air_conditioner",
      "value": true
    }}
  ],
  "extraction_metadata": {{
    "extraction_timestamp": "{timestamp}",
    "model_version": "gemma-3n-e4b-it"
  }}
}}"""

USER_PROMPT_TEMPLATE = """Phân tích bài đăng cho thuê phòng trọ sau và trích xuất thông tin có cấu trúc:

===BÀI ĐĂNG===
{raw_text}

===LINK NGUỒN===
{source_url}

Hãy trích xuất tất cả thông tin có thể từ bài đăng này theo định dạng JSON được yêu cầu."""

# =============================================================================
# CORE TRANSFORMATION FUNCTIONS
# =============================================================================

def initialize_gemini_client() -> genai.Client:
    """
    Initialize and configure the Gemini client using Google Gen AI SDK.
    
    Returns:
        genai.Client: Configured client for Gemini API calls
        
    Note: 
        Migrated from deprecated Vertex AI SDK to Google Gen AI SDK
        as per Google's deprecation notice (June 24, 2026).
    """
    try:
        from utils import get_secret
        project_id = os.getenv("GCP_PROJECT", "omega-sorter-467514-q6")
        api_key = get_secret(project_id, "gemini-api-key")
    except Exception as e:
        logger.warning(f"Could not get API key from Secret Manager: {e}")
        # Fallback to environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or Secret Manager")
    
    client = genai.Client(api_key=api_key)
    return client


def build_transformation_prompt(raw_text: str, source_url: str, available_attributes: Dict[str, Dict[str, Any]]) -> str:
    """
    Build the complete prompt for LLM transformation.
    
    Args:
        raw_text: Raw text content from scraped post
        source_url: Source URL of the post
        available_attributes: Current attribute definitions
        
    Returns:
        str: Complete prompt for LLM
    """
    # Build dynamic system prompt with current attributes
    attribute_descriptions = build_dynamic_prompt(available_attributes)
    timestamp = datetime.now().isoformat()
    
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        available_attributes=attribute_descriptions,
        timestamp=timestamp
    )
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        raw_text=raw_text.strip(),
        source_url=source_url.strip()
    )
    
    return f"{system_prompt}\n\n{user_prompt}"


def clean_extracted_data(listing_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and normalize extracted listing data.
    
    Args:
        listing_data: Raw extracted data from LLM
        
    Returns:
        Dict[str, Any]: Cleaned data ready for Pydantic validation
    """
    cleaned = listing_data.copy()
    
    # Ensure required fields have values
    if not cleaned.get("title"):
        cleaned["title"] = "Phòng trọ cho thuê"
    
    if not cleaned.get("description"):
        cleaned["description"] = "Thông tin chi tiết liên hệ trực tiếp"
    
    # Ensure price is reasonable
    price = cleaned.get("price_monthly_vnd", 0)
    if isinstance(price, str):
        # Try to extract number from string
        import re
        numbers = re.findall(r'\d+', price.replace(",", "").replace(".", ""))
        if numbers:
            price = int("".join(numbers))
        else:
            price = 1000000  # Default 1M VND
    
    if price < 500000:
        price = price * 1000 if price > 0 else 1000000  # Convert to VND if needed
    
    cleaned["price_monthly_vnd"] = min(price, 50000000)  # Cap at 50M VND
    
    # Ensure area is reasonable
    area = cleaned.get("area_m2")
    if area and area > 200:
        cleaned["area_m2"] = None  # Invalid area
    
    # Clean phone number
    phone = cleaned.get("contact_phone")
    if phone:
        # Remove spaces and special characters, keep only digits
        import re
        cleaned_phone = re.sub(r'[^\d]', '', str(phone))
        if len(cleaned_phone) >= 9:  # Valid Vietnamese phone number
            cleaned["contact_phone"] = cleaned_phone
        else:
            cleaned["contact_phone"] = None
    
    # Set default status
    cleaned["status"] = "pending_review"
    
    return cleaned


def transform_raw_post(
    raw_text: str, 
    source_url: str, 
    client: Optional[genai.Client] = None,
    engine=None
) -> TransformationOutput:
    """
    Transform a raw scraped post into structured listing data using Google Gen AI SDK.
    
    Args:
        raw_text: Raw text content from scraped post
        source_url: Source URL of the post
        client: Optional pre-initialized Gemini client
        engine: Optional SQLAlchemy engine for attribute lookup
        
    Returns:
        TransformationOutput: Structured and validated transformation result
        
    Raises:
        ValueError: If transformation fails or validation errors occur
        
    Note:
        Updated to use Google Gen AI SDK with gemini-2.5-flash-lite model
        for optimal cost-efficiency and Vietnamese language support.
    """
    start_time = datetime.now()
    
    try:
        # Initialize client if not provided
        if client is None:
            client = initialize_gemini_client()
        
        # Get available attributes from database
        available_attributes = get_available_attributes(engine)
        
        # Validate input
        transform_input = TransformationInput(
            raw_text=raw_text,
            source_url=source_url
        )
        
        # Build prompt
        prompt = build_transformation_prompt(raw_text, source_url, available_attributes)
        
        logger.info(f"Transforming post from {source_url}")
        logger.debug(f"Available attributes: {len(available_attributes)}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        # Call Gemini using Google Gen AI SDK
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig()
        
        # Get response from Gemini
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text
        
        logger.debug(f"Raw LLM response: {response_text}")
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        # Extract and clean listing data
        listing_data = response_json.get("listing", {})
        cleaned_listing = clean_extracted_data(listing_data)
        cleaned_listing["source_url"] = source_url
        
        # Extract attributes
        attributes_data = response_json.get("attributes", [])
        valid_attributes = []
        
        for attr_data in attributes_data:
            if isinstance(attr_data, dict) and "attribute_slug" in attr_data and "value" in attr_data:
                slug = attr_data["attribute_slug"]
                if slug in available_attributes:
                    valid_attributes.append(ExtractedAttribute(
                        attribute_slug=slug,
                        value=attr_data["value"]
                    ))
                else:
                    logger.warning(f"Unknown attribute slug '{slug}' ignored")
        
        # Create final response
        transformation_output = TransformationOutput(
            listing=Listing(**cleaned_listing),
            attributes=valid_attributes,
            extraction_metadata={
                "processing_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                "model_version": GEMINI_MODEL,
                "extraction_timestamp": datetime.now().isoformat(),
                "prompt_length": len(prompt),
                "input_text_length": len(raw_text),
                "attributes_available": len(available_attributes),
                "attributes_extracted": len(valid_attributes)
            }
        )
        
        # Final validation
        if validate_transformation_output(transformation_output):
            logger.info(f"Successfully transformed post {source_url} with {len(valid_attributes)} attributes")
            return transformation_output
        else:
            raise ValueError("Output validation failed")
            
    except ValidationError as e:
        logger.error(f"Validation error for {source_url}: {e}")
        raise ValueError(f"Transformation validation failed: {e}")
    
    except Exception as e:
        logger.error(f"Transformation error for {source_url}: {e}")
        raise ValueError(f"Transformation failed: {e}")


# =============================================================================
# ATTRIBUTE MAPPING UTILITIES
# =============================================================================

def resolve_attribute_slugs_to_ids(
    attributes: List[ExtractedAttribute], 
    available_attributes: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Resolve attribute slugs to database IDs for insertion.
    
    Args:
        attributes: List of extracted attributes with slugs
        available_attributes: Current attribute definitions from database
        
    Returns:
        List[Dict]: Attributes ready for database insertion
    """
    resolved = []
    
    for attr in attributes:
        attr_info = available_attributes.get(attr.attribute_slug)
        if not attr_info:
            logger.warning(f"Unknown attribute slug: {attr.attribute_slug}")
            continue
            
        attr_id = attr_info.get("id")
        attr_type = attr_info.get("type")
        
        if not attr_id:
            logger.warning(f"No ID found for attribute slug: {attr.attribute_slug}")
            continue
        
        # Prepare database row according to listing_attributes table schema
        attr_dict = {
            "attribute_id": attr_id,
            "value_boolean": None,
            "value_integer": None,
            "value_string": None
        }
        
        # Set appropriate value field based on attribute type and value
        value = attr.value
        
        if attr_type == "boolean" and isinstance(value, bool):
            attr_dict["value_boolean"] = value
        elif attr_type == "integer" and isinstance(value, (int, float)):
            attr_dict["value_integer"] = int(value)
        elif attr_type == "string" or attr_type == "enum":
            attr_dict["value_string"] = str(value)
        else:
            # Type mismatch - convert to string as fallback
            logger.warning(f"Type mismatch for {attr.attribute_slug}: expected {attr_type}, got {type(value)}")
            attr_dict["value_string"] = str(value)
        
        resolved.append(attr_dict)
    
    return resolved


def prepare_database_insertion_payload(
    listing: Listing,
    attributes: List[ExtractedAttribute],
    available_attributes: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Prepare complete payload for database insertion following our API structure.
    
    Args:
        listing: Validated Listing object
        attributes: List of extracted attributes
        available_attributes: Current attribute definitions from database
        
    Returns:
        Dict: Complete payload for create_listing API endpoint
    """
    # Convert listing to dict, excluding auto-generated fields
    listing_dict = listing.model_dump(exclude={"id"})
    
    # Resolve attributes to database format
    resolved_attributes = resolve_attribute_slugs_to_ids(attributes, available_attributes)
    
    # Build payload matching our API structure
    payload = {
        "listing": listing_dict,
        "attributes": resolved_attributes
    }
    
    return payload


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

__all__ = [
    'transform_raw_post',
    'resolve_attribute_slugs_to_ids',
    'prepare_database_insertion_payload',
    'initialize_gemini_client',
    'get_available_attributes',
    'get_fallback_attributes',
    'build_dynamic_prompt'
]

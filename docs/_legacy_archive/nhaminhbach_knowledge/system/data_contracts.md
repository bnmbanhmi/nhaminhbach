# Data Contracts
#system

## Overview
Data contracts define the structure and validation rules for data flowing through our LLM transformation pipeline. They ensure type safety and schema compliance between raw scraped data, LLM processing, and database storage.

## Implementation
- **Framework:** Pydantic v2 with comprehensive field validation
- **Location:** `/packages/functions/data_contracts.py`
- **Purpose:** Mirror PostgreSQL database schema exactly for reliable data transformation

## Core Models

### ListingCreate
**Purpose:** Primary data contract for creating new rental listings
**Fields:**
- `title`: TEXT - Property title/heading
- `description`: TEXT - Detailed property description  
- `price_monthly_vnd`: INTEGER - Monthly rent in Vietnamese Dong
- `area_m2`: NUMERIC - Property area in square meters
- `address_street`, `address_ward`, `address_district`: TEXT - Address components
- `latitude`, `longitude`: NUMERIC - Geographic coordinates
- `contact_phone`: TEXT - Contact information
- `image_urls`: List[str] - Array of image URLs
- `source_url`: TEXT - Original post URL (unique constraint)

### AttributeCreate
**Purpose:** Data contract for property attributes/amenities
**Fields:**
- `type`: Enum - 'boolean', 'string', 'integer', 'enum'
- `name`: TEXT - Human-readable name (e.g., "Điều hoà")
- `slug`: TEXT - Machine-readable identifier (e.g., "air_conditioner")
- `possible_values`: List[str] - Valid values for enum types

### ListingAttributeCreate
**Purpose:** Data contract linking listings to their attributes
**Fields:**
- `listing_id`: UUID - Reference to listing
- `attribute_id`: INTEGER - Reference to attribute
- `value_string`, `value_integer`, `value_boolean`: Optional fields for attribute values

## Validation Rules
- **Database Constraint Mirroring:** All Pydantic validations mirror exact PostgreSQL constraints
- **Cross-field Validation:** Complex validation rules that span multiple fields
- **Type Safety:** Strict typing prevents runtime errors during LLM transformation
- **Instructor Integration:** Models work seamlessly with Instructor library for LLM structured output

## Usage in LLM Pipeline
1. **Raw Input:** Vietnamese rental post text
2. **LLM Processing:** Gemini 2.5 Flash Lite transforms text using Instructor + Pydantic models
3. **Validation:** Pydantic validates all fields against database constraints
4. **Database Storage:** Validated data inserted into PostgreSQL tables

## Key Principles
- **Single Source of Truth:** Database schema drives Pydantic model structure
- **Zero Schema Mismatches:** Models prevent any database constraint violations
- **Vietnamese Text Support:** Specialized handling for Vietnamese rental property terminology
- **Fallback Attributes:** System gracefully handles unknown or missing attributes

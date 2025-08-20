"""
Pydantic Data Contracts for LLM Transformation Pipeline

This module defines the strict data contracts that mirror our PostgreSQL database schema.
These models serve as the blueprint for LLM output validation and ensure data integrity
throughout the transformation process.

Author: CTO Alex
Created: 2025-08-19
Task: 25081913_define_pydantic_data_contracts
"""

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal
from datetime import datetime
import uuid


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

# Status enum for listings (matches database constraint)
ListingStatus = Literal["available", "rented", "pending_review", "rejected"]

# Attribute types (matches database constraint)
AttributeType = Literal["boolean", "string", "integer", "enum"]


# =============================================================================
# CORE ENTITY MODELS
# =============================================================================

class Listing(BaseModel):
    """
    Core listing entity - mirrors the 'listings' table structure exactly.
    
    This represents a rental property listing with all required and optional fields
    that match the PostgreSQL database schema.
    """
    id: Optional[str] = Field(None, description="UUID primary key (auto-generated)")
    status: ListingStatus = Field(..., description="Current status of the listing")
    source_url: str = Field(..., description="Unique source URL (permalink)")
    title: str = Field(..., description="Property title/headline")
    description: str = Field(..., description="Detailed property description") 
    price_monthly_vnd: int = Field(..., ge=0, description="Monthly rent in VND")
    area_m2: Optional[Decimal] = Field(None, ge=0, description="Property area in square meters")
    address_street: Optional[str] = Field(None, description="Street address")
    address_ward: Optional[str] = Field(None, description="Ward/neighborhood")
    address_district: Optional[str] = Field(None, description="District")
    latitude: Optional[Decimal] = Field(None, description="GPS latitude coordinate")
    longitude: Optional[Decimal] = Field(None, description="GPS longitude coordinate")
    contact_phone: Optional[str] = Field(None, description="Contact phone number")
    image_urls: List[str] = Field(default_factory=list, description="Array of image URLs")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            Decimal: float,
            uuid.UUID: str
        }
        json_schema_extra = {
            "example": {
                "status": "pending_review",
                "source_url": "https://www.facebook.com/groups/123/posts/456",
                "title": "Phòng trọ sinh viên Cầu Giấy",
                "description": "Phòng 15m2, đầy đủ nội thất, gần trường đại học",
                "price_monthly_vnd": 2500000,
                "area_m2": 15.0,
                "address_ward": "Dịch Vọng",
                "address_district": "Cầu Giấy", 
                "contact_phone": "0987654321",
                "image_urls": ["https://example.com/image1.jpg"]
            }
        }

    @field_validator('source_url')
    @classmethod
    def validate_source_url(cls, v):
        """Ensure source_url is not empty and is a valid URL format"""
        if not v or not v.strip():
            raise ValueError('source_url cannot be empty')
        return v.strip()

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Ensure title is not empty"""
        if not v or not v.strip():
            raise ValueError('title cannot be empty')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Ensure description is not empty"""
        if not v or not v.strip():
            raise ValueError('description cannot be empty')
        return v.strip()

    @field_validator('price_monthly_vnd')
    @classmethod
    def validate_price(cls, v):
        """Ensure price is reasonable (between 500K and 50M VND)"""
        if v < 500000:
            raise ValueError('price_monthly_vnd must be at least 500,000 VND')
        if v > 50000000:
            raise ValueError('price_monthly_vnd cannot exceed 50,000,000 VND') 
        return v

    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, v):
        """Ensure all image URLs are valid HTTP(S) URLs"""
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid image URL: {url}')
        return v


class Attribute(BaseModel):
    """
    Attribute definition - mirrors the 'attributes' table structure.
    
    Defines the available attributes/amenities that can be associated with listings.
    """
    id: Optional[int] = Field(None, description="Attribute ID (auto-generated)")
    type: AttributeType = Field(..., description="Data type for this attribute")
    name: str = Field(..., description="Human-readable attribute name")
    slug: str = Field(..., description="Machine-readable attribute identifier")
    possible_values: Optional[List[str]] = Field(None, description="Valid values for enum type")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "boolean",
                "name": "Điều hoà",
                "slug": "air_conditioner",
                "possible_values": None
            }
        }

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Ensure name is not empty"""
        if not v or not v.strip():
            raise ValueError('name cannot be empty')
        return v.strip()

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Ensure slug is not empty and follows naming convention"""
        if not v or not v.strip():
            raise ValueError('slug cannot be empty')
        # Basic slug validation - alphanumeric and underscores only
        import re
        if not re.match(r'^[a-z0-9_]+$', v.strip()):
            raise ValueError('slug must contain only lowercase letters, numbers, and underscores')
        return v.strip()

    @model_validator(mode='after')
    def validate_enum_constraints(self):
        """Ensure enum type attributes have possible_values defined"""
        if self.type == 'enum' and not self.possible_values:
            raise ValueError('enum type attributes must have possible_values defined')
        if self.type != 'enum' and self.possible_values:
            raise ValueError('only enum type attributes should have possible_values')
        
        return self


class ListingAttribute(BaseModel):
    """
    Listing-Attribute association - mirrors the 'listing_attributes' table.
    
    Connects a listing to its attributes with typed values.
    """
    listing_id: str = Field(..., description="UUID of the associated listing")
    attribute_id: int = Field(..., description="ID of the associated attribute")
    value_string: Optional[str] = Field(None, description="String value for text attributes")
    value_integer: Optional[int] = Field(None, description="Integer value for numeric attributes")
    value_boolean: Optional[bool] = Field(None, description="Boolean value for yes/no attributes")

    class Config:
        json_schema_extra = {
            "example": {
                "listing_id": "123e4567-e89b-12d3-a456-426614174000",
                "attribute_id": 1,
                "value_boolean": True,
                "value_integer": None,
                "value_string": None
            }
        }

    @model_validator(mode='after')
    def validate_single_value(self):
        """Ensure exactly one value field is set"""
        value_fields = ['value_string', 'value_integer', 'value_boolean']
        set_values = [getattr(self, field) for field in value_fields if getattr(self, field) is not None]
        
        if len(set_values) != 1:
            raise ValueError('Exactly one value field must be set')
        
        return self


# =============================================================================
# TRANSFORMATION PIPELINE MODELS
# =============================================================================

class TransformationInput(BaseModel):
    """
    Input model for the LLM transformation pipeline.
    
    Represents the raw scraped data that needs to be transformed.
    """
    raw_text: str = Field(..., description="Raw text content from scraped post")
    source_url: str = Field(..., description="Source URL/permalink of the post")
    image_urls: List[str] = Field(default_factory=list, description="Associated image URLs")
    
    @field_validator('raw_text')
    @classmethod
    def validate_raw_text(cls, v):
        """Ensure raw text is not empty"""
        if not v or not v.strip():
            raise ValueError('raw_text cannot be empty')
        return v.strip()


class ExtractedAttribute(BaseModel):
    """
    Represents an extracted attribute from the LLM transformation.
    
    This is the intermediate format before database insertion.
    """
    attribute_slug: str = Field(..., description="Slug of the attribute being set")
    value: Union[str, int, bool] = Field(..., description="The extracted value")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "attribute_slug": "air_conditioner",
                "value": True,
                "confidence": 0.95
            }
        }


class TransformationOutput(BaseModel):
    """
    Complete output model for the LLM transformation pipeline.
    
    This is what the LLM must produce - a fully structured listing with attributes.
    This model will be enforced by the Instructor library.
    """
    listing: Listing = Field(..., description="The structured listing data")
    attributes: List[ExtractedAttribute] = Field(default_factory=list, description="Extracted attributes")
    extraction_metadata: Optional[dict] = Field(None, description="Metadata about the extraction process")

    class Config:
        json_schema_extra = {
            "example": {
                "listing": {
                    "status": "pending_review",
                    "source_url": "https://www.facebook.com/groups/123/posts/456",
                    "title": "Phòng trọ sinh viên Cầu Giấy 2.5tr",
                    "description": "Phòng 15m2, điều hoà, gần ĐH Quốc Gia",
                    "price_monthly_vnd": 2500000,
                    "area_m2": 15.0,
                    "address_ward": "Dịch Vọng",
                    "address_district": "Cầu Giấy",
                    "contact_phone": "0987654321",
                    "image_urls": []
                },
                "attributes": [
                    {
                        "attribute_slug": "air_conditioner", 
                        "value": True,
                        "confidence": 0.9
                    },
                    {
                        "attribute_slug": "furnished",
                        "value": True, 
                        "confidence": 0.8
                    }
                ],
                "extraction_metadata": {
                    "processing_time_ms": 1200,
                    "model_version": "gemma-3b-e4b",
                    "extraction_timestamp": "2025-08-19T10:30:00Z"
                }
            }
        }

    @model_validator(mode='after')
    def validate_listing_attributes_consistency(self):
        """Ensure listing and attributes are consistent"""
        if self.listing and self.attributes:
            # Basic consistency check - could be expanded
            if not self.listing.source_url:
                raise ValueError('listing must have source_url when attributes are provided')
        
        return self


# =============================================================================
# DATABASE INSERTION MODELS  
# =============================================================================

class DatabaseInsertionPayload(BaseModel):
    """
    Final payload for database insertion after LLM transformation.
    
    This model represents the complete data ready for insertion into PostgreSQL.
    """
    listing_data: dict = Field(..., description="Listing data for INSERT statement")
    attributes_data: List[dict] = Field(default_factory=list, description="Attributes data for batch INSERT")
    
    class Config:
        json_schema_extra = {
            "example": {
                "listing_data": {
                    "status": "pending_review",
                    "title": "Processed Title",
                    "description": "Processed Description", 
                    "price_monthly_vnd": 2500000,
                    "area_m2": 15.0,
                    "address_ward": "Dịch Vọng",
                    "address_district": "Cầu Giấy",
                    "source_url": "https://facebook.com/...",
                    "image_urls": []
                },
                "attributes_data": [
                    {
                        "attribute_id": 1,
                        "value_boolean": True,
                        "value_integer": None,
                        "value_string": None
                    }
                ]
            }
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def validate_transformation_output(output: TransformationOutput) -> bool:
    """
    Comprehensive validation of transformation output.
    
    Args:
        output: The transformation output to validate
        
    Returns:
        bool: True if valid, raises ValidationError if invalid
    """
    try:
        # The Pydantic model validation will run automatically
        # Additional business logic validation can be added here
        
        # Ensure required fields are present
        if not output.listing.title or not output.listing.description:
            raise ValueError("Listing must have title and description")
        
        if not output.listing.source_url:
            raise ValueError("Listing must have source_url")
            
        # Ensure price is reasonable
        if output.listing.price_monthly_vnd < 500000:
            raise ValueError("Price seems too low")
            
        return True
        
    except Exception as e:
        raise ValueError(f"Transformation output validation failed: {e}")


def convert_to_database_payload(output: TransformationOutput) -> DatabaseInsertionPayload:
    """
    Convert transformation output to database insertion payload.
    
    Args:
        output: Validated transformation output
        
    Returns:
        DatabaseInsertionPayload: Ready for database insertion
    """
    # Convert listing to dict for SQL insertion
    listing_dict = output.listing.dict(exclude={'id'})  # Exclude ID as it's auto-generated
    
    # Convert attributes to database format
    # Note: This would need attribute ID lookup in real implementation
    attributes_list = []
    for attr in output.attributes:
        attr_dict: dict = {
            "attribute_id": None,  # Would be resolved via slug lookup
            "value_boolean": None,
            "value_integer": None, 
            "value_string": None
        }
        
        # Set the appropriate value field based on type
        if isinstance(attr.value, bool):
            attr_dict["value_boolean"] = attr.value
        elif isinstance(attr.value, int):
            attr_dict["value_integer"] = attr.value
        else:
            attr_dict["value_string"] = str(attr.value)
            
        attributes_list.append(attr_dict)
    
    return DatabaseInsertionPayload(
        listing_data=listing_dict,
        attributes_data=attributes_list
    )


# =============================================================================
# EXPORT ALL MODELS
# =============================================================================

__all__ = [
    'Listing',
    'Attribute', 
    'ListingAttribute',
    'TransformationInput',
    'ExtractedAttribute',
    'TransformationOutput',
    'DatabaseInsertionPayload',
    'ListingStatus',
    'AttributeType',
    'validate_transformation_output',
    'convert_to_database_payload'
]

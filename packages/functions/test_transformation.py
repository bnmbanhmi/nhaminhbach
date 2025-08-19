#!/usr/bin/env python3
"""
Test script for transformation engine - validates against database schema
"""

import os
import sys
import logging
from transformation_engine import (
    get_available_attributes,
    build_dynamic_prompt
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test the transformation engine strictly against database schema"""
    
    print("🧪 Testing Transformation Engine")
    print("================================")
    
    # Test 1: Basic database connectivity and table existence
    print("\n1. Testing database connectivity and schema...")
    try:
        from main import get_db_engine
        engine = get_db_engine()
        
        # Test basic connectivity and table existence
        import sqlalchemy
        with engine.connect() as conn:
            # Test listings table exists
            try:
                conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM listings")).scalar()
                print("✅ Listings table accessible")
            except Exception as e:
                print(f"❌ Listings table issue: {e}")
                return False
            
            # Test attributes table exists and has data
            try:
                attr_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM attributes")).scalar()
                print(f"✅ Attributes table accessible ({attr_count} records)")
            except Exception as e:
                print(f"❌ Attributes table issue: {e}")
                return False
            
            # Test listing_attributes table exists
            try:
                conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM listing_attributes")).scalar()
                print("✅ Listing_attributes table accessible")
            except Exception as e:
                print(f"❌ Listing_attributes table issue: {e}")
                return False
    
    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
        return False
    
    # Test 2: Attribute system (fallback and database)
    print("\n2. Testing attribute system...")
    try:
        attributes = get_available_attributes()
        print(f"✅ Loaded {len(attributes)} attributes")
        
        # Verify attribute structure matches database schema
        for slug, info in list(attributes.items())[:3]:
            required_keys = {'type', 'name', 'slug'}
            if not required_keys.issubset(info.keys()):
                print(f"❌ Attribute {slug} missing required keys: {required_keys - info.keys()}")
                return False
        
        print("✅ Attribute structure complies with database schema")
        
    except Exception as e:
        print(f"❌ Attribute system failed: {e}")
        return False
    
    # Test 3: Data contracts validation
    print("\n3. Testing Pydantic data contracts...")
    try:
        from data_contracts import Listing, ExtractedAttribute, TransformationOutput
        
        # Test Listing model against database schema
        sample_listing = Listing(
            status="pending_review",
            source_url="https://test.com/post/123",
            title="Test Property",
            description="Test description",
            price_monthly_vnd=2000000,
            area_m2=20.5,
            address_ward="Test Ward",
            address_district="Test District"
        )
        
        print("✅ Listing model validation passed")
        
        # Test ExtractedAttribute model
        sample_attr = ExtractedAttribute(
            attribute_slug="air_conditioner",
            value=True
        )
        
        print("✅ ExtractedAttribute model validation passed")
        
        # Test TransformationOutput model
        sample_output = TransformationOutput(
            listing=sample_listing,
            attributes=[sample_attr],
            extraction_metadata={"test": "data"}
        )
        
        print("✅ TransformationOutput model validation passed")
        
    except Exception as e:
        print(f"❌ Data contracts validation failed: {e}")
        return False
    
    # Test 4: Prompt generation
    print("\n4. Testing prompt generation...")
    try:
        attributes = get_available_attributes()
        prompt_section = build_dynamic_prompt(attributes)
        
        if len(prompt_section) < 50:
            print(f"❌ Prompt too short: {len(prompt_section)} chars")
            return False
        
        print(f"✅ Dynamic prompt generated ({len(prompt_section)} characters)")
        
    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
        return False
    
    print("\n🎉 All database schema and structure tests passed!")
    print("⚠️  LLM testing skipped (requires API key configuration)")
    print("📋 Ready for integration with properly configured API keys")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Simple test for transformation engine - tests structure without database
"""

import sys
import logging
from decimal import Decimal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_contracts():
    """Test Pydantic data contracts against database schema"""
    print("🧪 Testing Data Contracts")
    print("=========================")
    
    try:
        from data_contracts import Listing, ExtractedAttribute, TransformationOutput
        
        # Test 1: Listing model - must match database schema exactly
        print("\n1. Testing Listing model...")
        sample_listing = Listing(
            status="pending_review",
            source_url="https://facebook.com/groups/test/posts/123",
            title="Phòng trọ test",
            description="Mô tả test",
            price_monthly_vnd=2000000,
            area_m2=Decimal('20.5'),
            address_ward="Phường test",
            address_district="Quận test",
            contact_phone="0987654321"
        )
        
        # Verify required fields exist
        assert sample_listing.status in ['available', 'rented', 'pending_review', 'rejected']
        assert sample_listing.source_url.startswith('http')
        assert isinstance(sample_listing.price_monthly_vnd, int)
        assert sample_listing.price_monthly_vnd >= 500000
        
        print("✅ Listing model matches database schema")
        
        # Test 2: ExtractedAttribute model
        print("\n2. Testing ExtractedAttribute model...")
        
        # Boolean attribute
        bool_attr = ExtractedAttribute(attribute_slug="air_conditioner", value=True)
        assert isinstance(bool_attr.value, bool)
        
        # String attribute  
        str_attr = ExtractedAttribute(attribute_slug="description", value="Test value")
        assert isinstance(str_attr.value, str)
        
        # Integer attribute
        int_attr = ExtractedAttribute(attribute_slug="floor_number", value=3)
        assert isinstance(int_attr.value, int)
        
        print("✅ ExtractedAttribute model works with all value types")
        
        # Test 3: TransformationOutput model
        print("\n3. Testing TransformationOutput model...")
        
        output = TransformationOutput(
            listing=sample_listing,
            attributes=[bool_attr, str_attr, int_attr],
            extraction_metadata={
                "processing_time_ms": 1500,
                "model_version": "gemma-3n-e4b-it",
                "extraction_timestamp": "2025-08-19T10:30:00Z"
            }
        )
        
        assert len(output.attributes) == 3
        assert output.extraction_metadata is not None
        
        print("✅ TransformationOutput model complete and valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Data contracts test failed: {e}")
        return False

def test_transformation_structure():
    """Test transformation engine structure without LLM calls"""
    print("\n🔧 Testing Transformation Structure")
    print("===================================")
    
    try:
        from transformation_engine import get_fallback_attributes, build_dynamic_prompt
        
        # Test 1: Fallback attributes
        print("\n1. Testing fallback attribute system...")
        fallback_attrs = get_fallback_attributes()
        
        assert len(fallback_attrs) > 0
        assert 'air_conditioner' in fallback_attrs
        assert fallback_attrs['air_conditioner']['type'] == 'boolean'
        
        print(f"✅ Fallback attributes loaded ({len(fallback_attrs)} items)")
        
        # Test 2: Dynamic prompt generation
        print("\n2. Testing dynamic prompt generation...")
        prompt_section = build_dynamic_prompt(fallback_attrs)
        
        assert len(prompt_section) > 100  # Should be substantial
        assert 'air_conditioner' in prompt_section
        assert 'boolean' in prompt_section
        
        print(f"✅ Dynamic prompt generated ({len(prompt_section)} characters)")
        
        return True
        
    except Exception as e:
        print(f"❌ Transformation structure test failed: {e}")
        return False

def test_database_insertion_format():
    """Test that our output format matches the database insertion requirements"""
    print("\n💾 Testing Database Insertion Format")
    print("====================================")
    
    try:
        from transformation_engine import prepare_database_insertion_payload
        from data_contracts import Listing, ExtractedAttribute
        
        # Create sample data
        listing = Listing(
            status="pending_review",
            source_url="https://facebook.com/test/123",
            title="Test listing",
            description="Test description",
            price_monthly_vnd=2500000
        )
        
        attributes = [
            ExtractedAttribute(attribute_slug="air_conditioner", value=True),
            ExtractedAttribute(attribute_slug="price_note", value="Giá tốt")
        ]
        
        # Mock attribute map
        available_attributes = {
            "air_conditioner": {"id": 1, "type": "boolean"},
            "price_note": {"id": 2, "type": "string"}
        }
        
        # Test payload preparation
        payload = prepare_database_insertion_payload(listing, attributes, available_attributes)
        
        # Verify structure matches API requirements
        assert "listing" in payload
        assert "attributes" in payload
        assert isinstance(payload["attributes"], list)
        
        # Check attribute format matches listing_attributes table
        attr_payload = payload["attributes"][0]
        required_keys = {"attribute_id", "value_boolean", "value_integer", "value_string"}
        assert required_keys.issubset(attr_payload.keys())
        
        print("✅ Database insertion payload format correct")
        print(f"   - Listing fields: {len(payload['listing'])}")
        print(f"   - Attributes: {len(payload['attributes'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database insertion format test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Transformation Engine Validation")
    print("====================================")
    
    tests = [
        test_data_contracts,
        test_transformation_structure, 
        test_database_insertion_format
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test {test.__name__} failed")
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Transformation engine structure is valid.")
        print("📋 Ready for integration with:")
        print("   - Gemini API key configuration")
        print("   - Database connection (Cloud SQL)")
        print("   - Production deployment")
        return True
    else:
        print("❌ Some tests failed. Fix issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

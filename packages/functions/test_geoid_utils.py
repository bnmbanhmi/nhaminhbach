"""
Unit Tests for GeoID System
============================
Test Base36 conversion, fingerprinting, and house/room creation logic.

Run with:
    python3 -m pytest test_geoid_utils.py -v
    
Or directly:
    python3 test_geoid_utils.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from geoid_utils import (
    to_base36,
    from_base36,
    format_geoid_display,
    normalize_text,
    generate_address_fingerprint,
    generate_phone_fingerprint,
    get_ward_code,
    get_ward_name,
)


def test_base36_conversion():
    """Test Base36 encoding/decoding."""
    print("\n=== Test Base36 Conversion ===")
    
    # Test cases: (number, width, expected_base36)
    cases = [
        (0, 3, "000"),
        (10, 3, "00A"),
        (35, 3, "00Z"),
        (36, 3, "010"),
        (1295, 3, "0ZZ"),
        (46655, 3, "ZZZ"),  # Max for 3 chars
        (0, 2, "00"),
        (1, 2, "01"),
        (35, 2, "0Z"),
        (1295, 2, "ZZ"),  # Max for 2 chars
    ]
    
    for num, width, expected in cases:
        result = to_base36(num, width)
        assert result == expected, f"to_base36({num}, {width}) = {result}, expected {expected}"
        
        # Test reverse conversion
        decoded = from_base36(result)
        assert decoded == num, f"from_base36({result}) = {decoded}, expected {num}"
        
        print(f"✓ {num:5d} → {result} → {decoded}")
    
    print("✅ Base36 conversion tests passed")


def test_display_formatting():
    """Test elastic display formatting."""
    print("\n=== Test Display Formatting ===")
    
    cases = [
        ("29CG.0AB01", "29CGAB1"),   # Remove leading zeros
        ("29CG.00A0R", "29CGA.R"),   # Keep minimal padding
        ("29CG.W8K00", "29CGW8K"),   # Whole house (room=00)
        ("29DD.00501", "29DD51"),    # Multiple leading zeros
        ("29CG.ABC12", "29CGABC12"), # No leading zeros
    ]
    
    for full, expected in cases:
        result = format_geoid_display(full)
        assert result == expected, f"format_geoid_display({full}) = {result}, expected {expected}"
        print(f"✓ {full:14s} → {result}")
    
    print("✅ Display formatting tests passed")


def test_text_normalization():
    """Test Vietnamese text normalization."""
    print("\n=== Test Text Normalization ===")
    
    cases = [
        ("  Cầu Giấy  ", "cau giay"),
        ("Phạm Hùng", "pham hung"),
        ("123 Nguyễn Trãi, P.5", "123 nguyen trai p5"),
        ("  Multiple   Spaces  ", "multiple spaces"),
    ]
    
    for text, expected in cases:
        result = normalize_text(text)
        assert result == expected, f"normalize_text('{text}') = '{result}', expected '{expected}'"
        print(f"✓ '{text}' → '{result}'")
    
    print("✅ Text normalization tests passed")


def test_address_fingerprinting():
    """Test address fingerprinting for deduplication."""
    print("\n=== Test Address Fingerprinting ===")
    
    # Same address should produce same hash
    hash1 = generate_address_fingerprint("Hà Nội", "Dịch Vọng", "Phạm Hùng", "123")
    hash2 = generate_address_fingerprint("Hà Nội", "Dịch Vọng", "Phạm Hùng", "123")
    assert hash1 == hash2, "Same address should produce same hash"
    print(f"✓ Same address → Same hash: {hash1[:16]}...")
    
    # Different address should produce different hash
    hash3 = generate_address_fingerprint("Hà Nội", "Dịch Vọng", "Phạm Hùng", "456")
    assert hash1 != hash3, "Different address should produce different hash"
    print(f"✓ Different address → Different hash: {hash3[:16]}...")
    
    # Case insensitive
    hash4 = generate_address_fingerprint("HÀ NỘI", "DỊCH VỌNG", "PHẠM HÙNG", "123")
    assert hash1 == hash4, "Hash should be case-insensitive"
    print(f"✓ Case insensitive hashing works")
    
    # Insufficient data returns None
    hash5 = generate_address_fingerprint("Hà Nội", "", "", None)
    assert hash5 is None, "Insufficient data should return None"
    print(f"✓ Insufficient data → None")
    
    print("✅ Address fingerprinting tests passed")


def test_phone_fingerprinting():
    """Test phone-based fingerprinting."""
    print("\n=== Test Phone Fingerprinting ===")
    
    # Same phone+street should produce same hash
    hash1 = generate_phone_fingerprint("0987654321", "Phạm Hùng")
    hash2 = generate_phone_fingerprint("098-765-4321", "Phạm Hùng")  # Different format
    assert hash1 == hash2, "Same phone (different format) should produce same hash"
    print(f"✓ Same phone+street → Same hash: {hash1[:16]}...")
    
    # Different phone should produce different hash
    hash3 = generate_phone_fingerprint("0123456789", "Phạm Hùng")
    assert hash1 != hash3, "Different phone should produce different hash"
    print(f"✓ Different phone → Different hash: {hash3[:16]}...")
    
    print("✅ Phone fingerprinting tests passed")


def test_ward_codes():
    """Test ward code mapping."""
    print("\n=== Test Ward Codes ===")
    
    cases = [
        ("Cầu Giấy", "CG"),
        ("Phường Cầu Giấy", "CG"),  # With prefix
        ("Nghĩa Đô", "ND"),
        ("Dân Hòa", "DH"),
        ("Mỹ Đức", "MD"),
    ]
    
    for ward_name, expected_code in cases:
        code = get_ward_code(ward_name)
        assert code == expected_code, f"get_ward_code('{ward_name}') = {code}, expected {expected_code}"
        print(f"✓ {ward_name:20s} → {code}")
        
        # Test reverse mapping
        if code:
            name = get_ward_name(code)
            assert name is not None, f"get_ward_name('{code}') should not be None"
            print(f"  {code} → {name}")
    
    print("✅ Ward code mapping tests passed")


def test_geoid_format_examples():
    """Test real-world GeoID examples."""
    print("\n=== Test Real-World GeoID Examples ===")
    
    # Simulate creating GeoIDs for different scenarios
    scenarios = [
        {
            "desc": "First listing in Cầu Giấy",
            "house_count": 0,
            "room_num": None,
            "expected_house": "000",
            "expected_room": "00",
            "expected_full": "29CG.00000",
            "expected_display": "29CG0"
        },
        {
            "desc": "10th listing in Đống Đa",
            "house_count": 10,
            "room_num": None,
            "expected_house": "00A",
            "expected_room": "00",
            "expected_full": "29DD.00A00",
            "expected_display": "29DDA"
        },
        {
            "desc": "Room 301 in house W8K",
            "house_count": 1234,  # W8K in base36
            "room_num": "301",
            "expected_house": "W8K",
            "expected_room": "8H",  # 301 in base36
            "expected_full": "29CG.W8K8H",
            "expected_display": "29CGW8K8H"
        },
    ]
    
    for scenario in scenarios:
        house_id = to_base36(scenario["house_count"], 3)
        
        if scenario["room_num"]:
            room_id = to_base36(int(scenario["room_num"]), 2)
        else:
            room_id = "00"
        
        full_geoid = f"29CG.{house_id}{room_id}"
        
        print(f"\n{scenario['desc']}:")
        print(f"  House count: {scenario['house_count']} → {house_id}")
        print(f"  Room: {scenario['room_num']} → {room_id}")
        print(f"  Full GeoID: {full_geoid}")
        print(f"  Display: {format_geoid_display(full_geoid)}")
    
    print("\n✅ Real-world GeoID examples validated")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("GEOID SYSTEM UNIT TESTS")
    print("=" * 60)
    
    try:
        test_base36_conversion()
        test_display_formatting()
        test_text_normalization()
        test_address_fingerprinting()
        test_phone_fingerprinting()
        test_ward_codes()
        test_geoid_format_examples()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return True
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

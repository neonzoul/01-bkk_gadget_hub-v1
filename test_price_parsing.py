"""
Test script for price parsing functionality in DataProducer.
"""

from src.producers.data_producer import DataProducer

def test_price_parsing():
    """Test various price formats."""
    producer = DataProducer()
    
    test_cases = [
        ("49700", 49700.0),
        ("49,700", 49700.0),
        ("฿49,700", 49700.0),
        ("49700 THB", 49700.0),
        ("49700 Baht", 49700.0),
        (" 49,700.50 ", 49700.50),
        (49700, 49700.0),  # Already a number
        (49700.99, 49700.99),  # Already a float
    ]
    
    print("Testing price parsing...")
    
    for price_input, expected in test_cases:
        try:
            result = producer._parse_price(price_input)
            status = "✓" if result == expected else "✗"
            print(f"{status} Input: {repr(price_input)} -> Output: {result} (Expected: {expected})")
        except Exception as e:
            print(f"✗ Input: {repr(price_input)} -> Error: {e}")
    
    # Test error cases
    error_cases = [None, "", "   ", "invalid", "฿฿฿"]
    
    print("\nTesting error cases...")
    for price_input in error_cases:
        try:
            result = producer._parse_price(price_input)
            print(f"✗ Input: {repr(price_input)} -> Unexpected success: {result}")
        except Exception as e:
            print(f"✓ Input: {repr(price_input)} -> Expected error: {e}")

if __name__ == "__main__":
    test_price_parsing()
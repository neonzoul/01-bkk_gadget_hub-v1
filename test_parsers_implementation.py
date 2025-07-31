"""
Test suite for Task 6.2 - Parsers implementation validation.

This script tests the PowerBuy JSON parsing functions, price parsing logic,
and data transformation capabilities to ensure they meet all requirements.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, 'src')

def test_price_parser():
    """Test PriceParser functionality with various price formats."""
    print("Testing PriceParser...")
    
    try:
        from parsers.powerbuy_parser import PriceParser
        
        # Test cases for price parsing
        test_cases = [
            # (input, expected_output, description)
            (49700, 49700.0, "Numeric integer"),
            (49700.50, 49700.50, "Numeric float"),
            ("49700", 49700.0, "String number"),
            ("49,700", 49700.0, "String with comma"),
            ("฿49,700", 49700.0, "Thai Baht symbol"),
            ("49700 THB", 49700.0, "THB suffix"),
            ("49700 Baht", 49700.0, "Baht suffix"),
            (" ฿ 49,700.50 THB ", 49700.50, "Complex formatting"),
            ("1,234,567.89", 1234567.89, "Large number with commas"),
            ("0.01", 0.01, "Minimum valid price"),
            ("999999.99", 999999.99, "Large valid price")
        ]
        
        passed = 0
        for input_val, expected, description in test_cases:
            try:
                result = PriceParser.parse_price(input_val)
                if abs(result - expected) < 0.001:  # Float comparison with tolerance
                    print(f"   ✓ {description}: {input_val} → {result}")
                    passed += 1
                else:
                    print(f"   ❌ {description}: Expected {expected}, got {result}")
            except Exception as e:
                print(f"   ❌ {description}: Exception {str(e)}")
        
        # Test error cases
        error_cases = [
            (None, "None value"),
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            ("invalid", "Non-numeric string"),
            (-100, "Negative price")
        ]
        
        error_passed = 0
        for input_val, description in error_cases:
            try:
                PriceParser.parse_price(input_val)
                print(f"   ❌ {description}: Should have raised ValueError")
            except ValueError:
                print(f"   ✓ {description}: Correctly raised ValueError")
                error_passed += 1
            except Exception as e:
                print(f"   ❌ {description}: Wrong exception type: {type(e)}")
        
        # Test price range validation
        range_tests = [
            (100.0, True, "Normal price"),
            (0.005, False, "Below minimum"),
            (2000000.0, False, "Above maximum")
        ]
        
        range_passed = 0
        for price, expected, description in range_tests:
            result = PriceParser.validate_price_range(price)
            if result == expected:
                print(f"   ✓ Range validation {description}: {price} → {result}")
                range_passed += 1
            else:
                print(f"   ❌ Range validation {description}: Expected {expected}, got {result}")
        
        total_tests = len(test_cases) + len(error_cases) + len(range_tests)
        total_passed = passed + error_passed + range_passed
        
        print(f"   PriceParser: {total_passed}/{total_tests} tests passed")
        return total_passed == total_tests
        
    except Exception as e:
        print(f"❌ PriceParser test failed: {str(e)}")
        return False

def test_powerbuy_json_parser():
    """Test PowerBuyJSONParser with various JSON structures."""
    print("\nTesting PowerBuyJSONParser...")
    
    try:
        from parsers.powerbuy_parser import PowerBuyJSONParser
        
        parser = PowerBuyJSONParser()
        
        # Test case 1: Standard PowerBuy format
        standard_format = {
            "products": [
                {
                    "name": "iPhone 15 Pro Max",
                    "sku": "IPHONE15PM",
                    "price": "49700",
                    "stock_status": "In Stock"
                },
                {
                    "name": "Samsung Galaxy S24",
                    "sku": "GALAXYS24",
                    "price": 35900,
                    "stock_status": "มีสินค้า"
                }
            ]
        }
        
        products = parser.extract_products_from_json(standard_format, "standard_format_test")
        if len(products) == 2:
            print("   ✓ Standard format: Extracted 2 products")
            print(f"     - Product 1: {products[0].name} (SKU: {products[0].sku})")
            print(f"     - Product 2: {products[1].name} (SKU: {products[1].sku})")
        else:
            print(f"   ❌ Standard format: Expected 2 products, got {len(products)}")
            return False
        
        # Test case 2: Direct array format
        array_format = [
            {
                "name": "iPad Pro",
                "sku": "IPADPRO",
                "price": "39900"
            }
        ]
        
        parser.reset_stats()
        products = parser.extract_products_from_json(array_format, "array_format_test")
        if len(products) == 1:
            print("   ✓ Array format: Extracted 1 product")
            print(f"     - Product: {products[0].name} (SKU: {products[0].sku})")
        else:
            print(f"   ❌ Array format: Expected 1 product, got {len(products)}")
            return False
        
        # Test case 3: Single product format
        single_format = {
            "name": "MacBook Pro",
            "sku": "MACBOOKPRO",
            "price": "89900",
            "stock_status": "Available"
        }
        
        parser.reset_stats()
        products = parser.extract_products_from_json(single_format, "single_format_test")
        if len(products) == 1:
            print("   ✓ Single format: Extracted 1 product")
            print(f"     - Product: {products[0].name} (SKU: {products[0].sku})")
        else:
            print(f"   ❌ Single format: Expected 1 product, got {len(products)}")
            return False
        
        # Test case 4: Nested data format
        nested_format = {
            "data": {
                "products": [
                    {
                        "name": "AirPods Pro",
                        "sku": "AIRPODSPRO",
                        "price": "8900"
                    }
                ]
            }
        }
        
        parser.reset_stats()
        products = parser.extract_products_from_json(nested_format, "nested_format_test")
        if len(products) == 1:
            print("   ✓ Nested format: Extracted 1 product")
            print(f"     - Product: {products[0].name} (SKU: {products[0].sku})")
        else:
            print(f"   ❌ Nested format: Expected 1 product, got {len(products)}")
            return False
        
        # Test case 5: Complex price structures
        complex_price_format = {
            "products": [
                {
                    "name": "Test Product",
                    "sku": "TEST001",
                    "price": {
                        "selling": "15900",
                        "original": "17900"
                    },
                    "stock": {
                        "status": "In Stock"
                    }
                }
            ]
        }
        
        parser.reset_stats()
        products = parser.extract_products_from_json(complex_price_format, "complex_price_test")
        if len(products) == 1 and products[0].price == "15900":
            print("   ✓ Complex price structure: Extracted nested price")
            print(f"     - Product: {products[0].name} (Price: {products[0].price})")
        else:
            print(f"   ❌ Complex price structure: Failed to extract nested price")
            return False
        
        # Test statistics
        parser.reset_stats()
        parser.extract_products_from_json(standard_format, "stats_test")
        stats = parser.get_extraction_stats()
        
        if stats['products_extracted'] == 2 and stats['success_rate'] == 100.0:
            print("   ✓ Statistics tracking: Working correctly")
        else:
            print(f"   ❌ Statistics tracking: Expected 2 products, 100% success rate")
            print(f"     Got: {stats['products_extracted']} products, {stats['success_rate']}% success")
            return False
        
        print("   PowerBuyJSONParser: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ PowerBuyJSONParser test failed: {str(e)}")
        return False

def test_data_transformer():
    """Test DataTransformer functionality."""
    print("\nTesting DataTransformer...")
    
    try:
        from parsers.powerbuy_parser import DataTransformer
        from src.validators.models import RawProductData
        
        transformer = DataTransformer()
        
        # Create test raw products
        raw_products = [
            RawProductData(
                name="  iPhone 15 Pro Max  ",
                sku="  iphone15pm  ",
                price="฿49,700",
                stock_status="In Stock",
                raw_json={"test": "data1"}
            ),
            RawProductData(
                name="Samsung Galaxy S24",
                sku="GALAXYS24",
                price="35900",
                stock_status="มีสินค้า",
                raw_json={"test": "data2"}
            ),
            RawProductData(
                name="iPad Pro",
                sku="IPADPRO",
                price="39,900.50",
                stock_status="หมด",
                raw_json={"test": "data3"}
            ),
            RawProductData(
                name="",  # Empty name test
                sku="EMPTYNAME",
                price="1000",
                stock_status="Available",
                raw_json={"test": "data4"}
            )
        ]
        
        # Transform products
        validated_products = transformer.transform_to_product_data(raw_products)
        
        # Validate results
        if len(validated_products) == 4:
            print("   ✓ Transformation: All 4 products transformed successfully")
        else:
            print(f"   ❌ Transformation: Expected 4 products, got {len(validated_products)}")
            return False
        
        # Check specific transformations
        product1 = validated_products[0]
        if (product1.name == "iPhone 15 Pro Max" and 
            product1.sku == "IPHONE15PM" and 
            product1.price_thb == 49700.0 and
            product1.stock_status == "In Stock"):
            print("   ✓ Product 1: Name/SKU cleaning and price parsing correct")
        else:
            print(f"   ❌ Product 1: Transformation incorrect")
            print(f"     Expected: iPhone 15 Pro Max, IPHONE15PM, 49700.0, In Stock")
            print(f"     Got: {product1.name}, {product1.sku}, {product1.price_thb}, {product1.stock_status}")
            return False
        
        # Check Thai stock status normalization
        product2 = validated_products[1]
        if product2.stock_status == "In Stock":
            print("   ✓ Product 2: Thai stock status normalized correctly")
        else:
            print(f"   ❌ Product 2: Thai stock status not normalized: {product2.stock_status}")
            return False
        
        # Check out of stock normalization
        product3 = validated_products[2]
        if product3.stock_status == "Out of Stock" and product3.price_thb == 39900.50:
            print("   ✓ Product 3: Out of stock status and decimal price correct")
        else:
            print(f"   ❌ Product 3: Status or price incorrect: {product3.stock_status}, {product3.price_thb}")
            return False
        
        # Check empty name handling
        product4 = validated_products[3]
        if product4.name == "Unknown Product":
            print("   ✓ Product 4: Empty name handled correctly")
        else:
            print(f"   ❌ Product 4: Empty name not handled: {product4.name}")
            return False
        
        # Test statistics
        stats = transformer.get_transformation_stats()
        if (stats['transformations_attempted'] == 4 and 
            stats['transformations_successful'] == 4 and
            stats['success_rate'] == 100.0):
            print("   ✓ Statistics: Transformation stats correct")
        else:
            print(f"   ❌ Statistics: Expected 4/4 (100%), got {stats['transformations_successful']}/{stats['transformations_attempted']} ({stats['success_rate']}%)")
            return False
        
        print("   DataTransformer: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ DataTransformer test failed: {str(e)}")
        return False

def test_integration_with_existing_system():
    """Test integration with existing data models and system."""
    print("\nTesting integration with existing system...")
    
    try:
        from parsers.powerbuy_parser import PowerBuyJSONParser, DataTransformer
        from src.validators.models import RawProductData, ProductData
        
        # Test that parsers work with existing models
        parser = PowerBuyJSONParser()
        transformer = DataTransformer()
        
        # Sample data similar to what would come from scrapers
        sample_json = {
            "products": [
                {
                    "name": "Test Integration Product",
                    "sku": "INTEGRATION001",
                    "price": "25900",
                    "stock_status": "In Stock"
                }
            ]
        }
        
        # Full pipeline test
        raw_products = parser.extract_products_from_json(sample_json, "integration_test")
        validated_products = transformer.transform_to_product_data(raw_products)
        
        if (len(raw_products) == 1 and len(validated_products) == 1 and
            isinstance(raw_products[0], RawProductData) and
            isinstance(validated_products[0], ProductData)):
            print("   ✓ Integration: Full pipeline works with existing models")
        else:
            print(f"   ❌ Integration: Pipeline failed")
            print(f"     Raw products: {len(raw_products)}, Validated: {len(validated_products)}")
            if raw_products:
                print(f"     Raw product type: {type(raw_products[0])}")
            if validated_products:
                print(f"     Validated product type: {type(validated_products[0])}")
            return False
        
        # Test that ProductData validation still works
        product = validated_products[0]
        try:
            # This should work
            product_dict = product.model_dump()
            if all(key in product_dict for key in ['name', 'sku', 'price_thb', 'stock_status']):
                print("   ✓ Integration: ProductData serialization works")
            else:
                print("   ❌ Integration: ProductData missing required fields")
                return False
        except Exception as e:
            print(f"   ❌ Integration: ProductData serialization failed: {str(e)}")
            return False
        
        print("   Integration: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

def test_requirements_compliance():
    """Test that implementation meets task 6.2 requirements."""
    print("\nTesting requirements compliance...")
    
    try:
        # Requirement 3.3: Handle PowerBuy API response structure
        from parsers.powerbuy_parser import PowerBuyJSONParser
        parser = PowerBuyJSONParser()
        
        # Test PowerBuy API structure handling
        powerbuy_response = {"products": [{"name": "Test", "sku": "TEST", "price": "1000"}]}
        products = parser.extract_products_from_json(powerbuy_response, "req_test")
        
        if len(products) == 1:
            print("   ✓ Requirement 3.3: PowerBuy API structure handled")
        else:
            print("   ❌ Requirement 3.3: PowerBuy API structure not handled")
            return False
        
        # Requirement 4.2: Data transformation logic
        from parsers.powerbuy_parser import DataTransformer
        transformer = DataTransformer()
        
        validated = transformer.transform_to_product_data(products)
        if len(validated) == 1 and hasattr(validated[0], 'price_thb'):
            print("   ✓ Requirement 4.2: Data transformation logic implemented")
        else:
            print("   ❌ Requirement 4.2: Data transformation logic failed")
            return False
        
        # Requirement 4.3: Price parsing and normalization
        from parsers.powerbuy_parser import PriceParser
        
        test_price = PriceParser.parse_price("฿1,500.50")
        if test_price == 1500.50:
            print("   ✓ Requirement 4.3: Price parsing and normalization working")
        else:
            print(f"   ❌ Requirement 4.3: Price parsing failed, got {test_price}")
            return False
        
        print("   Requirements compliance: All requirements satisfied")
        return True
        
    except Exception as e:
        print(f"❌ Requirements compliance test failed: {str(e)}")
        return False

def main():
    """Run all tests for task 6.2 implementation."""
    print("Task 6.2 Implementation Test Suite")
    print("=" * 50)
    
    tests = [
        test_price_parser,
        test_powerbuy_json_parser,
        test_data_transformer,
        test_integration_with_existing_system,
        test_requirements_compliance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Task 6.2 implementation is complete.")
        print("\nImplemented Features:")
        print("✅ PowerBuyJSONParser - Handles multiple JSON response formats")
        print("✅ PriceParser - Robust price parsing with Thai currency support")
        print("✅ DataTransformer - Complete data transformation pipeline")
        print("✅ Integration - Seamless integration with existing models")
        print("✅ Requirements - All task requirements satisfied")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
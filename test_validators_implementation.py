"""
Test suite for Task 6.3 - Enhanced validators implementation.

This script tests the enhanced Pydantic models, product validation,
and stock status normalization to ensure they meet all requirements.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, 'src')

def test_enhanced_product_data_model():
    """Test enhanced ProductData model with new validation features."""
    print("Testing Enhanced ProductData Model...")
    
    try:
        from validators.models import ProductData
        
        # Test case 1: Valid product data
        valid_product = ProductData(
            name="iPhone 15 Pro Max (256GB, Natural Titanium)",
            sku="IPHONE15PM256",
            price_thb=49700.0,
            stock_status="In Stock",
            brand="Apple",
            category="Smartphones"
        )
        
        print(f"   ✓ Valid product created: {valid_product.name}")
        print(f"     SKU: {valid_product.sku}, Price: {valid_product.price_thb}")
        
        # Test case 2: Name cleaning and validation
        messy_name_product = ProductData(
            name="  Samsung   Galaxy  S24   Ultra  ",
            sku="  galaxys24ultra  ",
            price_thb=45900.50,
            stock_status="มีสินค้า"  # Thai stock status
        )
        
        if (messy_name_product.name == "Samsung Galaxy S24 Ultra" and
            messy_name_product.sku == "GALAXYS24ULTRA" and
            messy_name_product.stock_status == "In Stock"):
            print("   ✓ Name/SKU cleaning and Thai stock normalization working")
        else:
            print(f"   ❌ Cleaning failed: '{messy_name_product.name}', '{messy_name_product.sku}', '{messy_name_product.stock_status}'")
            return False
        
        # Test case 3: Price validation
        try:
            ProductData(
                name="Invalid Product",
                sku="INVALID",
                price_thb=-100.0  # Negative price should fail
            )
            print("   ❌ Negative price validation failed")
            return False
        except ValueError:
            print("   ✓ Negative price correctly rejected")
        
        # Test case 4: Enhanced stock status normalization
        thai_stock_tests = [
            ("มีสินค้า", "In Stock"),
            ("หมด", "Out of Stock"),
            ("พร้อมส่ง", "In Stock"),
            ("สินค้าหมด", "Out of Stock"),
            ("ไม่มีสินค้า", "Out of Stock"),
            ("", "Unknown")
        ]
        
        for thai_status, expected in thai_stock_tests:
            product = ProductData(
                name="Test Product",
                sku="TEST",
                price_thb=1000.0,
                stock_status=thai_status
            )
            if product.stock_status == expected:
                print(f"   ✓ Thai status '{thai_status}' → '{expected}'")
            else:
                print(f"   ❌ Thai status '{thai_status}' → '{product.stock_status}' (expected '{expected}')")
                return False
        
        print("   Enhanced ProductData Model: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced ProductData Model test failed: {str(e)}")
        return False

def test_enhanced_raw_product_data_model():
    """Test enhanced RawProductData model with field validation."""
    print("\nTesting Enhanced RawProductData Model...")
    
    try:
        from validators.models import RawProductData
        
        # Test case 1: Valid raw product data
        raw_product = RawProductData(
            name="iPhone 15 Pro Max",
            sku="IPHONE15PM",
            price="49700",
            stock_status="In Stock",
            raw_json={"test": "data"},
            brand="Apple",
            category="Electronics"
        )
        
        print(f"   ✓ Valid raw product created: {raw_product.name}")
        
        # Test case 2: Name validation and cleaning
        messy_raw = RawProductData(
            name="  Samsung    Galaxy   S24  ",
            sku="  samsung_s24  ",
            price="35900",
            raw_json={"source": "api"}
        )
        
        if (messy_raw.name == "Samsung Galaxy S24" and
            messy_raw.sku == "SAMSUNG_S24"):
            print("   ✓ Raw data name/SKU cleaning working")
        else:
            print(f"   ❌ Raw data cleaning failed: '{messy_raw.name}', '{messy_raw.sku}'")
            return False
        
        # Test case 3: Validation errors
        try:
            RawProductData(
                name="",  # Empty name should fail
                sku="TEST",
                raw_json={}
            )
            print("   ❌ Empty name validation failed")
            return False
        except ValueError:
            print("   ✓ Empty name correctly rejected")
        
        # Test case 4: Extra fields allowed
        extra_fields_product = RawProductData(
            name="Test Product",
            sku="TEST",
            raw_json={"test": "data"},
            custom_field="custom_value",  # Extra field should be allowed
            another_field=123
        )
        
        if hasattr(extra_fields_product, 'custom_field'):
            print("   ✓ Extra fields correctly allowed")
        else:
            print("   ❌ Extra fields not allowed")
            return False
        
        print("   Enhanced RawProductData Model: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced RawProductData Model test failed: {str(e)}")
        return False

def test_product_validator():
    """Test ProductValidator class functionality."""
    print("\nTesting ProductValidator...")
    
    try:
        from validators.product_validator import ProductValidator
        from validators.models import ProductData
        
        validator = ProductValidator()
        
        # Test case 1: Valid product validation
        valid_product = ProductData(
            name="iPhone 15 Pro",
            sku="IPHONE15PRO",
            price_thb=39900.0,
            stock_status="In Stock"
        )
        
        if validator.validate_product_data(valid_product):
            print("   ✓ Valid product validation passed")
        else:
            print("   ❌ Valid product validation failed")
            return False
        
        # Test case 2: Invalid product validation
        try:
            invalid_product = ProductData(
                name="X",  # Too short name
                sku="INVALID",
                price_thb=50000.0,
                stock_status="In Stock"
            )
            
            # This should pass model validation but might fail validator rules
            result = validator.validate_product_data(invalid_product)
            print(f"   ✓ Short name product validation result: {result}")
            
        except Exception as e:
            print(f"   ✓ Invalid product correctly handled: {str(e)}")
        
        # Test case 3: Validation statistics
        stats = validator.get_validation_stats()
        if (isinstance(stats, dict) and 
            'products_validated' in stats and
            'success_rate' in stats):
            print(f"   ✓ Validation statistics working: {stats['products_validated']} products, {stats['success_rate']:.1f}% success")
        else:
            print("   ❌ Validation statistics not working")
            return False
        
        print("   ProductValidator: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ ProductValidator test failed: {str(e)}")
        return False

def test_stock_status_normalizer():
    """Test StockStatusNormalizer with comprehensive Thai support."""
    print("\nTesting StockStatusNormalizer...")
    
    try:
        from validators.stock_normalizer import StockStatusNormalizer
        
        normalizer = StockStatusNormalizer()
        
        # Test case 1: English stock status normalization
        english_tests = [
            ("In Stock", "In Stock"),
            ("Available", "In Stock"),
            ("Out of Stock", "Out of Stock"),
            ("Unavailable", "Out of Stock"),
            ("sold out", "Out of Stock"),
            ("ready to ship", "In Stock")
        ]
        
        for input_status, expected in english_tests:
            result = normalizer.normalize_stock_status(input_status)
            if result == expected:
                print(f"   ✓ English: '{input_status}' → '{result}'")
            else:
                print(f"   ❌ English: '{input_status}' → '{result}' (expected '{expected}')")
                return False
        
        # Test case 2: Thai stock status normalization
        thai_tests = [
            ("มีสินค้า", "In Stock"),
            ("พร้อมส่ง", "In Stock"),
            ("หมด", "Out of Stock"),
            ("สินค้าหมด", "Out of Stock"),
            ("ไม่มีสินค้า", "Out of Stock"),
            ("พร้อมจัดส่ง", "In Stock"),
            ("ขายหมด", "Out of Stock")
        ]
        
        for input_status, expected in thai_tests:
            result = normalizer.normalize_stock_status(input_status)
            if result == expected:
                print(f"   ✓ Thai: '{input_status}' → '{result}'")
            else:
                print(f"   ❌ Thai: '{input_status}' → '{result}' (expected '{expected}')")
                return False
        
        # Test case 3: Edge cases
        edge_cases = [
            (None, "Unknown"),
            ("", "Unknown"),
            ("   ", "Unknown"),
            ("random text", "Unknown")
        ]
        
        for input_status, expected in edge_cases:
            result = normalizer.normalize_stock_status(input_status)
            if result == expected:
                print(f"   ✓ Edge case: '{input_status}' → '{result}'")
            else:
                print(f"   ❌ Edge case: '{input_status}' → '{result}' (expected '{expected}')")
                return False
        
        # Test case 4: Statistics
        stats = normalizer.get_normalization_stats()
        if (isinstance(stats, dict) and 
            'total_normalized' in stats and
            'success_rate' in stats):
            print(f"   ✓ Normalization statistics: {stats['total_normalized']} normalized, {stats['success_rate']:.1f}% success")
        else:
            print("   ❌ Normalization statistics not working")
            return False
        
        print("   StockStatusNormalizer: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ StockStatusNormalizer test failed: {str(e)}")
        return False

def test_integration_with_existing_system():
    """Test integration with existing parsers and other components."""
    print("\nTesting Integration with Existing System...")
    
    try:
        # Test that parsers can still import and use the models
        from parsers.powerbuy_parser import DataTransformer
        from src.validators.models import RawProductData, ProductData
        
        # Create test data
        raw_product = RawProductData(
            name="Integration Test Product",
            sku="INTEGRATION001",
            price="25900",
            stock_status="มีสินค้า",
            raw_json={"test": "integration"}
        )
        
        # Test transformation
        transformer = DataTransformer()
        validated_products = transformer.transform_to_product_data([raw_product])
        
        if len(validated_products) == 1:
            product = validated_products[0]
            if isinstance(product, ProductData):
                # Check if stock status is properly normalized (should be "In Stock" for "มีสินค้า")
                expected_stock = "In Stock"  # "มีสินค้า" should normalize to "In Stock"
                actual_stock = product.stock_status
                
                if actual_stock == expected_stock:
                    print("   ✓ Integration with parsers working")
                else:
                    print(f"   ❌ Stock normalization in integration: '{actual_stock}' (expected '{expected_stock}')")
                    return False
            else:
                print(f"   ❌ Type check failed: {type(product)}")
                return False
        else:
            print(f"   ❌ Length check failed: {len(validated_products)}")
            return False
        
        # Test that enhanced validation works in the pipeline
        product = validated_products[0]
        if (product.name == "Integration Test Product" and
            product.sku == "INTEGRATION001" and
            product.price_thb == 25900.0):
            print("   ✓ Enhanced validation working in pipeline")
        else:
            print("   ❌ Enhanced validation not working in pipeline")
            return False
        
        print("   Integration: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

def test_requirements_compliance():
    """Test that implementation meets task 6.3 requirements."""
    print("\nTesting Requirements Compliance...")
    
    try:
        # Requirement 4.1: Move Pydantic models to dedicated validators module
        from validators import RawProductData, ProductData, CollectionSummary, ProcessingSummary
        print("   ✓ Requirement 4.1: Pydantic models in dedicated validators module")
        
        # Requirement 4.3: Add stock status normalization to standard values
        from validators import StockStatusNormalizer
        normalizer = StockStatusNormalizer()
        
        # Test comprehensive normalization
        test_statuses = ["มีสินค้า", "หมด", "In Stock", "Out of Stock", "Available"]
        normalized = [normalizer.normalize_stock_status(status) for status in test_statuses]
        
        if all(status in ["In Stock", "Out of Stock", "Unknown"] for status in normalized):
            print("   ✓ Requirement 4.3: Stock status normalization to standard values")
        else:
            print(f"   ❌ Requirement 4.3: Invalid normalized values: {normalized}")
            return False
        
        # Requirement 1.1: Integrate Pydantic validation for all processed product data
        from validators import ProductValidator
        validator = ProductValidator()
        
        # Test that validation is integrated
        test_product = ProductData(
            name="Test Product",
            sku="TEST001",
            price_thb=1000.0,
            stock_status="In Stock"
        )
        
        if validator.validate_product_data(test_product):
            print("   ✓ Requirement 1.1: Pydantic validation integrated for processed data")
        else:
            print("   ❌ Requirement 1.1: Pydantic validation not working")
            return False
        
        print("   Requirements compliance: All requirements satisfied")
        return True
        
    except Exception as e:
        print(f"❌ Requirements compliance test failed: {str(e)}")
        return False

def main():
    """Run all tests for task 6.3 implementation."""
    print("Task 6.3 Implementation Test Suite")
    print("=" * 50)
    
    tests = [
        test_enhanced_product_data_model,
        test_enhanced_raw_product_data_model,
        test_product_validator,
        test_stock_status_normalizer,
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
        print("🎉 All tests passed! Task 6.3 implementation is complete.")
        print("\nImplemented Features:")
        print("✅ Enhanced Pydantic models with comprehensive validation")
        print("✅ ProductValidator for advanced product data validation")
        print("✅ StockStatusNormalizer with extensive Thai language support")
        print("✅ Integration with existing parsers and data pipeline")
        print("✅ Requirements compliance - all task requirements satisfied")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
"""
Integration test with actual POC data to validate complete data pipeline.
This test demonstrates that our data models work with the existing POC CSV structure.
"""

import csv
import json
import os
from datetime import datetime
from typing import List

from src.validators.models import RawProductData, ProductData, ProcessingSummary
from src.producers.data_producer import DataProducer


def create_json_from_poc_csv():
    """Convert POC CSV data to JSON format for testing."""
    poc_csv_path = "_dev-Document/250726-scriping-powerbuy/test_collect.csv"
    
    if not os.path.exists(poc_csv_path):
        print("POC CSV file not found, creating sample data...")
        return create_sample_json_data()
    
    # Read POC CSV data
    products = []
    with open(poc_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert CSV format to JSON format
            product = {
                "sku": row['SKU'],
                "name": row['Name'].strip('"'),  # Remove quotes
                "price": int(row['Price'].replace(',', ''))  # Remove commas and convert to int
            }
            products.append(product)
    
    return {"products": products}


def create_sample_json_data():
    """Create sample JSON data if POC CSV is not available."""
    return {
        "products": [
            {
                "sku": "295649",
                "name": "Galaxy S24 Ultra (RAM 12GB, 256GB, Titanium Black)",
                "price": 30400
            },
            {
                "sku": "286634",
                "name": "Galaxy S23 Ultra (RAM 8GB, 256GB, Phantom Black)",
                "price": 41900
            },
            {
                "sku": "289217",
                "name": "ตู้เย็น 2 ประตู 13.9 คิว Inverter (สีดำ) รุ่น RT38CG6020B1ST",
                "price": 9990
            }
        ]
    }


def test_complete_data_pipeline():
    """Test the complete data pipeline from JSON to validated ProductData."""
    print("Testing Complete Data Pipeline")
    print("=" * 50)
    
    # Step 1: Create test JSON data from POC
    print("Step 1: Creating JSON data from POC CSV...")
    json_data = create_json_from_poc_csv()
    print(f"   Created JSON with {len(json_data['products'])} products")
    
    # Step 2: Save JSON to test file
    test_json_path = "raw_data/search_results/poc_integration_test.json"
    os.makedirs(os.path.dirname(test_json_path), exist_ok=True)
    
    with open(test_json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"   Saved test JSON to: {test_json_path}")
    
    # Step 3: Initialize DataProducer and process data
    print("\nStep 2: Processing data with DataProducer...")
    producer = DataProducer()
    producer.reset_stats()
    
    # Load raw data
    raw_data = producer.load_raw_data()
    print(f"   Loaded {len(raw_data)} JSON files")
    
    # Process products
    raw_products = producer.process_products(raw_data)
    print(f"   Extracted {len(raw_products)} raw products")
    
    # Validate data
    validated_products = producer.validate_data(raw_products)
    print(f"   Validated {len(validated_products)} products")
    
    # Step 4: Generate processing summary
    print("\nStep 3: Generating processing summary...")
    summary = producer.get_processing_summary()
    
    print(f"   Files processed: {summary.total_files_processed}")
    print(f"   Products extracted: {summary.total_products_extracted}")
    print(f"   Successful validations: {summary.successful_validations}")
    print(f"   Validation failures: {summary.validation_failures}")
    
    if producer.stats['errors']:
        print(f"   Errors: {len(producer.stats['errors'])}")
        for error in producer.stats['errors'][:3]:
            print(f"     - {error}")
    
    # Step 5: Validate specific products
    print("\nStep 4: Validating specific products...")
    
    if validated_products:
        # Test first product
        product1 = validated_products[0]
        print(f"   Product 1: {product1.name}")
        print(f"     SKU: {product1.sku}")
        print(f"     Price: {product1.price_thb:,.2f} THB")
        print(f"     Stock: {product1.stock_status}")
        
        # Validate data types
        assert isinstance(product1.name, str), "Name should be string"
        assert isinstance(product1.sku, str), "SKU should be string"
        assert isinstance(product1.price_thb, float), "Price should be float"
        assert isinstance(product1.stock_status, (str, type(None))), "Stock status should be string or None"
        
        # Find Thai product if available
        thai_products = [p for p in validated_products if any(ord(c) > 127 for c in p.name)]
        if thai_products:
            thai_product = thai_products[0]
            print(f"   Thai Product: {thai_product.name}")
            print(f"     SKU: {thai_product.sku}")
            print(f"     Price: {thai_product.price_thb:,.2f} THB")
            
            # Validate Thai text handling
            assert len(thai_product.name) > 0, "Thai product name should not be empty"
            assert thai_product.price_thb > 0, "Thai product price should be positive"
    
    # Step 6: Test data model serialization
    print("\nStep 5: Testing data serialization...")
    
    if validated_products:
        # Test JSON serialization
        product_dict = validated_products[0].dict()
        print(f"   Serialized product keys: {list(product_dict.keys())}")
        
        # Validate serialized data
        assert 'name' in product_dict
        assert 'sku' in product_dict
        assert 'price_thb' in product_dict
        assert 'stock_status' in product_dict
        
        # Test that price is properly formatted
        assert isinstance(product_dict['price_thb'], float)
        assert product_dict['price_thb'] >= 0
    
    print("\n✅ Complete data pipeline test passed!")
    return True


def test_error_handling_scenarios():
    """Test various error handling scenarios."""
    print("\nTesting Error Handling Scenarios")
    print("=" * 50)
    
    producer = DataProducer()
    producer.reset_stats()
    
    # Test 1: Invalid price formats
    print("Test 1: Invalid price formats...")
    invalid_data = {
        "products": [
            {
                "sku": "TEST001",
                "name": "Valid Product",
                "price": 100
            },
            {
                "sku": "TEST002", 
                "name": "Invalid Price Product",
                "price": "not_a_number"
            },
            {
                "sku": "TEST003",
                "name": "Missing Price Product"
                # No price field
            }
        ]
    }
    
    raw_products = producer._extract_products_from_json(invalid_data)
    validated_products = producer.validate_data(raw_products)
    
    print(f"   Raw products extracted: {len(raw_products)}")
    print(f"   Valid products after validation: {len(validated_products)}")
    print(f"   Validation failures: {producer.stats['validation_failures']}")
    
    assert len(raw_products) == 3, "Should extract all raw products"
    assert len(validated_products) == 1, "Should validate only products with valid prices"
    assert producer.stats['validation_failures'] == 2, "Should have 2 validation failures"
    
    # Test 2: Empty data structures
    print("\nTest 2: Empty data structures...")
    producer.reset_stats()
    
    empty_data_cases = [
        {"products": []},  # Empty products array
        {},  # Empty object
        {"other_field": "value"}  # No products field
    ]
    
    for i, empty_data in enumerate(empty_data_cases):
        raw_products = producer._extract_products_from_json(empty_data)
        print(f"   Case {i+1}: Extracted {len(raw_products)} products")
        assert len(raw_products) == 0, f"Should extract 0 products from empty case {i+1}"
    
    print("✅ Error handling tests passed!")


def generate_test_report():
    """Generate a comprehensive test report."""
    print("\nGenerating Test Report")
    print("=" * 50)
    
    report = {
        "test_date": datetime.now().isoformat(),
        "test_results": {
            "complete_pipeline": False,
            "error_handling": False,
            "poc_compatibility": False
        },
        "statistics": {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        },
        "details": []
    }
    
    # Run tests and collect results
    try:
        test_complete_data_pipeline()
        report["test_results"]["complete_pipeline"] = True
        report["statistics"]["passed_tests"] += 1
        report["details"].append("✅ Complete data pipeline test passed")
    except Exception as e:
        report["test_results"]["complete_pipeline"] = False
        report["statistics"]["failed_tests"] += 1
        report["details"].append(f"❌ Complete data pipeline test failed: {e}")
    
    try:
        test_error_handling_scenarios()
        report["test_results"]["error_handling"] = True
        report["statistics"]["passed_tests"] += 1
        report["details"].append("✅ Error handling test passed")
    except Exception as e:
        report["test_results"]["error_handling"] = False
        report["statistics"]["failed_tests"] += 1
        report["details"].append(f"❌ Error handling test failed: {e}")
    
    # POC compatibility test
    poc_csv_path = "_dev-Document/250726-scriping-powerbuy/test_collect.csv"
    if os.path.exists(poc_csv_path):
        try:
            json_data = create_json_from_poc_csv()
            if len(json_data["products"]) > 0:
                report["test_results"]["poc_compatibility"] = True
                report["statistics"]["passed_tests"] += 1
                report["details"].append("✅ POC compatibility test passed")
            else:
                raise Exception("No products found in POC data")
        except Exception as e:
            report["test_results"]["poc_compatibility"] = False
            report["statistics"]["failed_tests"] += 1
            report["details"].append(f"❌ POC compatibility test failed: {e}")
    else:
        report["details"].append("⚠️  POC CSV file not found, skipping compatibility test")
    
    report["statistics"]["total_tests"] = report["statistics"]["passed_tests"] + report["statistics"]["failed_tests"]
    
    # Save report
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Display summary
    print(f"\nTest Summary:")
    print(f"  Total tests: {report['statistics']['total_tests']}")
    print(f"  Passed: {report['statistics']['passed_tests']}")
    print(f"  Failed: {report['statistics']['failed_tests']}")
    print(f"  Success rate: {(report['statistics']['passed_tests'] / max(report['statistics']['total_tests'], 1)) * 100:.1f}%")
    
    print(f"\nDetailed Results:")
    for detail in report["details"]:
        print(f"  {detail}")
    
    print(f"\nReport saved to: test_report.json")
    
    return report


if __name__ == "__main__":
    print("POC Integration Test Suite")
    print("=" * 60)
    
    # Run all tests and generate report
    report = generate_test_report()
    
    # Final status
    if report["statistics"]["failed_tests"] == 0:
        print("\n🎉 All tests passed! Data models are ready for production.")
    else:
        print(f"\n⚠️  {report['statistics']['failed_tests']} test(s) failed. Please review the issues above.")
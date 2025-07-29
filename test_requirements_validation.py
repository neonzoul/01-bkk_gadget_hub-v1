"""
Requirements validation test for Task 3.
Validates that data models work with existing test_collect.csv data structure,
tests data transformation and validation functions, and creates unit tests
for data models with various input scenarios.
"""

import csv
import json
import os
from datetime import datetime

from src.validators.models import RawProductData, ProductData, CollectionSummary, ProcessingSummary
from src.producers.data_producer import DataProducer


def validate_requirement_4_1():
    """
    Requirement 4.1: Validate Pydantic models work with existing test_collect.csv data structure
    """
    print("Validating Requirement 4.1: Pydantic models with POC CSV data")
    print("-" * 60)
    
    poc_csv_path = "_dev-Document/250726-scriping-powerbuy/test_collect.csv"
    
    if not os.path.exists(poc_csv_path):
        print("⚠️  POC CSV file not found, using sample data")
        sample_data = [
            {"Name": "Galaxy S24 Ultra (RAM 12GB, 256GB, Titanium Black)", "SKU": "295649", "Price": "30,400"},
            {"Name": "ตู้เย็น 2 ประตู 13.9 คิว Inverter (สีดำ)", "SKU": "289217", "Price": "9,990"}
        ]
    else:
        # Read actual POC CSV data
        with open(poc_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sample_data = list(reader)[:10]  # Test with first 10 rows
    
    producer = DataProducer()
    successful_conversions = 0
    total_rows = len(sample_data)
    
    print(f"Testing {total_rows} rows from POC CSV data...")
    
    for i, row in enumerate(sample_data):
        try:
            # Convert POC CSV format to our data models
            
            # Step 1: Create RawProductData (simulating JSON input)
            raw_product = RawProductData(
                name=row['Name'].strip('"'),  # Remove quotes if present
                sku=row['SKU'],
                price=row['Price'],  # Keep original format for price parsing test
                stock_status=None,  # POC didn't have stock status
                raw_json={
                    "name": row['Name'].strip('"'),
                    "sku": row['SKU'],
                    "price": row['Price']
                }
            )
            
            # Step 2: Convert to ProductData (with validation)
            price_thb = producer._parse_price(raw_product.price)
            
            validated_product = ProductData(
                name=raw_product.name,
                sku=raw_product.sku,
                price_thb=price_thb,
                stock_status="Unknown"  # Default for POC data
            )
            
            successful_conversions += 1
            
            if i < 3:  # Show first 3 conversions
                print(f"  ✅ Row {i+1}: {validated_product.name[:50]}...")
                print(f"     SKU: {validated_product.sku}, Price: {validated_product.price_thb:,.2f} THB")
            
        except Exception as e:
            print(f"  ❌ Row {i+1} failed: {e}")
    
    success_rate = (successful_conversions / total_rows) * 100
    print(f"\nResults: {successful_conversions}/{total_rows} successful conversions ({success_rate:.1f}%)")
    
    assert success_rate >= 95, f"Success rate {success_rate:.1f}% is below 95% threshold"
    print("✅ Requirement 4.1 PASSED: Pydantic models work with POC CSV data")
    
    return True


def validate_requirement_4_2():
    """
    Requirement 4.2: Test data transformation and validation functions
    """
    print("\nValidating Requirement 4.2: Data transformation and validation functions")
    print("-" * 60)
    
    producer = DataProducer()
    
    # Test 1: JSON to RawProductData transformation
    print("Test 1: JSON to RawProductData transformation...")
    test_json = {
        "products": [
            {"sku": "TEST001", "name": "Test Product 1", "price": 1000},
            {"sku": "TEST002", "name": "Test Product 2", "price": "2,500"},
            {"sku": "TEST003", "name": "ทดสอบสินค้า 3", "price": "฿3,990"}
        ]
    }
    
    raw_products = producer._extract_products_from_json(test_json)
    assert len(raw_products) == 3, "Should extract 3 raw products"
    assert all(isinstance(p, RawProductData) for p in raw_products), "All should be RawProductData instances"
    print("  ✅ JSON to RawProductData transformation works")
    
    # Test 2: RawProductData to ProductData validation
    print("Test 2: RawProductData to ProductData validation...")
    validated_products = producer.validate_data(raw_products)
    assert len(validated_products) == 3, "Should validate 3 products"
    assert all(isinstance(p, ProductData) for p in validated_products), "All should be ProductData instances"
    print("  ✅ RawProductData to ProductData validation works")
    
    # Test 3: Price transformation functions
    print("Test 3: Price transformation functions...")
    price_test_cases = [
        ("1000", 1000.0),
        ("2,500", 2500.0),
        ("฿3,990", 3990.0),
        ("4500 THB", 4500.0),
        (5000, 5000.0)
    ]
    
    for price_input, expected in price_test_cases:
        result = producer._parse_price(price_input)
        assert result == expected, f"Price parsing failed for {price_input}"
    
    print("  ✅ Price transformation functions work")
    
    # Test 4: Stock status normalization
    print("Test 4: Stock status normalization...")
    stock_test_cases = [
        ("in stock", "In Stock"),
        ("มีสินค้า", "In Stock"),
        ("out of stock", "Out of Stock"),
        ("หมด", "Out of Stock"),
        ("unknown", "Unknown"),
        (None, "Unknown")
    ]
    
    for stock_input, expected in stock_test_cases:
        product = ProductData(
            name="Test",
            sku="TEST",
            price_thb=100.0,
            stock_status=stock_input
        )
        assert product.stock_status == expected, f"Stock normalization failed for {stock_input}"
    
    print("  ✅ Stock status normalization works")
    
    print("✅ Requirement 4.2 PASSED: Data transformation and validation functions work correctly")
    return True


def validate_requirement_4_3():
    """
    Requirement 4.3: Create unit tests for data models with various input scenarios
    """
    print("\nValidating Requirement 4.3: Unit tests for data models with various scenarios")
    print("-" * 60)
    
    test_scenarios = [
        "Valid complete data",
        "Missing optional fields", 
        "Edge case prices",
        "Thai text handling",
        "Error conditions",
        "Boundary values"
    ]
    
    passed_scenarios = 0
    
    # Scenario 1: Valid complete data
    print("Scenario 1: Valid complete data...")
    try:
        product = ProductData(
            name="Complete Product",
            sku="COMP001",
            price_thb=1500.99,
            stock_status="In Stock"
        )
        assert product.name == "Complete Product"
        assert product.price_thb == 1500.99
        passed_scenarios += 1
        print("  ✅ Valid complete data scenario passed")
    except Exception as e:
        print(f"  ❌ Valid complete data scenario failed: {e}")
    
    # Scenario 2: Missing optional fields
    print("Scenario 2: Missing optional fields...")
    try:
        raw_product = RawProductData(
            name="Minimal Product",
            sku="MIN001",
            raw_json={"name": "Minimal Product", "sku": "MIN001"}
        )
        assert raw_product.price is None
        assert raw_product.stock_status is None
        passed_scenarios += 1
        print("  ✅ Missing optional fields scenario passed")
    except Exception as e:
        print(f"  ❌ Missing optional fields scenario failed: {e}")
    
    # Scenario 3: Edge case prices
    print("Scenario 3: Edge case prices...")
    try:
        producer = DataProducer()
        edge_prices = ["0", "0.01", "999999.99", "1,234,567.89"]
        for price in edge_prices:
            result = producer._parse_price(price)
            assert result >= 0, f"Price should be non-negative: {price}"
        passed_scenarios += 1
        print("  ✅ Edge case prices scenario passed")
    except Exception as e:
        print(f"  ❌ Edge case prices scenario failed: {e}")
    
    # Scenario 4: Thai text handling
    print("Scenario 4: Thai text handling...")
    try:
        thai_product = ProductData(
            name="สมาร์ทโฟน iPhone 15 Pro Max (256GB, สีทิเทเนียมธรรมชาติ)",
            sku="THAI001",
            price_thb=45900.0,
            stock_status="มีสินค้า"
        )
        assert len(thai_product.name) > 0
        assert "สมาร์ทโฟน" in thai_product.name
        assert thai_product.stock_status == "In Stock"  # Should be normalized
        passed_scenarios += 1
        print("  ✅ Thai text handling scenario passed")
    except Exception as e:
        print(f"  ❌ Thai text handling scenario failed: {e}")
    
    # Scenario 5: Error conditions
    print("Scenario 5: Error conditions...")
    try:
        error_caught = False
        try:
            ProductData(
                name="Invalid Product",
                sku="INV001",
                price_thb=-100.0,  # Negative price should fail
                stock_status="In Stock"
            )
        except ValueError:
            error_caught = True
        
        assert error_caught, "Should have caught negative price error"
        passed_scenarios += 1
        print("  ✅ Error conditions scenario passed")
    except Exception as e:
        print(f"  ❌ Error conditions scenario failed: {e}")
    
    # Scenario 6: Boundary values
    print("Scenario 6: Boundary values...")
    try:
        # Test very long names, empty strings, etc.
        long_name = "A" * 500  # Very long product name
        product = ProductData(
            name=long_name,
            sku="LONG001",
            price_thb=0.01,  # Minimum price
            stock_status=""  # Empty stock status
        )
        assert len(product.name) == 500
        assert product.price_thb == 0.01
        assert product.stock_status == "Unknown"  # Should normalize empty to Unknown
        passed_scenarios += 1
        print("  ✅ Boundary values scenario passed")
    except Exception as e:
        print(f"  ❌ Boundary values scenario failed: {e}")
    
    success_rate = (passed_scenarios / len(test_scenarios)) * 100
    print(f"\nResults: {passed_scenarios}/{len(test_scenarios)} scenarios passed ({success_rate:.1f}%)")
    
    assert success_rate >= 95, f"Scenario success rate {success_rate:.1f}% is below 95% threshold"
    print("✅ Requirement 4.3 PASSED: Unit tests cover various input scenarios")
    
    return True


def generate_final_validation_report():
    """Generate final validation report for Task 3."""
    print("\n" + "="*80)
    print("TASK 3 FINAL VALIDATION REPORT")
    print("="*80)
    
    requirements = [
        ("4.1", "Validate Pydantic models work with existing test_collect.csv data structure"),
        ("4.2", "Test data transformation and validation functions"),
        ("4.3", "Create unit tests for data models with various input scenarios")
    ]
    
    results = {}
    
    # Run all requirement validations
    try:
        results["4.1"] = validate_requirement_4_1()
    except Exception as e:
        results["4.1"] = False
        print(f"❌ Requirement 4.1 FAILED: {e}")
    
    try:
        results["4.2"] = validate_requirement_4_2()
    except Exception as e:
        results["4.2"] = False
        print(f"❌ Requirement 4.2 FAILED: {e}")
    
    try:
        results["4.3"] = validate_requirement_4_3()
    except Exception as e:
        results["4.3"] = False
        print(f"❌ Requirement 4.3 FAILED: {e}")
    
    # Generate summary
    passed_requirements = sum(results.values())
    total_requirements = len(requirements)
    success_rate = (passed_requirements / total_requirements) * 100
    
    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Requirements tested: {total_requirements}")
    print(f"Requirements passed: {passed_requirements}")
    print(f"Requirements failed: {total_requirements - passed_requirements}")
    print(f"Success rate: {success_rate:.1f}%")
    
    print(f"\nDetailed Results:")
    for req_id, description in requirements:
        status = "✅ PASSED" if results.get(req_id, False) else "❌ FAILED"
        print(f"  {req_id}: {status} - {description}")
    
    # Save report
    report = {
        "task": "Task 3: Test data models with sample JSON data from POC",
        "test_date": datetime.now().isoformat(),
        "requirements_tested": {req_id: desc for req_id, desc in requirements},
        "results": results,
        "summary": {
            "total_requirements": total_requirements,
            "passed_requirements": passed_requirements,
            "failed_requirements": total_requirements - passed_requirements,
            "success_rate": success_rate
        }
    }
    
    with open("task3_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: task3_validation_report.json")
    
    if success_rate == 100:
        print("\n🎉 TASK 3 COMPLETED SUCCESSFULLY!")
        print("All requirements have been validated and are working correctly.")
        print("Data models are ready for production use with POC data structure.")
    else:
        print(f"\n⚠️  TASK 3 PARTIALLY COMPLETED ({success_rate:.1f}%)")
        print("Some requirements need attention before marking task as complete.")
    
    return success_rate == 100


if __name__ == "__main__":
    print("Task 3 Requirements Validation")
    print("Testing data models with sample JSON data from POC")
    print("="*80)
    
    success = generate_final_validation_report()
    
    if success:
        print("\n✅ Task 3 is ready to be marked as COMPLETED")
    else:
        print("\n❌ Task 3 needs additional work before completion")
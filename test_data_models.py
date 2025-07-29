"""
Comprehensive unit tests for data models with sample JSON data from POC.
Tests Pydantic models, data transformation, and validation functions.
"""

import json
import csv
import os
from typing import List, Dict, Any
from datetime import datetime

from src.validators.models import RawProductData, ProductData, CollectionSummary, ProcessingSummary
from src.producers.data_producer import DataProducer


class TestDataModels:
    """Test suite for Pydantic data models."""
    
    def setup_method(self):
        """Setup test data for each test method."""
        # Sample PowerBuy API JSON structure
        self.sample_json_data = {
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
                }
            ]
        }
        
        # Sample CSV data from POC (converted to expected format)
        self.poc_csv_data = [
            {"Name": "Galaxy S23 Ultra (RAM 8GB, 256GB, Phantom Black)", "SKU": "286634", "Price": "41,900"},
            {"Name": "Galaxy S24 Ultra (RAM 12GB, 256GB, Titanium Black)", "SKU": "295649", "Price": "30,400"},
            {"Name": "ตู้เย็น 2 ประตู 13.9 คิว Inverter (สีดำ) รุ่น RT38CG6020B1ST", "SKU": "289217", "Price": "9,990"}
        ]
    
    def test_raw_product_data_creation(self):
        """Test RawProductData model creation with various inputs."""
        # Test with complete data
        raw_product = RawProductData(
            name="Galaxy S24 Ultra (RAM 12GB, 256GB, Titanium Black)",
            sku="295649",
            price="30400",
            stock_status="In Stock",
            raw_json=self.sample_json_data["products"][0]
        )
        
        assert raw_product.name == "Galaxy S24 Ultra (RAM 12GB, 256GB, Titanium Black)"
        assert raw_product.sku == "295649"
        assert raw_product.price == "30400"
        assert raw_product.stock_status == "In Stock"
        assert raw_product.raw_json["sku"] == "295649"
    
    def test_raw_product_data_with_missing_fields(self):
        """Test RawProductData with optional missing fields."""
        raw_product = RawProductData(
            name="Test Product",
            sku="TEST001",
            raw_json={"sku": "TEST001", "name": "Test Product"}
        )
        
        assert raw_product.name == "Test Product"
        assert raw_product.sku == "TEST001"
        assert raw_product.price is None
        assert raw_product.stock_status is None
    
    def test_product_data_validation(self):
        """Test ProductData validation with various price formats."""
        # Test with valid data
        product = ProductData(
            name="Galaxy S24 Ultra",
            sku="295649",
            price_thb=30400.0,
            stock_status="In Stock"
        )
        
        assert product.name == "Galaxy S24 Ultra"
        assert product.sku == "295649"
        assert product.price_thb == 30400.0
        assert product.stock_status == "In Stock"
    
    def test_product_data_price_validation(self):
        """Test price validation rules."""
        # Test price rounding
        product = ProductData(
            name="Test Product",
            sku="TEST001",
            price_thb=30400.999,
            stock_status="In Stock"
        )
        assert product.price_thb == 30401.0  # Should round to 2 decimal places
        
        # Test negative price validation
        try:
            ProductData(
                name="Test Product",
                sku="TEST001",
                price_thb=-100.0,
                stock_status="In Stock"
            )
            assert False, "Should have raised ValueError for negative price"
        except ValueError as e:
            assert "Price cannot be negative" in str(e)
    
    def test_stock_status_normalization(self):
        """Test stock status normalization for various inputs."""
        test_cases = [
            ("in stock", "In Stock"),
            ("available", "In Stock"),
            ("มีสินค้า", "In Stock"),
            ("พร้อมส่ง", "In Stock"),
            ("out of stock", "Out of Stock"),
            ("unavailable", "Out of Stock"),
            ("หมด", "Out of Stock"),
            ("สินค้าหมด", "Out of Stock"),
            ("unknown status", "Unknown"),
            ("", "Unknown"),
            (None, "Unknown")
        ]
        
        for input_status, expected_output in test_cases:
            product = ProductData(
                name="Test Product",
                sku="TEST001",
                price_thb=100.0,
                stock_status=input_status
            )
            assert product.stock_status == expected_output, f"Failed for input: {input_status}"
    
    def test_collection_summary_validation(self):
        """Test CollectionSummary model validation."""
        summary = CollectionSummary(
            search_terms_processed=["iphone", "samsung"],
            total_products_found=50,
            files_created=["iphone_data.json", "samsung_data.json"],
            errors=["Network timeout on page 3"],
            collection_time=datetime.now()
        )
        
        assert len(summary.search_terms_processed) == 2
        assert summary.total_products_found == 50
        assert len(summary.files_created) == 2
        assert len(summary.errors) == 1
        
        # Test negative product count validation
        try:
            CollectionSummary(
                search_terms_processed=["test"],
                total_products_found=-1,
                files_created=[],
                errors=[],
                collection_time=datetime.now()
            )
            assert False, "Should have raised ValueError for negative product count"
        except ValueError as e:
            assert "Product count cannot be negative" in str(e)
    
    def test_processing_summary_validation(self):
        """Test ProcessingSummary model validation."""
        summary = ProcessingSummary(
            total_files_processed=2,
            total_products_extracted=50,
            successful_validations=48,
            validation_failures=2,
            processing_time=datetime.now(),
            output_file="competitor_prices_2025-07-30.csv"
        )
        
        assert summary.total_files_processed == 2
        assert summary.total_products_extracted == 50
        assert summary.successful_validations == 48
        assert summary.validation_failures == 2
        
        # Test negative count validation
        try:
            ProcessingSummary(
                total_files_processed=-1,
                total_products_extracted=0,
                successful_validations=0,
                validation_failures=0,
                processing_time=datetime.now(),
                output_file="test.csv"
            )
            assert False, "Should have raised ValueError for negative count"
        except ValueError as e:
            assert "Count values cannot be negative" in str(e)


class TestDataTransformation:
    """Test data transformation and validation functions."""
    
    def setup_method(self):
        """Setup test data and DataProducer instance."""
        self.producer = DataProducer()
        
        # Create test JSON file with POC-like data
        self.test_data = {
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
    
    def test_json_to_raw_product_transformation(self):
        """Test transformation from JSON to RawProductData."""
        raw_products = self.producer._extract_products_from_json(self.test_data)
        
        assert len(raw_products) == 3
        
        # Test first product
        product1 = raw_products[0]
        assert isinstance(product1, RawProductData)
        assert product1.name == "Galaxy S24 Ultra (RAM 12GB, 256GB, Titanium Black)"
        assert product1.sku == "295649"
        assert product1.price == "30400"
        assert product1.stock_status == "Unknown"  # Default when not provided
        
        # Test Thai product name handling
        product3 = raw_products[2]
        assert "ตู้เย็น" in product3.name
        assert product3.sku == "289217"
    
    def test_raw_to_validated_product_transformation(self):
        """Test transformation from RawProductData to ProductData."""
        raw_products = self.producer._extract_products_from_json(self.test_data)
        validated_products = self.producer.validate_data(raw_products)
        
        assert len(validated_products) == 3
        
        # Test first validated product
        product1 = validated_products[0]
        assert isinstance(product1, ProductData)
        assert product1.name == "Galaxy S24 Ultra (RAM 12GB, 256GB, Titanium Black)"
        assert product1.sku == "295649"
        assert product1.price_thb == 30400.0
        assert product1.stock_status == "Unknown"
    
    def test_price_parsing_with_poc_formats(self):
        """Test price parsing with formats from POC CSV data."""
        test_cases = [
            ("41,900", 41900.0),  # Comma-separated format from POC
            ("30,400", 30400.0),
            ("9,990", 9990.0),
            ("690", 690.0),  # No comma format
            (30400, 30400.0),  # Numeric format from JSON
            ("฿41,900", 41900.0),  # With Thai currency symbol
        ]
        
        for price_input, expected_output in test_cases:
            result = self.producer._parse_price(price_input)
            assert result == expected_output, f"Failed for input: {price_input}"
    
    def test_error_handling_in_transformation(self):
        """Test error handling during data transformation."""
        # Test with malformed JSON data
        malformed_data = {
            "products": [
                {
                    "sku": "TEST001",
                    "name": "Valid Product",
                    "price": 100
                },
                {
                    "sku": "TEST002",
                    "name": "Invalid Product",
                    "price": "invalid_price"  # This should cause validation error
                },
                {
                    # Missing required fields
                    "price": 200
                }
            ]
        }
        
        raw_products = self.producer._extract_products_from_json(malformed_data)
        validated_products = self.producer.validate_data(raw_products)
        
        # Should have processed valid products and logged errors for invalid ones
        assert len(raw_products) == 3  # All raw products extracted
        assert len(validated_products) == 1  # Only valid products validated
        assert self.producer.stats['validation_failures'] == 2  # Two validation failures
        assert len(self.producer.stats['errors']) == 2  # Two errors logged


class TestPOCDataCompatibility:
    """Test compatibility with actual POC CSV data."""
    
    def setup_method(self):
        """Setup with actual POC data."""
        self.poc_csv_path = "_dev-Document/250726-scriping-powerbuy/test_collect.csv"
        self.producer = DataProducer()
    
    def test_poc_csv_data_structure(self):
        """Test that we can read and understand POC CSV structure."""
        if not os.path.exists(self.poc_csv_path):
            print("   ⚠️  POC CSV file not found, skipping test")
            return
        
        with open(self.poc_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) > 0
        
        # Check expected columns
        expected_columns = {'Name', 'SKU', 'Price'}
        actual_columns = set(rows[0].keys())
        assert expected_columns.issubset(actual_columns)
        
        # Test sample row structure
        sample_row = rows[0]
        assert 'Name' in sample_row
        assert 'SKU' in sample_row
        assert 'Price' in sample_row
    
    def test_poc_data_to_product_model_conversion(self):
        """Test converting POC CSV data to our ProductData model."""
        if not os.path.exists(self.poc_csv_path):
            print("   ⚠️  POC CSV file not found, skipping test")
            return
        
        with open(self.poc_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Convert first few rows to ProductData
        converted_products = []
        for row in rows[:5]:  # Test first 5 rows
            try:
                # Parse price from POC format (with commas)
                price_thb = self.producer._parse_price(row['Price'])
                
                product = ProductData(
                    name=row['Name'].strip('"'),  # Remove quotes if present
                    sku=row['SKU'],
                    price_thb=price_thb,
                    stock_status="Unknown"  # POC didn't have stock status
                )
                converted_products.append(product)
            except Exception as e:
                print(f"Failed to convert row: {row}, Error: {e}")
        
        assert len(converted_products) > 0
        
        # Verify converted data
        product1 = converted_products[0]
        assert isinstance(product1, ProductData)
        assert product1.sku == "286634"
        assert product1.price_thb == 41900.0
        assert "Galaxy S23 Ultra" in product1.name
    
    def test_thai_text_handling(self):
        """Test handling of Thai text from POC data."""
        if not os.path.exists(self.poc_csv_path):
            print("   ⚠️  POC CSV file not found, skipping test")
            return
        
        # Find a row with Thai text
        thai_product_data = {
            "name": "ตู้เย็น 2 ประตู 13.9 คิว Inverter (สีดำ) รุ่น RT38CG6020B1ST",
            "sku": "289217",
            "price": "9,990"
        }
        
        # Test that Thai text is handled correctly
        price_thb = self.producer._parse_price(thai_product_data['price'])
        
        product = ProductData(
            name=thai_product_data['name'],
            sku=thai_product_data['sku'],
            price_thb=price_thb,
            stock_status="Unknown"
        )
        
        assert "ตู้เย็น" in product.name
        assert product.sku == "289217"
        assert product.price_thb == 9990.0


def run_all_tests():
    """Run all tests and display results."""
    print("Running Data Model Tests...")
    print("=" * 50)
    
    # Test 1: Basic model creation
    print("1. Testing basic model creation...")
    test_models = TestDataModels()
    test_models.setup_method()
    
    try:
        test_models.test_raw_product_data_creation()
        test_models.test_product_data_validation()
        print("   ✅ Basic model creation tests passed")
    except Exception as e:
        print(f"   ❌ Basic model creation tests failed: {e}")
    
    # Test 2: Validation rules
    print("2. Testing validation rules...")
    try:
        test_models.test_product_data_price_validation()
        test_models.test_stock_status_normalization()
        print("   ✅ Validation rules tests passed")
    except Exception as e:
        print(f"   ❌ Validation rules tests failed: {e}")
    
    # Test 3: Data transformation
    print("3. Testing data transformation...")
    test_transform = TestDataTransformation()
    test_transform.setup_method()
    
    try:
        test_transform.test_json_to_raw_product_transformation()
        test_transform.test_raw_to_validated_product_transformation()
        test_transform.test_price_parsing_with_poc_formats()
        print("   ✅ Data transformation tests passed")
    except Exception as e:
        print(f"   ❌ Data transformation tests failed: {e}")
    
    # Test 4: POC compatibility
    print("4. Testing POC data compatibility...")
    test_poc = TestPOCDataCompatibility()
    test_poc.setup_method()
    
    try:
        test_poc.test_poc_csv_data_structure()
        test_poc.test_poc_data_to_product_model_conversion()
        test_poc.test_thai_text_handling()
        print("   ✅ POC compatibility tests passed")
    except Exception as e:
        print(f"   ❌ POC compatibility tests failed: {e}")
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    run_all_tests()
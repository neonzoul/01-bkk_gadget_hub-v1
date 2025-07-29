"""
Test script for DataProducer class functionality.
Tests the basic JSON parsing and batch processing capabilities.
"""

import json
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import the DataProducer class
from src.producers.data_producer import DataProducer

def create_test_data():
    """Create test JSON files in the raw_data directory."""
    # Ensure test directory exists
    test_dir = "raw_data/search_results"
    os.makedirs(test_dir, exist_ok=True)
    
    # Copy the sample data to test directory
    sample_file = "_Outcome/iphone-2507-scrapegraphai.json"
    if os.path.exists(sample_file):
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        
        # Create test file
        test_file = os.path.join(test_dir, "test_iphone_data.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print(f"Created test file: {test_file}")
        return True
    else:
        print(f"Sample file not found: {sample_file}")
        return False

def test_data_producer():
    """Test the DataProducer class functionality."""
    print("Testing DataProducer class...")
    
    # Create test data
    if not create_test_data():
        print("Failed to create test data")
        return
    
    # Initialize DataProducer
    producer = DataProducer()
    
    # Test 1: Load raw data
    print("\n1. Testing load_raw_data()...")
    raw_data = producer.load_raw_data()
    print(f"Loaded {len(raw_data)} JSON files")
    
    if raw_data:
        print(f"First file keys: {list(raw_data[0].keys())}")
        if 'products' in raw_data[0]:
            print(f"Number of products in first file: {len(raw_data[0]['products'])}")
    
    # Test 2: Process products
    print("\n2. Testing process_products()...")
    raw_products = producer.process_products(raw_data)
    print(f"Extracted {len(raw_products)} raw products")
    
    if raw_products:
        print(f"First product: {raw_products[0].name} - SKU: {raw_products[0].sku} - Price: {raw_products[0].price}")
    
    # Test 3: Validate data
    print("\n3. Testing validate_data()...")
    validated_products = producer.validate_data(raw_products)
    print(f"Successfully validated {len(validated_products)} products")
    
    if validated_products:
        print(f"First validated product: {validated_products[0].name} - Price: {validated_products[0].price_thb} THB")
    
    # Test 4: Get processing summary
    print("\n4. Testing get_processing_summary()...")
    summary = producer.get_processing_summary()
    print(f"Processing Summary:")
    print(f"  Files processed: {summary.total_files_processed}")
    print(f"  Products extracted: {summary.total_products_extracted}")
    print(f"  Successful validations: {summary.successful_validations}")
    print(f"  Validation failures: {summary.validation_failures}")
    
    if producer.stats['errors']:
        print(f"  Errors encountered: {len(producer.stats['errors'])}")
        for error in producer.stats['errors'][:3]:  # Show first 3 errors
            print(f"    - {error}")
    
    print("\nDataProducer test completed successfully!")

if __name__ == "__main__":
    test_data_producer()
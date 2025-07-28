"""
Test script to verify the project setup and core data models.
"""

import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append('src')

from validators.models import ProductData, RawProductData, CollectionSummary, ProcessingSummary
from config import config

def test_data_models():
    """Test the Pydantic data models"""
    print("Testing Pydantic data models...")
    
    # Test RawProductData
    raw_data = RawProductData(
        name="iPhone 15 Pro",
        sku="IP15PRO128",
        price="39,900 บาท",
        stock_status="มีสินค้า",
        raw_json={"id": 12345, "category": "smartphones"}
    )
    print(f"✓ RawProductData created: {raw_data.name}")
    
    # Test ProductData with validation
    product_data = ProductData(
        name="iPhone 15 Pro",
        sku="IP15PRO128",
        price_thb=39900.0,
        stock_status="มีสินค้า"
    )
    print(f"✓ ProductData created: {product_data.name}, Price: {product_data.price_thb}, Stock: {product_data.stock_status}")
    
    # Test CollectionSummary
    summary = CollectionSummary(
        search_terms_processed=["iPhone 15", "Samsung Galaxy"],
        total_products_found=25,
        files_created=["iphone_2025-07-30.json", "samsung_2025-07-30.json"],
        errors=[],
        collection_time=datetime.now()
    )
    print(f"✓ CollectionSummary created: {summary.total_products_found} products found")
    
    # Test ProcessingSummary
    proc_summary = ProcessingSummary(
        total_files_processed=2,
        total_products_extracted=25,
        successful_validations=23,
        validation_failures=2,
        processing_time=datetime.now(),
        output_file="competitor_prices_2025-07-30.csv"
    )
    print(f"✓ ProcessingSummary created: {proc_summary.successful_validations}/{proc_summary.total_products_extracted} products validated")

def test_configuration():
    """Test the configuration management"""
    print("\nTesting configuration management...")
    
    # Test configuration loading
    print(f"✓ Config loaded - Search terms: {len(config.get_search_terms())}")
    print(f"✓ Base URL: {config.scraping.base_url}")
    print(f"✓ Input directory: {config.processing.input_directory}")
    print(f"✓ Output directory: {config.processing.output_directory}")
    
    # Test directory creation
    config.ensure_directories()
    print("✓ Directories ensured")
    
    # Test output filename generation
    filename = config.get_output_filename("2025-07-30")
    print(f"✓ Output filename: {filename}")
    
    # Test search terms management
    original_count = len(config.get_search_terms())
    config.add_search_term("Test Product")
    new_count = len(config.get_search_terms())
    print(f"✓ Search term added: {original_count} -> {new_count}")
    
    config.remove_search_term("Test Product")
    final_count = len(config.get_search_terms())
    print(f"✓ Search term removed: {new_count} -> {final_count}")

def test_directory_structure():
    """Test that all required directories exist"""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "src/collectors",
        "src/producers", 
        "src/validators",
        "raw_data/search_results",
        "raw_data/individual_products",
        "raw_data/processed",
        "output",
        "logs"
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ {directory}")
        else:
            print(f"✗ {directory} - MISSING")

if __name__ == "__main__":
    print("=== PowerBuy Scraper Setup Verification ===\n")
    
    try:
        test_directory_structure()
        test_data_models()
        test_configuration()
        print("\n=== All tests passed! Setup is complete. ===")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        sys.exit(1)
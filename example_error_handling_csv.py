#!/usr/bin/env python3
"""
Example usage of enhanced DataProducer with error handling and CSV export.
Demonstrates the implementation of task 7: Add error handling and CSV enhancement.
"""

import os
import json
import logging
from datetime import datetime

# Setup logging to see error handling in action
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Demonstrate enhanced DataProducer functionality."""
    
    print("Enhanced DataProducer with Error Handling and CSV Export")
    print("=" * 60)
    
    try:
        # Import the enhanced DataProducer
        from src.producers.data_producer import DataProducer
        
        # Initialize with default directories
        producer = DataProducer()
        print("✓ DataProducer initialized with enhanced error handling")
        
        # Check if we have any raw data to process
        if not os.path.exists("raw_data/search_results"):
            print("⚠️  No raw data directory found. Creating sample data...")
            create_sample_data()
        
        # Process complete pipeline with error handling
        try:
            output_path, summary = producer.process_complete_pipeline()
            
            print(f"\n✓ Processing completed successfully!")
            print(f"  Output CSV: {output_path}")
            print(f"  Files processed: {summary.total_files_processed}")
            print(f"  Products extracted: {summary.total_products_extracted}")
            print(f"  Successful validations: {summary.successful_validations}")
            print(f"  Validation failures: {summary.validation_failures}")
            
            # Show detailed statistics
            stats = producer.get_detailed_stats()
            print(f"\n📊 Detailed Statistics:")
            print(f"  File processing success rate: {stats['file_processing']['success_rate']:.1f}%")
            print(f"  Data validation success rate: {stats['data_validation']['success_rate']:.1f}%")
            print(f"  Total errors encountered: {stats['errors_and_warnings']['total_errors']}")
            print(f"  Total warnings: {stats['errors_and_warnings']['total_warnings']}")
            
            if stats['errors_and_warnings']['error_details']:
                print(f"\n⚠️  Recent errors:")
                for error in stats['errors_and_warnings']['error_details'][-3:]:
                    print(f"    - {error}")
            
            # Verify CSV output
            if os.path.exists(output_path):
                import pandas as pd
                df = pd.read_csv(output_path, encoding='utf-8')
                print(f"\n📄 CSV Output Preview:")
                print(f"  Rows: {len(df)}")
                print(f"  Columns: {list(df.columns)}")
                if len(df) > 0:
                    print(f"  Sample data:")
                    print(df.head(3).to_string(index=False))
            
        except Exception as e:
            print(f"✗ Pipeline failed: {str(e)}")
            
            # Show error details from producer
            stats = producer.get_detailed_stats()
            if stats['errors_and_warnings']['error_details']:
                print(f"\nError details:")
                for error in stats['errors_and_warnings']['error_details'][-5:]:
                    print(f"  - {error}")
    
    except ImportError as e:
        print(f"✗ Import error: {str(e)}")
        print("Make sure all required modules are installed and available.")
    
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

def create_sample_data():
    """Create sample data for demonstration."""
    
    # Ensure directories exist
    os.makedirs("raw_data/search_results", exist_ok=True)
    
    # Create sample JSON data
    sample_data = {
        "products": [
            {
                "name": "iPhone 15 Pro Max 256GB",
                "sku": "IP15PM256",
                "price": "45,900",
                "stock_status": "In Stock"
            },
            {
                "name": "Samsung Galaxy S24 Ultra 512GB",
                "sku": "SGS24U512",
                "price": "42900.00",
                "stock_status": "มีสินค้า"
            },
            {
                "name": "MacBook Air M3 13-inch",
                "sku": "MBA13M3",
                "price": "39,900",
                "stock_status": "Available"
            }
        ]
    }
    
    # Save sample data
    sample_file = "raw_data/search_results/sample_products.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Created sample data: {sample_file}")
    
    # Create a file with errors to demonstrate error handling
    error_data = {
        "products": [
            {
                "name": "Product with invalid price",
                "sku": "INVALID001",
                "price": "not_a_number",
                "stock_status": "In Stock"
            },
            {
                # Missing name field
                "sku": "MISSING001",
                "price": "1000",
                "stock_status": "Available"
            }
        ]
    }
    
    error_file = "raw_data/search_results/error_test.json"
    with open(error_file, 'w', encoding='utf-8') as f:
        json.dump(error_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Created error test data: {error_file}")

if __name__ == "__main__":
    main()
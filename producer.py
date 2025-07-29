"""
Main producer script demonstrating DataProducer usage.
This script shows how to use the DataProducer class to process raw JSON data.
"""

import logging
from src.producers.data_producer import DataProducer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function demonstrating DataProducer usage."""
    print("PowerBuy Data Producer")
    print("=" * 50)
    
    # Initialize the DataProducer
    producer = DataProducer()
    
    # Step 1: Load raw JSON data from input directory
    print("Step 1: Loading raw JSON data...")
    raw_data = producer.load_raw_data()
    
    if not raw_data:
        print("No JSON files found in input directory. Please add JSON files to process.")
        return
    
    # Step 2: Process products from raw data
    print("Step 2: Processing products...")
    raw_products = producer.process_products(raw_data)
    
    # Step 3: Validate and clean the data
    print("Step 3: Validating data...")
    validated_products = producer.validate_data(raw_products)
    
    # Step 4: Display processing summary
    print("Step 4: Processing Summary")
    print("-" * 30)
    summary = producer.get_processing_summary()
    
    print(f"Files processed: {summary.total_files_processed}")
    print(f"Products extracted: {summary.total_products_extracted}")
    print(f"Successful validations: {summary.successful_validations}")
    print(f"Validation failures: {summary.validation_failures}")
    
    if producer.stats['errors']:
        print(f"Errors encountered: {len(producer.stats['errors'])}")
        print("Recent errors:")
        for error in producer.stats['errors'][-3:]:  # Show last 3 errors
            print(f"  - {error}")
    
    # Display sample products
    if validated_products:
        print(f"\nSample products (showing first 5):")
        for i, product in enumerate(validated_products[:5], 1):
            print(f"{i}. {product.name}")
            print(f"   SKU: {product.sku}")
            print(f"   Price: {product.price_thb:,.2f} THB")
            print(f"   Stock: {product.stock_status}")
            print()
    
    print("Processing completed successfully!")

if __name__ == "__main__":
    main()
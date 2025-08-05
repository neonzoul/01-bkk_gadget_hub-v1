"""
Script to run the producer component for the complete dataset.
Processes all collected JSON data through DataProducer with deduplication.
"""

import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Set
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

from src.producers.data_producer import DataProducer
from src.validators.models import ProductData
from config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/producer_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CompleteDatasetProcessor:
    """
    Processes the complete dataset with deduplication and aggregation.
    """
    
    def __init__(self):
        self.producer = DataProducer()
        self.deduplication_stats = {
            'total_products_before_dedup': 0,
            'total_products_after_dedup': 0,
            'duplicates_removed': 0,
            'dedup_criteria_used': []
        }
    
    def deduplicate_products(self, products: List[ProductData]) -> List[ProductData]:
        """
        Remove duplicate products based on SKU and name similarity.
        
        Args:
            products: List of ProductData objects
            
        Returns:
            Deduplicated list of ProductData objects
        """
        logger.info(f"Starting deduplication process for {len(products)} products")
        
        self.deduplication_stats['total_products_before_dedup'] = len(products)
        
        # Track seen products using multiple criteria
        seen_skus: Set[str] = set()
        seen_names: Set[str] = set()
        deduplicated_products: List[ProductData] = []
        
        for product in products:
            is_duplicate = False
            duplicate_reason = []
            
            # Check for SKU duplicates
            if product.sku in seen_skus:
                is_duplicate = True
                duplicate_reason.append(f"SKU '{product.sku}' already exists")
            
            # Check for exact name duplicates
            normalized_name = product.name.strip().lower()
            if normalized_name in seen_names:
                is_duplicate = True
                duplicate_reason.append(f"Name '{product.name}' already exists")
            
            if is_duplicate:
                logger.debug(f"Removing duplicate product: {product.name} (SKU: {product.sku}) - {', '.join(duplicate_reason)}")
                self.deduplication_stats['duplicates_removed'] += 1
            else:
                # Add to seen sets and keep the product
                seen_skus.add(product.sku)
                seen_names.add(normalized_name)
                deduplicated_products.append(product)
        
        self.deduplication_stats['total_products_after_dedup'] = len(deduplicated_products)
        self.deduplication_stats['dedup_criteria_used'] = ['SKU', 'Product Name']
        
        logger.info(f"Deduplication completed:")
        logger.info(f"  - Products before: {self.deduplication_stats['total_products_before_dedup']}")
        logger.info(f"  - Products after: {self.deduplication_stats['total_products_after_dedup']}")
        logger.info(f"  - Duplicates removed: {self.deduplication_stats['duplicates_removed']}")
        
        return deduplicated_products
    
    def aggregate_search_results(self, input_directories: List[str]) -> List[Dict]:
        """
        Aggregate raw data from multiple directories.
        
        Args:
            input_directories: List of directories containing JSON files
            
        Returns:
            Combined list of raw data from all directories
        """
        all_raw_data = []
        
        for directory in input_directories:
            if os.path.exists(directory):
                logger.info(f"Processing directory: {directory}")
                raw_data = self.producer.load_raw_data(directory)
                all_raw_data.extend(raw_data)
                logger.info(f"Loaded {len(raw_data)} files from {directory}")
            else:
                logger.warning(f"Directory not found: {directory}")
        
        logger.info(f"Total raw data files aggregated: {len(all_raw_data)}")
        return all_raw_data
    
    def process_complete_dataset(self) -> str:
        """
        Process the complete dataset with aggregation and deduplication.
        
        Returns:
            Path to the output CSV file
        """
        logger.info("Starting complete dataset processing")
        
        # Define input directories to process
        input_directories = [
            config.processing.input_directory,  # raw_data/search_results
            "raw_data/search_results/2025-07-30",
            "raw_data/search_results/2025-07-31"
        ]
        
        try:
            # Step 1: Aggregate raw data from multiple sources
            logger.info("Step 1: Aggregating raw data from multiple directories")
            all_raw_data = self.aggregate_search_results(input_directories)
            
            if not all_raw_data:
                raise RuntimeError("No raw data found in any input directory")
            
            # Step 2: Extract products from aggregated data
            logger.info("Step 2: Extracting products from aggregated data")
            raw_products = self.producer.process_products(all_raw_data)
            
            if not raw_products:
                raise RuntimeError("No products extracted from raw data")
            
            # Step 3: Validate data
            logger.info("Step 3: Validating extracted product data")
            validated_products = self.producer.validate_data(raw_products)
            
            if not validated_products:
                raise RuntimeError("No products passed validation")
            
            # Step 4: Deduplicate products
            logger.info("Step 4: Deduplicating products")
            deduplicated_products = self.deduplicate_products(validated_products)
            
            if not deduplicated_products:
                raise RuntimeError("No products remaining after deduplication")
            
            # Step 5: Export to CSV
            logger.info("Step 5: Exporting to CSV")
            output_filename = f"competitor_prices_complete_{datetime.now().strftime('%Y-%m-%d')}.csv"
            output_path = self.producer.export_csv(deduplicated_products, output_filename)
            
            # Step 6: Generate comprehensive summary
            self.generate_processing_summary(output_path, len(deduplicated_products))
            
            logger.info(f"Complete dataset processing finished successfully")
            logger.info(f"Output file: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Complete dataset processing failed: {str(e)}")
            raise
    
    def generate_processing_summary(self, output_path: str, final_product_count: int):
        """
        Generate and log comprehensive processing summary.
        
        Args:
            output_path: Path to output CSV file
            final_product_count: Final number of products in output
        """
        logger.info("=" * 60)
        logger.info("COMPLETE DATASET PROCESSING SUMMARY")
        logger.info("=" * 60)
        
        # Get detailed stats from producer
        detailed_stats = self.producer.get_detailed_stats()
        
        logger.info(f"File Processing:")
        logger.info(f"  - Files processed: {detailed_stats['file_processing']['files_processed']}")
        logger.info(f"  - Files failed: {detailed_stats['file_processing']['files_failed']}")
        logger.info(f"  - File success rate: {detailed_stats['file_processing']['success_rate']:.1f}%")
        
        logger.info(f"Product Extraction:")
        logger.info(f"  - Products extracted: {detailed_stats['product_extraction']['products_extracted']}")
        logger.info(f"  - Extraction errors: {detailed_stats['product_extraction']['extraction_errors']}")
        
        logger.info(f"Data Validation:")
        logger.info(f"  - Successful validations: {detailed_stats['data_validation']['successful_validations']}")
        logger.info(f"  - Validation failures: {detailed_stats['data_validation']['validation_failures']}")
        logger.info(f"  - Validation success rate: {detailed_stats['data_validation']['success_rate']:.1f}%")
        
        logger.info(f"Deduplication:")
        logger.info(f"  - Products before dedup: {self.deduplication_stats['total_products_before_dedup']}")
        logger.info(f"  - Products after dedup: {self.deduplication_stats['total_products_after_dedup']}")
        logger.info(f"  - Duplicates removed: {self.deduplication_stats['duplicates_removed']}")
        logger.info(f"  - Dedup criteria: {', '.join(self.deduplication_stats['dedup_criteria_used'])}")
        
        logger.info(f"Final Output:")
        logger.info(f"  - Output file: {output_path}")
        logger.info(f"  - Final product count: {final_product_count}")
        logger.info(f"  - File size: {os.path.getsize(output_path) / 1024:.1f} KB")
        
        # Log any errors or warnings
        if detailed_stats['errors_and_warnings']['total_errors'] > 0:
            logger.warning(f"Total errors encountered: {detailed_stats['errors_and_warnings']['total_errors']}")
            logger.warning("Recent errors:")
            for error in detailed_stats['errors_and_warnings']['error_details']:
                logger.warning(f"  - {error}")
        
        if detailed_stats['errors_and_warnings']['total_warnings'] > 0:
            logger.info(f"Total warnings: {detailed_stats['errors_and_warnings']['total_warnings']}")
        
        logger.info("=" * 60)


def main():
    """Main function to run complete dataset processing."""
    print("PowerBuy Complete Dataset Processor")
    print("=" * 50)
    
    # Ensure required directories exist
    config.ensure_directories()
    
    try:
        # Initialize processor
        processor = CompleteDatasetProcessor()
        
        # Process complete dataset
        output_path = processor.process_complete_dataset()
        
        print(f"\n✅ Processing completed successfully!")
        print(f"📄 Output file: {output_path}")
        print(f"📊 Check the log file for detailed statistics")
        
        # Display file info
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"📁 File size: {file_size / 1024:.1f} KB")
            
            # Count lines in CSV (excluding header)
            with open(output_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for line in f) - 1  # Subtract header
            print(f"📈 Products in CSV: {line_count}")
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        print(f"\n❌ Processing failed: {str(e)}")
        print("📋 Check the log file for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()
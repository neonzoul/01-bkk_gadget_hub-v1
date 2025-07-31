"""
DataProducer class for processing raw JSON files from PowerBuy scraping.
Handles batch processing and data extraction from PowerBuy API response structure.
Enhanced with comprehensive error handling and Pandas CSV export functionality.
"""

import json
import os
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..validators.models import RawProductData, ProductData, ProcessingSummary
from ..parsers.powerbuy_parser import PowerBuyJSONParser, DataTransformer
from config import config


class DataProducer:
    """
    Producer component that processes raw JSON data into clean, validated CSV output.
    Handles PowerBuy API response structure and batch processing of multiple files.
    """
    
    def __init__(self, input_directory: str = None, output_directory: str = None):
        """
        Initialize DataProducer with configurable directories and enhanced error handling.
        
        Args:
            input_directory: Directory containing raw JSON files
            output_directory: Directory for processed output files
        """
        try:
            self.input_directory = input_directory or config.processing.input_directory
            self.output_directory = output_directory or config.processing.output_directory
            
            # Ensure directories exist with error handling
            self._ensure_directories()
            
            # Setup logging
            self.logger = logging.getLogger(__name__)
            
            # Initialize specialized parsers
            self.json_parser = PowerBuyJSONParser()
            self.data_transformer = DataTransformer()
            
            # Processing statistics with enhanced tracking
            self.stats = {
                'files_processed': 0,
                'files_failed': 0,
                'products_extracted': 0,
                'successful_validations': 0,
                'validation_failures': 0,
                'json_parse_errors': 0,
                'csv_export_errors': 0,
                'errors': [],
                'warnings': []
            }
            
            self.logger.info(f"DataProducer initialized - Input: {self.input_directory}, Output: {self.output_directory}")
            
        except Exception as e:
            # Critical initialization error
            error_msg = f"Failed to initialize DataProducer: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _ensure_directories(self) -> None:
        """
        Ensure required directories exist with comprehensive error handling.
        
        Raises:
            RuntimeError: If directories cannot be created
        """
        directories = [self.input_directory, self.output_directory]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                
                # Verify directory is writable
                test_file = os.path.join(directory, '.test_write')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                except Exception as e:
                    raise RuntimeError(f"Directory {directory} is not writable: {str(e)}")
                    
            except Exception as e:
                raise RuntimeError(f"Failed to create directory {directory}: {str(e)}")
    
    def load_raw_data(self, input_directory: str = None) -> List[Dict[str, Any]]:
        """
        Load all JSON files from the input directory with enhanced error handling.
        
        Args:
            input_directory: Optional override for input directory
            
        Returns:
            List of dictionaries containing raw JSON data from all files
            
        Raises:
            RuntimeError: If directory access fails critically
        """
        directory = input_directory or self.input_directory
        raw_data = []
        
        try:
            self.logger.info(f"Loading raw data from directory: {directory}")
            
            # Verify directory exists and is accessible
            if not os.path.exists(directory):
                raise RuntimeError(f"Input directory does not exist: {directory}")
            
            if not os.path.isdir(directory):
                raise RuntimeError(f"Input path is not a directory: {directory}")
            
            # Find all JSON files in the directory
            try:
                json_files = list(Path(directory).glob("*.json"))
            except Exception as e:
                raise RuntimeError(f"Failed to scan directory {directory}: {str(e)}")
            
            if not json_files:
                self.logger.warning(f"No JSON files found in directory: {directory}")
                return raw_data
            
            self.logger.info(f"Found {len(json_files)} JSON files to process")
            
            # Process each JSON file with individual error handling
            for json_file in json_files:
                try:
                    self._load_single_json_file(json_file, raw_data)
                    
                except Exception as e:
                    # Log error but continue with other files
                    error_msg = f"Failed to process file {json_file}: {str(e)}"
                    self.logger.error(error_msg)
                    self.stats['files_failed'] += 1
                    self.stats['errors'].append(error_msg)
                    continue
            
            success_rate = (self.stats['files_processed'] / len(json_files)) * 100 if json_files else 0
            self.logger.info(f"File loading completed: {self.stats['files_processed']}/{len(json_files)} files successful ({success_rate:.1f}%)")
            
            return raw_data
            
        except RuntimeError:
            # Re-raise runtime errors (critical failures)
            raise
        except Exception as e:
            # Wrap unexpected errors
            error_msg = f"Unexpected error loading raw data: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _load_single_json_file(self, json_file: Path, raw_data: List[Dict[str, Any]]) -> None:
        """
        Load a single JSON file with comprehensive error handling.
        
        Args:
            json_file: Path to JSON file
            raw_data: List to append loaded data to
            
        Raises:
            Various exceptions for different failure modes
        """
        self.logger.debug(f"Processing file: {json_file}")
        
        # Check file accessibility
        if not os.access(json_file, os.R_OK):
            raise PermissionError(f"Cannot read file: {json_file}")
        
        # Check file size (prevent loading extremely large files)
        file_size = os.path.getsize(json_file)
        max_size = 100 * 1024 * 1024  # 100MB limit
        if file_size > max_size:
            raise ValueError(f"File too large ({file_size / 1024 / 1024:.1f}MB): {json_file}")
        
        try:
            # Load JSON with proper encoding handling
            with open(json_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            # Validate JSON structure
            if not isinstance(file_data, (dict, list)):
                raise ValueError(f"Invalid JSON structure (not dict or list): {type(file_data)}")
            
            # Add metadata about the source file
            if isinstance(file_data, dict):
                file_data['_source_file'] = str(json_file)
                file_data['_processed_at'] = datetime.now().isoformat()
                file_data['_file_size'] = file_size
            else:
                # For list format, wrap in metadata dict
                file_data = {
                    'products': file_data,
                    '_source_file': str(json_file),
                    '_processed_at': datetime.now().isoformat(),
                    '_file_size': file_size
                }
            
            raw_data.append(file_data)
            self.stats['files_processed'] += 1
            
            self.logger.debug(f"Successfully loaded file: {json_file} ({file_size} bytes)")
            
        except json.JSONDecodeError as e:
            self.stats['json_parse_errors'] += 1
            raise ValueError(f"Invalid JSON format: {str(e)} at line {e.lineno}, column {e.colno}")
        
        except UnicodeDecodeError as e:
            raise ValueError(f"Encoding error: {str(e)}")
        
        except MemoryError:
            raise ValueError(f"File too large to load into memory: {json_file}")
        
        except Exception as e:
            # Catch any other file-related errors
            raise RuntimeError(f"Unexpected error loading file: {str(e)}")
    
    def process_products(self, raw_data: List[Dict[str, Any]]) -> List[RawProductData]:
        """
        Process raw JSON data to extract product information with enhanced error handling.
        Uses specialized PowerBuy JSON parser for robust data extraction.
        
        Args:
            raw_data: List of raw JSON data from files
            
        Returns:
            List of RawProductData objects extracted from all files
        """
        all_products = []
        
        if not raw_data:
            self.logger.warning("No raw data provided for processing")
            return all_products
        
        self.logger.info(f"Processing {len(raw_data)} raw data files")
        
        for i, file_data in enumerate(raw_data):
            source_file = file_data.get('_source_file', f'file_{i}')
            
            try:
                # Validate file data structure
                if not isinstance(file_data, dict):
                    raise ValueError(f"Invalid file data structure: {type(file_data)}")
                
                # Use specialized parser for robust extraction
                products = self.json_parser.extract_products_from_json(file_data, source_file)
                
                if products:
                    all_products.extend(products)
                    self.logger.debug(f"Extracted {len(products)} products from {source_file}")
                else:
                    warning_msg = f"No products found in {source_file}"
                    self.logger.warning(warning_msg)
                    self.stats['warnings'].append(warning_msg)
                
            except Exception as e:
                error_msg = f"Error processing file {source_file}: {str(e)}"
                self.logger.error(error_msg)
                self.stats['errors'].append(error_msg)
                continue
        
        self.stats['products_extracted'] = len(all_products)
        
        # Log extraction summary
        parser_stats = self.json_parser.get_extraction_stats()
        self.logger.info(f"Product extraction completed:")
        self.logger.info(f"  - Total products extracted: {len(all_products)}")
        self.logger.info(f"  - Extraction success rate: {parser_stats['success_rate']:.1f}%")
        self.logger.info(f"  - Files with errors: {len([e for e in self.stats['errors'] if 'processing file' in e])}")
        
        return all_products
    
    def validate_data(self, raw_products: List[RawProductData]) -> List[ProductData]:
        """
        Validate and clean raw product data using enhanced data transformer.
        
        Args:
            raw_products: List of RawProductData objects
            
        Returns:
            List of validated ProductData objects
        """
        if not raw_products:
            self.logger.warning("No raw products provided for validation")
            return []
        
        self.logger.info(f"Validating {len(raw_products)} raw products")
        
        try:
            # Use specialized data transformer for robust validation
            validated_products = self.data_transformer.transform_to_product_data(raw_products)
            
            # Update statistics from transformer
            transformer_stats = self.data_transformer.get_transformation_stats()
            self.stats['successful_validations'] = transformer_stats['transformations_successful']
            self.stats['validation_failures'] = transformer_stats['transformation_errors']
            
            # Add transformer errors to our error list
            self.stats['errors'].extend(transformer_stats['error_details'])
            
            # Log validation summary
            success_rate = transformer_stats['success_rate']
            self.logger.info(f"Data validation completed:")
            self.logger.info(f"  - Successfully validated: {len(validated_products)} products")
            self.logger.info(f"  - Validation success rate: {success_rate:.1f}%")
            self.logger.info(f"  - Validation failures: {transformer_stats['transformation_errors']}")
            
            return validated_products
            
        except Exception as e:
            error_msg = f"Critical error during data validation: {str(e)}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            raise RuntimeError(error_msg) from e
    
    def export_csv(self, products: List[ProductData], output_filename: str = None) -> str:
        """
        Export validated product data to CSV using Pandas with comprehensive error handling.
        
        Args:
            products: List of validated ProductData objects
            output_filename: Optional custom filename (defaults to date-based name)
            
        Returns:
            Path to the exported CSV file
            
        Raises:
            RuntimeError: If CSV export fails
        """
        if not products:
            raise ValueError("No products provided for CSV export")
        
        try:
            # Generate output filename if not provided
            if not output_filename:
                output_filename = config.get_output_filename()
            
            # Ensure filename has .csv extension
            if not output_filename.endswith('.csv'):
                output_filename += '.csv'
            
            output_path = os.path.join(self.output_directory, output_filename)
            
            self.logger.info(f"Exporting {len(products)} products to CSV: {output_path}")
            
            # Convert ProductData objects to DataFrame
            df = self._create_dataframe_from_products(products)
            
            # Export to CSV with proper encoding and formatting
            self._export_dataframe_to_csv(df, output_path)
            
            # Verify export success
            self._verify_csv_export(output_path, len(products))
            
            self.logger.info(f"CSV export completed successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.stats['csv_export_errors'] += 1
            error_msg = f"CSV export failed: {str(e)}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _create_dataframe_from_products(self, products: List[ProductData]) -> pd.DataFrame:
        """
        Create Pandas DataFrame from ProductData objects with proper formatting.
        
        Args:
            products: List of ProductData objects
            
        Returns:
            Formatted Pandas DataFrame
        """
        try:
            # Convert products to dictionary format
            data_rows = []
            for product in products:
                row = {
                    'Name': product.name,
                    'SKU': product.sku,
                    'Price': product.price_thb,
                    'Stock Status': product.stock_status
                }
                
                # Add optional fields if present
                if hasattr(product, 'brand') and product.brand:
                    row['Brand'] = product.brand
                if hasattr(product, 'category') and product.category:
                    row['Category'] = product.category
                if hasattr(product, 'data_source') and product.data_source:
                    row['Source'] = product.data_source
                
                data_rows.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(data_rows)
            
            # Format price column
            if 'Price' in df.columns:
                df['Price'] = df['Price'].apply(lambda x: f"{x:.2f}")
            
            # Sort by SKU for consistent output
            if 'SKU' in df.columns:
                df = df.sort_values('SKU')
            
            # Reset index
            df = df.reset_index(drop=True)
            
            self.logger.debug(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            raise RuntimeError(f"Failed to create DataFrame: {str(e)}")
    
    def _export_dataframe_to_csv(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Export DataFrame to CSV with proper encoding and error handling.
        
        Args:
            df: DataFrame to export
            output_path: Path for CSV output
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Export with UTF-8 encoding for Thai character support
            df.to_csv(
                output_path,
                index=False,
                encoding=config.processing.csv_encoding,
                quoting=1,  # Quote all fields to handle commas in product names
                escapechar='\\',  # Escape character for special cases
                lineterminator='\n'  # Consistent line endings
            )
            
        except PermissionError as e:
            raise RuntimeError(f"Permission denied writing to {output_path}: {str(e)}")
        except UnicodeEncodeError as e:
            raise RuntimeError(f"Encoding error writing CSV: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error writing CSV: {str(e)}")
    
    def _verify_csv_export(self, output_path: str, expected_rows: int) -> None:
        """
        Verify CSV export was successful by checking file and row count.
        
        Args:
            output_path: Path to exported CSV
            expected_rows: Expected number of data rows
        """
        try:
            # Check file exists
            if not os.path.exists(output_path):
                raise RuntimeError("CSV file was not created")
            
            # Check file size
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise RuntimeError("CSV file is empty")
            
            # Verify row count by reading back
            try:
                verification_df = pd.read_csv(output_path, encoding=config.processing.csv_encoding)
                actual_rows = len(verification_df)
                
                if actual_rows != expected_rows:
                    self.logger.warning(f"Row count mismatch: expected {expected_rows}, got {actual_rows}")
                else:
                    self.logger.debug(f"CSV verification successful: {actual_rows} rows")
                    
            except Exception as e:
                self.logger.warning(f"Could not verify CSV content: {str(e)}")
            
        except Exception as e:
            raise RuntimeError(f"CSV verification failed: {str(e)}")
    
    def get_processing_summary(self, output_file: str = "") -> ProcessingSummary:
        """
        Generate a comprehensive summary of the processing results.
        
        Args:
            output_file: Path to output CSV file if available
            
        Returns:
            ProcessingSummary object with enhanced statistics
        """
        return ProcessingSummary(
            total_files_processed=self.stats['files_processed'],
            total_products_extracted=self.stats['products_extracted'],
            successful_validations=self.stats['successful_validations'],
            validation_failures=self.stats['validation_failures'],
            processing_time=datetime.now(),
            output_file=output_file
        )
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """
        Get detailed processing statistics including error details.
        
        Returns:
            Dictionary with comprehensive statistics
        """
        total_files_attempted = self.stats['files_processed'] + self.stats['files_failed']
        file_success_rate = (self.stats['files_processed'] / max(total_files_attempted, 1)) * 100
        
        total_validations_attempted = self.stats['successful_validations'] + self.stats['validation_failures']
        validation_success_rate = (self.stats['successful_validations'] / max(total_validations_attempted, 1)) * 100
        
        return {
            'file_processing': {
                'files_processed': self.stats['files_processed'],
                'files_failed': self.stats['files_failed'],
                'success_rate': file_success_rate,
                'json_parse_errors': self.stats['json_parse_errors']
            },
            'product_extraction': {
                'products_extracted': self.stats['products_extracted'],
                'extraction_errors': len([e for e in self.stats['errors'] if 'processing file' in e])
            },
            'data_validation': {
                'successful_validations': self.stats['successful_validations'],
                'validation_failures': self.stats['validation_failures'],
                'success_rate': validation_success_rate
            },
            'csv_export': {
                'export_errors': self.stats['csv_export_errors']
            },
            'errors_and_warnings': {
                'total_errors': len(self.stats['errors']),
                'total_warnings': len(self.stats['warnings']),
                'error_details': self.stats['errors'][-10:],  # Last 10 errors
                'warning_details': self.stats['warnings'][-10:]  # Last 10 warnings
            }
        }
    
    def reset_stats(self) -> None:
        """Reset processing statistics for a new run."""
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'products_extracted': 0,
            'successful_validations': 0,
            'validation_failures': 0,
            'json_parse_errors': 0,
            'csv_export_errors': 0,
            'errors': [],
            'warnings': []
        }
        
        # Reset parser and transformer stats
        if hasattr(self, 'json_parser'):
            self.json_parser.reset_stats()
        if hasattr(self, 'data_transformer'):
            self.data_transformer.reset_stats()
    
    def process_complete_pipeline(self, input_directory: str = None, output_filename: str = None) -> Tuple[str, ProcessingSummary]:
        """
        Execute the complete data processing pipeline with comprehensive error handling.
        
        Args:
            input_directory: Optional override for input directory
            output_filename: Optional custom output filename
            
        Returns:
            Tuple of (output_csv_path, processing_summary)
            
        Raises:
            RuntimeError: If pipeline fails critically
        """
        try:
            self.logger.info("Starting complete data processing pipeline")
            
            # Step 1: Load raw data
            raw_data = self.load_raw_data(input_directory)
            if not raw_data:
                raise RuntimeError("No raw data loaded - cannot proceed with pipeline")
            
            # Step 2: Extract products
            raw_products = self.process_products(raw_data)
            if not raw_products:
                raise RuntimeError("No products extracted - cannot proceed with pipeline")
            
            # Step 3: Validate data
            validated_products = self.validate_data(raw_products)
            if not validated_products:
                raise RuntimeError("No products validated - cannot proceed with pipeline")
            
            # Step 4: Export CSV
            output_path = self.export_csv(validated_products, output_filename)
            
            # Step 5: Generate summary
            summary = self.get_processing_summary(output_path)
            
            self.logger.info(f"Pipeline completed successfully: {len(validated_products)} products exported to {output_path}")
            return output_path, summary
            
        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            raise RuntimeError(error_msg) from e
"""
DataProducer class for processing raw JSON files from PowerBuy scraping.
Handles batch processing and data extraction from PowerBuy API response structure.
"""

import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..validators.models import RawProductData, ProductData, ProcessingSummary
from config import config


class DataProducer:
    """
    Producer component that processes raw JSON data into clean, validated CSV output.
    Handles PowerBuy API response structure and batch processing of multiple files.
    """
    
    def __init__(self, input_directory: str = None, output_directory: str = None):
        """
        Initialize DataProducer with configurable directories.
        
        Args:
            input_directory: Directory containing raw JSON files
            output_directory: Directory for processed output files
        """
        self.input_directory = input_directory or config.processing.input_directory
        self.output_directory = output_directory or config.processing.output_directory
        
        # Ensure directories exist
        os.makedirs(self.input_directory, exist_ok=True)
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Processing statistics
        self.stats = {
            'files_processed': 0,
            'products_extracted': 0,
            'successful_validations': 0,
            'validation_failures': 0,
            'errors': []
        }
    
    def load_raw_data(self, input_directory: str = None) -> List[Dict[str, Any]]:
        """
        Load all JSON files from the input directory.
        
        Args:
            input_directory: Optional override for input directory
            
        Returns:
            List of dictionaries containing raw JSON data from all files
        """
        directory = input_directory or self.input_directory
        raw_data = []
        
        self.logger.info(f"Loading raw data from directory: {directory}")
        
        # Find all JSON files in the directory
        json_files = list(Path(directory).glob("*.json"))
        
        if not json_files:
            self.logger.warning(f"No JSON files found in directory: {directory}")
            return raw_data
        
        for json_file in json_files:
            try:
                self.logger.debug(f"Processing file: {json_file}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                
                # Add metadata about the source file
                file_data['_source_file'] = str(json_file)
                file_data['_processed_at'] = datetime.now().isoformat()
                
                raw_data.append(file_data)
                self.stats['files_processed'] += 1
                
                self.logger.debug(f"Successfully loaded file: {json_file}")
                
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON in file {json_file}: {e}"
                self.logger.error(error_msg)
                self.stats['errors'].append(error_msg)
                
            except Exception as e:
                error_msg = f"Error loading file {json_file}: {e}"
                self.logger.error(error_msg)
                self.stats['errors'].append(error_msg)
        
        self.logger.info(f"Loaded {len(raw_data)} JSON files successfully")
        return raw_data
    
    def process_products(self, raw_data: List[Dict[str, Any]]) -> List[RawProductData]:
        """
        Process raw JSON data to extract product information.
        Handles PowerBuy API response structure with products array.
        
        Args:
            raw_data: List of raw JSON data from files
            
        Returns:
            List of RawProductData objects extracted from all files
        """
        all_products = []
        
        self.logger.info(f"Processing {len(raw_data)} raw data files")
        
        for file_data in raw_data:
            try:
                # Extract products from PowerBuy API response structure
                products = self._extract_products_from_json(file_data)
                all_products.extend(products)
                
                self.logger.debug(f"Extracted {len(products)} products from {file_data.get('_source_file', 'unknown file')}")
                
            except Exception as e:
                error_msg = f"Error processing file {file_data.get('_source_file', 'unknown')}: {e}"
                self.logger.error(error_msg)
                self.stats['errors'].append(error_msg)
        
        self.stats['products_extracted'] = len(all_products)
        self.logger.info(f"Total products extracted: {len(all_products)}")
        
        return all_products
    
    def _extract_products_from_json(self, json_data: Dict[str, Any]) -> List[RawProductData]:
        """
        Extract product data from PowerBuy API JSON response structure.
        
        Args:
            json_data: Raw JSON data from PowerBuy API
            
        Returns:
            List of RawProductData objects
        """
        products = []
        
        # Handle PowerBuy API response structure: {"products": [...]}
        if 'products' in json_data and isinstance(json_data['products'], list):
            for product_item in json_data['products']:
                try:
                    # Extract basic product information
                    raw_product = RawProductData(
                        name=product_item.get('name', ''),
                        sku=product_item.get('sku', ''),
                        price=str(product_item.get('price', '')) if product_item.get('price') is not None else None,
                        stock_status=product_item.get('stock_status', 'Unknown'),  # Default to Unknown if not provided
                        raw_json=product_item  # Store complete original data
                    )
                    
                    products.append(raw_product)
                    
                except Exception as e:
                    error_msg = f"Error extracting product data: {e}, Product: {product_item}"
                    self.logger.warning(error_msg)
                    self.stats['errors'].append(error_msg)
                    continue
        
        # Handle alternative JSON structures if needed
        elif isinstance(json_data, list):
            # Direct array of products
            for product_item in json_data:
                try:
                    raw_product = RawProductData(
                        name=product_item.get('name', ''),
                        sku=product_item.get('sku', ''),
                        price=str(product_item.get('price', '')) if product_item.get('price') is not None else None,
                        stock_status=product_item.get('stock_status', 'Unknown'),
                        raw_json=product_item
                    )
                    
                    products.append(raw_product)
                    
                except Exception as e:
                    error_msg = f"Error extracting product from array: {e}, Product: {product_item}"
                    self.logger.warning(error_msg)
                    self.stats['errors'].append(error_msg)
                    continue
        
        else:
            # Single product object
            if json_data.get('name') or json_data.get('sku'):
                try:
                    raw_product = RawProductData(
                        name=json_data.get('name', ''),
                        sku=json_data.get('sku', ''),
                        price=str(json_data.get('price', '')) if json_data.get('price') is not None else None,
                        stock_status=json_data.get('stock_status', 'Unknown'),
                        raw_json=json_data
                    )
                    
                    products.append(raw_product)
                    
                except Exception as e:
                    error_msg = f"Error extracting single product: {e}, Data: {json_data}"
                    self.logger.warning(error_msg)
                    self.stats['errors'].append(error_msg)
        
        return products
    
    def validate_data(self, raw_products: List[RawProductData]) -> List[ProductData]:
        """
        Validate and clean raw product data using Pydantic models.
        
        Args:
            raw_products: List of RawProductData objects
            
        Returns:
            List of validated ProductData objects
        """
        validated_products = []
        
        self.logger.info(f"Validating {len(raw_products)} raw products")
        
        for raw_product in raw_products:
            try:
                # Convert raw price string to float
                price_thb = self._parse_price(raw_product.price)
                
                # Create validated product data
                validated_product = ProductData(
                    name=raw_product.name.strip(),
                    sku=raw_product.sku.strip(),
                    price_thb=price_thb,
                    stock_status=raw_product.stock_status or 'Unknown'
                )
                
                validated_products.append(validated_product)
                self.stats['successful_validations'] += 1
                
            except Exception as e:
                error_msg = f"Validation failed for product {raw_product.sku}: {e}"
                self.logger.warning(error_msg)
                self.stats['validation_failures'] += 1
                self.stats['errors'].append(error_msg)
                continue
        
        self.logger.info(f"Successfully validated {len(validated_products)} products")
        return validated_products
    
    def _parse_price(self, price_str: Optional[str]) -> float:
        """
        Parse price string to float, handling various formats.
        
        Args:
            price_str: Raw price string from API
            
        Returns:
            Parsed price as float
            
        Raises:
            ValueError: If price cannot be parsed
        """
        if not price_str:
            raise ValueError("Price is empty or None")
        
        # Handle numeric values that are already numbers
        if isinstance(price_str, (int, float)):
            return float(price_str)
        
        # Clean price string - remove currency symbols, commas, spaces
        cleaned_price = str(price_str).strip()
        
        # Remove common currency symbols and formatting
        cleaned_price = cleaned_price.replace('฿', '').replace('THB', '').replace('Baht', '')
        cleaned_price = cleaned_price.replace(',', '').replace(' ', '')
        
        # Handle empty string after cleaning
        if not cleaned_price:
            raise ValueError("Price string is empty after cleaning")
        
        try:
            return float(cleaned_price)
        except ValueError:
            raise ValueError(f"Cannot convert price to float: {price_str}")
    
    def get_processing_summary(self) -> ProcessingSummary:
        """
        Generate a summary of the processing results.
        
        Returns:
            ProcessingSummary object with statistics
        """
        return ProcessingSummary(
            total_files_processed=self.stats['files_processed'],
            total_products_extracted=self.stats['products_extracted'],
            successful_validations=self.stats['successful_validations'],
            validation_failures=self.stats['validation_failures'],
            processing_time=datetime.now(),
            output_file=""  # Will be set when CSV is exported
        )
    
    def reset_stats(self) -> None:
        """Reset processing statistics for a new run."""
        self.stats = {
            'files_processed': 0,
            'products_extracted': 0,
            'successful_validations': 0,
            'validation_failures': 0,
            'errors': []
        }
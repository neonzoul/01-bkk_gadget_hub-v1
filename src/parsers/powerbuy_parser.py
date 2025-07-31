"""
PowerBuy JSON Parser - Data extraction functions for PowerBuy API responses.

This module provides specialized parsing functions to extract product data from PowerBuy API responses,
handle data transformation, and convert raw JSON to ProductData models with proper validation.
"""

import json
import re
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from src.validators.models import RawProductData, ProductData


class PriceParser:
    """
    Specialized price parsing utility for PowerBuy product prices.
    
    Handles various price formats including Thai Baht currency symbols,
    comma separators, and different string representations.
    """
    
    @staticmethod
    def parse_price(price_input: Union[str, int, float, None]) -> float:
        """
        Parse price from various input formats to standardized float.
        
        Supports formats:
        - Numeric: 49700, 49700.50
        - String with commas: "49,700", "49,700.50"
        - Thai currency: "฿49,700", "49700 THB", "49700 Baht"
        - Mixed formats: " ฿ 49,700.50 THB "
        
        Args:
            price_input: Raw price data from API
            
        Returns:
            Parsed price as float with 2 decimal precision
            
        Raises:
            ValueError: If price cannot be parsed or is invalid
        """
        if price_input is None:
            raise ValueError("Price is None")
        
        # Handle numeric values directly
        if isinstance(price_input, (int, float)):
            if price_input < 0:
                raise ValueError(f"Price cannot be negative: {price_input}")
            return round(float(price_input), 2)
        
        # Convert to string for processing
        price_str = str(price_input).strip()
        
        if not price_str:
            raise ValueError("Price string is empty")
        
        # Remove currency symbols and formatting
        cleaned_price = PriceParser._clean_price_string(price_str)
        
        if not cleaned_price:
            raise ValueError(f"Price string is empty after cleaning: '{price_str}'")
        
        try:
            parsed_price = float(cleaned_price)
            
            if parsed_price < 0:
                raise ValueError(f"Price cannot be negative: {parsed_price}")
            
            return round(parsed_price, 2)
            
        except ValueError as e:
            if "could not convert" in str(e).lower():
                raise ValueError(f"Cannot convert price to float: '{price_str}' -> '{cleaned_price}'")
            raise
    
    @staticmethod
    def _clean_price_string(price_str: str) -> str:
        """
        Clean price string by removing currency symbols and formatting.
        
        Args:
            price_str: Raw price string
            
        Returns:
            Cleaned price string with only numbers and decimal point
        """
        # Remove Thai currency symbols
        cleaned = price_str.replace('฿', '')
        
        # Remove currency words (case insensitive)
        currency_words = ['THB', 'Baht', 'บาท']
        for word in currency_words:
            cleaned = re.sub(rf'\b{re.escape(word)}\b', '', cleaned, flags=re.IGNORECASE)
        
        # Remove commas (thousand separators)
        cleaned = cleaned.replace(',', '')
        
        # Remove extra spaces
        cleaned = re.sub(r'\s+', '', cleaned)
        
        # Handle multiple decimal points (keep only the last one)
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = '.'.join(parts[:-1]).replace('.', '') + '.' + parts[-1]
        
        return cleaned.strip()
    
    @staticmethod
    def validate_price_range(price: float, min_price: float = 0.01, max_price: float = 1000000.0) -> bool:
        """
        Validate that price is within reasonable range for PowerBuy products.
        
        Args:
            price: Parsed price value
            min_price: Minimum acceptable price (default: 0.01 THB)
            max_price: Maximum acceptable price (default: 1,000,000 THB)
            
        Returns:
            True if price is within valid range
        """
        return min_price <= price <= max_price


class PowerBuyJSONParser:
    """
    Specialized JSON parser for PowerBuy API response structures.
    
    Handles various PowerBuy API response formats and extracts product data
    with proper error handling and logging.
    """
    
    def __init__(self):
        """Initialize the parser with logging."""
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'products_extracted': 0,
            'extraction_errors': 0,
            'parsing_errors': []
        }
    
    def extract_products_from_json(self, json_data: Dict[str, Any], source_info: str = "unknown") -> List[RawProductData]:
        """
        Extract product data from PowerBuy API JSON response.
        
        Handles multiple response formats:
        1. Standard format: {"products": [...]}
        2. Direct array: [product1, product2, ...]
        3. Single product: {product_data}
        4. Nested format: {"data": {"products": [...]}}
        
        Args:
            json_data: Raw JSON data from PowerBuy API
            source_info: Information about data source for logging
            
        Returns:
            List of RawProductData objects
        """
        products = []
        
        try:
            # Reset stats for this extraction
            extraction_stats = {'found': 0, 'errors': 0}
            
            # Handle standard PowerBuy format: {"products": [...]}
            if 'products' in json_data and isinstance(json_data['products'], list):
                products.extend(self._extract_from_products_array(json_data['products'], extraction_stats))
                self.logger.debug(f"Extracted {extraction_stats['found']} products from standard format in {source_info}")
            
            # Handle nested data format: {"data": {"products": [...]}}
            elif 'data' in json_data and isinstance(json_data['data'], dict) and 'products' in json_data['data']:
                products.extend(self._extract_from_products_array(json_data['data']['products'], extraction_stats))
                self.logger.debug(f"Extracted {extraction_stats['found']} products from nested format in {source_info}")
            
            # Handle direct array format: [product1, product2, ...]
            elif isinstance(json_data, list):
                products.extend(self._extract_from_products_array(json_data, extraction_stats))
                self.logger.debug(f"Extracted {extraction_stats['found']} products from array format in {source_info}")
            
            # Handle single product format: {product_data}
            elif self._is_single_product(json_data):
                product = self._extract_single_product(json_data)
                if product:
                    products.append(product)
                    extraction_stats['found'] = 1
                self.logger.debug(f"Extracted single product from {source_info}")
            
            else:
                self.logger.warning(f"Unrecognized JSON structure in {source_info}: {list(json_data.keys()) if isinstance(json_data, dict) else type(json_data)}")
            
            # Update global stats
            self.stats['products_extracted'] += extraction_stats['found']
            self.stats['extraction_errors'] += extraction_stats['errors']
            
            self.logger.info(f"Successfully extracted {extraction_stats['found']} products from {source_info}")
            
        except Exception as e:
            error_msg = f"Critical error extracting products from {source_info}: {str(e)}"
            self.logger.error(error_msg)
            self.stats['parsing_errors'].append(error_msg)
            self.stats['extraction_errors'] += 1
        
        return products
    
    def _extract_from_products_array(self, products_array: List[Dict], stats: Dict[str, int]) -> List[RawProductData]:
        """
        Extract products from an array of product dictionaries.
        
        Args:
            products_array: List of product dictionaries
            stats: Statistics dictionary to update
            
        Returns:
            List of RawProductData objects
        """
        products = []
        
        for i, product_item in enumerate(products_array):
            try:
                product = self._extract_single_product(product_item)
                if product:
                    products.append(product)
                    stats['found'] += 1
                else:
                    stats['errors'] += 1
                    
            except Exception as e:
                error_msg = f"Error extracting product at index {i}: {str(e)}"
                self.logger.warning(error_msg)
                self.stats['parsing_errors'].append(error_msg)
                stats['errors'] += 1
                continue
        
        return products
    
    def _extract_single_product(self, product_data: Dict[str, Any]) -> Optional[RawProductData]:
        """
        Extract a single product from product dictionary.
        
        Args:
            product_data: Single product dictionary
            
        Returns:
            RawProductData object or None if extraction fails
        """
        try:
            # Extract basic required fields
            name = self._extract_product_name(product_data)
            sku = self._extract_product_sku(product_data)
            
            # Skip products without essential data
            if not name and not sku:
                self.logger.debug("Skipping product with no name or SKU")
                return None
            
            # Extract optional fields
            price = self._extract_product_price(product_data)
            stock_status = self._extract_stock_status(product_data)
            
            # Create RawProductData object
            raw_product = RawProductData(
                name=name or "Unknown Product",
                sku=sku or f"UNKNOWN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                price=price,
                stock_status=stock_status,
                raw_json=product_data
            )
            
            return raw_product
            
        except Exception as e:
            self.logger.warning(f"Failed to extract product: {str(e)}, Data: {product_data}")
            return None
    
    def _extract_product_name(self, product_data: Dict[str, Any]) -> str:
        """Extract product name from various possible fields."""
        name_fields = ['name', 'title', 'product_name', 'productName']
        
        for field in name_fields:
            if field in product_data and product_data[field]:
                return str(product_data[field]).strip()
        
        return ""
    
    def _extract_product_sku(self, product_data: Dict[str, Any]) -> str:
        """Extract product SKU from various possible fields."""
        sku_fields = ['sku', 'id', 'product_id', 'productId', 'code', 'product_code']
        
        for field in sku_fields:
            if field in product_data and product_data[field]:
                return str(product_data[field]).strip()
        
        return ""
    
    def _extract_product_price(self, product_data: Dict[str, Any]) -> Optional[str]:
        """Extract product price from various possible fields."""
        # Handle nested price structures first
        if 'price' in product_data and isinstance(product_data['price'], dict):
            nested_price_fields = ['selling', 'current', 'sale', 'final']
            for field in nested_price_fields:
                if field in product_data['price'] and product_data['price'][field] is not None:
                    return str(product_data['price'][field])
        
        # Handle direct price fields
        price_fields = ['price', 'selling_price', 'current_price', 'sale_price']
        
        for field in price_fields:
            if field in product_data and product_data[field] is not None:
                return str(product_data[field])
        
        return None
    
    def _extract_stock_status(self, product_data: Dict[str, Any]) -> Optional[str]:
        """Extract stock status from various possible fields."""
        stock_fields = ['stock_status', 'stock', 'availability', 'available']
        
        for field in stock_fields:
            if field in product_data and product_data[field] is not None:
                return str(product_data[field])
        
        # Handle nested stock structures
        if 'stock' in product_data and isinstance(product_data['stock'], dict):
            nested_stock_fields = ['status', 'availability', 'available']
            for field in nested_stock_fields:
                if field in product_data['stock'] and product_data['stock'][field] is not None:
                    return str(product_data['stock'][field])
        
        return None
    
    def _is_single_product(self, data: Dict[str, Any]) -> bool:
        """
        Check if the data represents a single product.
        
        Args:
            data: Dictionary to check
            
        Returns:
            True if data appears to be a single product
        """
        # Check for common product fields
        product_indicators = ['name', 'sku', 'price', 'title', 'product_name']
        return any(field in data for field in product_indicators)
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the extraction process.
        
        Returns:
            Dictionary with extraction statistics
        """
        return {
            'products_extracted': self.stats['products_extracted'],
            'extraction_errors': self.stats['extraction_errors'],
            'parsing_errors': self.stats['parsing_errors'].copy(),
            'success_rate': (
                self.stats['products_extracted'] / 
                max(self.stats['products_extracted'] + self.stats['extraction_errors'], 1)
            ) * 100
        }
    
    def reset_stats(self):
        """Reset extraction statistics."""
        self.stats = {
            'products_extracted': 0,
            'extraction_errors': 0,
            'parsing_errors': []
        }


class DataTransformer:
    """
    Data transformation utility for converting RawProductData to ProductData.
    
    Handles data cleaning, validation, and normalization with comprehensive
    error handling and logging.
    """
    
    def __init__(self):
        """Initialize the transformer with logging."""
        self.logger = logging.getLogger(__name__)
        self.price_parser = PriceParser()
        self.stats = {
            'transformations_attempted': 0,
            'transformations_successful': 0,
            'transformation_errors': 0,
            'error_details': []
        }
    
    def transform_to_product_data(self, raw_products: List[RawProductData]) -> List[ProductData]:
        """
        Transform list of RawProductData to validated ProductData objects.
        
        Args:
            raw_products: List of RawProductData objects
            
        Returns:
            List of validated ProductData objects
        """
        validated_products = []
        
        self.logger.info(f"Transforming {len(raw_products)} raw products to validated data")
        
        for raw_product in raw_products:
            self.stats['transformations_attempted'] += 1
            
            try:
                validated_product = self._transform_single_product(raw_product)
                if validated_product:
                    validated_products.append(validated_product)
                    self.stats['transformations_successful'] += 1
                else:
                    self.stats['transformation_errors'] += 1
                    
            except Exception as e:
                error_msg = f"Transformation failed for product {raw_product.sku}: {str(e)}"
                self.logger.warning(error_msg)
                self.stats['transformation_errors'] += 1
                self.stats['error_details'].append(error_msg)
                continue
        
        success_rate = (self.stats['transformations_successful'] / max(self.stats['transformations_attempted'], 1)) * 100
        self.logger.info(f"Transformation completed: {len(validated_products)} successful ({success_rate:.1f}%)")
        
        return validated_products
    
    def _transform_single_product(self, raw_product: RawProductData) -> Optional[ProductData]:
        """
        Transform a single RawProductData to ProductData.
        
        Args:
            raw_product: RawProductData object
            
        Returns:
            ProductData object or None if transformation fails
        """
        try:
            # Parse and validate price
            price_thb = self._parse_and_validate_price(raw_product.price, raw_product.sku)
            
            # Clean and validate name
            cleaned_name = self._clean_product_name(raw_product.name)
            
            # Clean and validate SKU
            cleaned_sku = self._clean_product_sku(raw_product.sku)
            
            # Normalize stock status
            normalized_stock = self._normalize_stock_status(raw_product.stock_status)
            
            # Create validated ProductData
            validated_product = ProductData(
                name=cleaned_name,
                sku=cleaned_sku,
                price_thb=price_thb,
                stock_status=normalized_stock
            )
            
            return validated_product
            
        except Exception as e:
            self.logger.debug(f"Single product transformation failed for {raw_product.sku}: {str(e)}")
            raise
    
    def _parse_and_validate_price(self, price_input: Optional[str], sku: str) -> float:
        """
        Parse and validate price with detailed error context.
        
        Args:
            price_input: Raw price string
            sku: Product SKU for error context
            
        Returns:
            Validated price as float
            
        Raises:
            ValueError: If price cannot be parsed or is invalid
        """
        try:
            if price_input is None:
                raise ValueError("Price is None")
            
            parsed_price = self.price_parser.parse_price(price_input)
            
            # Validate price range for PowerBuy products
            if not self.price_parser.validate_price_range(parsed_price):
                self.logger.warning(f"Price {parsed_price} for SKU {sku} is outside normal range")
            
            return parsed_price
            
        except ValueError as e:
            raise ValueError(f"Price parsing failed for SKU {sku}: {str(e)}")
    
    def _clean_product_name(self, name: str) -> str:
        """
        Clean and validate product name.
        
        Args:
            name: Raw product name
            
        Returns:
            Cleaned product name
        """
        if not name:
            return "Unknown Product"
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', name.strip())
        
        # Ensure minimum length
        if len(cleaned) < 2:
            return f"Product {cleaned}" if cleaned else "Unknown Product"
        
        return cleaned
    
    def _clean_product_sku(self, sku: str) -> str:
        """
        Clean and validate product SKU.
        
        Args:
            sku: Raw product SKU
            
        Returns:
            Cleaned product SKU
        """
        if not sku:
            return f"UNKNOWN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Remove whitespace and normalize
        cleaned = sku.strip().upper()
        
        # Ensure valid SKU format
        if len(cleaned) < 1:
            return f"UNKNOWN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return cleaned
    
    def _normalize_stock_status(self, stock_status: Optional[str]) -> str:
        """
        Normalize stock status to standard values.
        
        Args:
            stock_status: Raw stock status string
            
        Returns:
            Normalized stock status
        """
        if not stock_status:
            return 'Unknown'
        
        status_lower = stock_status.lower().strip()
        
        # In Stock variations
        in_stock_indicators = [
            'in stock', 'available', 'มีสินค้า', 'พร้อมส่ง', 'มีของ', 
            'in_stock', 'instock', 'yes', 'true', '1'
        ]
        
        # Out of Stock variations
        out_of_stock_indicators = [
            'out of stock', 'unavailable', 'หมด', 'สินค้าหมด', 'ไม่มีสินค้า',
            'out_of_stock', 'outofstock', 'no', 'false', '0'
        ]
        
        if any(indicator in status_lower for indicator in in_stock_indicators):
            return 'In Stock'
        elif any(indicator in status_lower for indicator in out_of_stock_indicators):
            return 'Out of Stock'
        else:
            return 'Unknown'
    
    def get_transformation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the transformation process.
        
        Returns:
            Dictionary with transformation statistics
        """
        return {
            'transformations_attempted': self.stats['transformations_attempted'],
            'transformations_successful': self.stats['transformations_successful'],
            'transformation_errors': self.stats['transformation_errors'],
            'error_details': self.stats['error_details'].copy(),
            'success_rate': (
                self.stats['transformations_successful'] / 
                max(self.stats['transformations_attempted'], 1)
            ) * 100
        }
    
    def reset_stats(self):
        """Reset transformation statistics."""
        self.stats = {
            'transformations_attempted': 0,
            'transformations_successful': 0,
            'transformation_errors': 0,
            'error_details': []
        }
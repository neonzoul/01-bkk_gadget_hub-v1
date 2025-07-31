"""
Enhanced product validation utilities for PowerBuy scraper.

This module provides comprehensive validation functions and utilities
for product data validation, normalization, and quality assurance.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from .models import RawProductData, ProductData


class ProductValidator:
    """
    Enhanced product validation utility with comprehensive validation rules.
    
    Provides advanced validation for PowerBuy product data including
    name validation, SKU format checking, price validation, and 
    stock status normalization with Thai language support.
    """
    
    def __init__(self):
        """Initialize the validator with logging."""
        self.logger = logging.getLogger(__name__)
        self.validation_stats = {
            'products_validated': 0,
            'validation_errors': 0,
            'normalization_applied': 0,
            'error_details': []
        }
    
    def validate_product_data(self, product_data: ProductData) -> bool:
        """
        Comprehensive validation of ProductData object.
        
        Args:
            product_data: ProductData object to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            self.validation_stats['products_validated'] += 1
            
            # Validate product name
            if not self._validate_product_name(product_data.name):
                return False
            
            # Validate SKU format
            if not self._validate_sku_format(product_data.sku):
                return False
            
            # Validate price
            if not self._validate_price_value(product_data.price_thb):
                return False
            
            # Validate stock status
            if not self._validate_stock_status(product_data.stock_status):
                return False
            
            return True
            
        except Exception as e:
            error_msg = f"Validation error for product {product_data.sku}: {str(e)}"
            self.logger.error(error_msg)
            self.validation_stats['validation_errors'] += 1
            self.validation_stats['error_details'].append(error_msg)
            return False
    
    def _validate_product_name(self, name: str) -> bool:
        """
        Validate product name format and content.
        
        Args:
            name: Product name to validate
            
        Returns:
            True if name is valid
        """
        if not name or not isinstance(name, str):
            self._log_validation_error("Product name is empty or not a string")
            return False
        
        # Check minimum length
        if len(name.strip()) < 2:
            self._log_validation_error(f"Product name too short: '{name}'")
            return False
        
        # Check maximum length (reasonable limit for PowerBuy products)
        if len(name) > 200:
            self._log_validation_error(f"Product name too long: {len(name)} characters")
            return False
        
        return True
    
    def _validate_sku_format(self, sku: str) -> bool:
        """
        Validate SKU format for PowerBuy products.
        
        Args:
            sku: Product SKU to validate
            
        Returns:
            True if SKU format is valid
        """
        if not sku or not isinstance(sku, str):
            self._log_validation_error("SKU is empty or not a string")
            return False
        
        # Check minimum length
        if len(sku.strip()) < 1:
            self._log_validation_error("SKU is empty after trimming")
            return False
        
        # Check for reasonable SKU format (alphanumeric with some special chars)
        if not re.match(r'^[A-Za-z0-9_-]+$', sku.strip()):
            self.logger.warning(f"SKU contains unusual characters: '{sku}'")
            # Don't fail validation, just warn
        
        return True
    
    def _validate_price_value(self, price: float) -> bool:
        """
        Validate price value for PowerBuy products.
        
        Args:
            price: Price value to validate
            
        Returns:
            True if price is valid
        """
        if not isinstance(price, (int, float)):
            self._log_validation_error(f"Price is not numeric: {type(price)}")
            return False
        
        if price < 0:
            self._log_validation_error(f"Price cannot be negative: {price}")
            return False
        
        # Check reasonable price range for PowerBuy products
        if price > 1000000:  # 1 million THB
            self.logger.warning(f"Price seems unusually high: {price:,.2f} THB")
            # Don't fail validation, just warn
        
        if price < 0.01 and price > 0:
            self.logger.warning(f"Price seems unusually low: {price:.4f} THB")
            # Don't fail validation, just warn
        
        return True
    
    def _validate_stock_status(self, stock_status: Optional[str]) -> bool:
        """
        Validate stock status value.
        
        Args:
            stock_status: Stock status to validate
            
        Returns:
            True if stock status is valid
        """
        if stock_status is None:
            return True  # None is acceptable
        
        if not isinstance(stock_status, str):
            self._log_validation_error(f"Stock status is not a string: {type(stock_status)}")
            return False
        
        # Check if it's one of the normalized values
        valid_statuses = ['In Stock', 'Out of Stock', 'Unknown']
        if stock_status not in valid_statuses:
            self.logger.warning(f"Stock status not normalized: '{stock_status}'")
            # Don't fail validation, just warn
        
        return True
    
    def _log_validation_error(self, message: str):
        """Log validation error and update statistics."""
        self.logger.error(message)
        self.validation_stats['validation_errors'] += 1
        self.validation_stats['error_details'].append(message)
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get validation statistics.
        
        Returns:
            Dictionary with validation statistics
        """
        return {
            'products_validated': self.validation_stats['products_validated'],
            'validation_errors': self.validation_stats['validation_errors'],
            'normalization_applied': self.validation_stats['normalization_applied'],
            'error_details': self.validation_stats['error_details'].copy(),
            'success_rate': (
                (self.validation_stats['products_validated'] - self.validation_stats['validation_errors']) /
                max(self.validation_stats['products_validated'], 1)
            ) * 100
        }
    
    def reset_stats(self):
        """Reset validation statistics."""
        self.validation_stats = {
            'products_validated': 0,
            'validation_errors': 0,
            'normalization_applied': 0,
            'error_details': []
        }
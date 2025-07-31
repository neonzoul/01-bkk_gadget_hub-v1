"""
Enhanced Pydantic models for data validation and structure definition.

This module provides comprehensive data models with advanced validation,
normalization, and Thai language support for the PowerBuy scraper system.
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import re


class RawProductData(BaseModel):
    """
    Raw product data from PowerBuy API with enhanced validation.
    
    This model represents unprocessed product data as received from
    PowerBuy API responses, with flexible validation and extra field support.
    """
    name: str = Field(..., min_length=1, max_length=500, description="Product name from API")
    sku: str = Field(..., min_length=1, max_length=100, description="Product SKU/ID from API")
    price: Optional[str] = Field(None, description="Raw price string from API")
    stock_status: Optional[str] = Field(None, description="Raw stock status from API")
    raw_json: Dict[str, Any] = Field(..., description="Complete original JSON for debugging")
    
    # Additional optional fields that might be present in API responses
    brand: Optional[str] = Field(None, description="Product brand if available")
    category: Optional[str] = Field(None, description="Product category if available")
    image_url: Optional[str] = Field(None, description="Product image URL if available")
    product_url: Optional[str] = Field(None, description="Product page URL if available")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate and clean product name."""
        if not v or not v.strip():
            raise ValueError('Product name cannot be empty')
        
        # Clean excessive whitespace
        cleaned = re.sub(r'\s+', ' ', v.strip())
        
        # Check for reasonable length
        if len(cleaned) > 500:
            raise ValueError(f'Product name too long: {len(cleaned)} characters')
        
        return cleaned
    
    @validator('sku')
    def validate_sku(cls, v):
        """Validate and clean product SKU."""
        if not v or not v.strip():
            raise ValueError('Product SKU cannot be empty')
        
        # Clean and normalize SKU
        cleaned = v.strip().upper()
        
        # Check for reasonable length
        if len(cleaned) > 100:
            raise ValueError(f'Product SKU too long: {len(cleaned)} characters')
        
        return cleaned
    
    @validator('price')
    def validate_price_string(cls, v):
        """Validate raw price string format."""
        if v is None:
            return v
        
        # Convert to string if not already
        price_str = str(v).strip()
        
        # Allow empty string (will be handled in processing)
        if not price_str:
            return None
        
        # Check for reasonable length (prevent extremely long strings)
        if len(price_str) > 50:
            raise ValueError(f'Price string too long: {len(price_str)} characters')
        
        return price_str

    class Config:
        # Allow extra fields in case API returns additional data
        extra = "allow"
        # Enable validation on assignment
        validate_assignment = True
        # Use enum values for better serialization
        use_enum_values = True


class ProductData(BaseModel):
    """
    Validated and cleaned product data with enhanced normalization.
    
    This model represents fully processed and validated product data
    ready for CSV export or further processing.
    """
    name: str = Field(..., min_length=2, max_length=500, description="Cleaned product name")
    sku: str = Field(..., min_length=1, max_length=100, description="Normalized product SKU")
    price_thb: float = Field(..., ge=0, description="Price in Thai Baht (non-negative)")
    stock_status: str = Field(default="Unknown", description="Normalized stock status")
    
    # Additional optional fields for enhanced data
    brand: Optional[str] = Field(None, description="Product brand if available")
    category: Optional[str] = Field(None, description="Product category if available")
    image_url: Optional[str] = Field(None, description="Product image URL if available")
    product_url: Optional[str] = Field(None, description="Product page URL if available")
    
    # Metadata fields
    data_source: str = Field(default="powerbuy.co.th", description="Data source identifier")
    collection_date: Optional[datetime] = Field(None, description="When data was collected")
    
    @validator('name')
    def validate_and_clean_name(cls, v):
        """Validate and clean product name with enhanced rules."""
        if not v or not v.strip():
            raise ValueError('Product name cannot be empty')
        
        # Clean excessive whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', v.strip())
        
        # Remove or replace problematic characters for CSV compatibility
        cleaned = re.sub(r'["\n\r\t]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Ensure minimum length after cleaning
        if len(cleaned) < 2:
            raise ValueError(f'Product name too short after cleaning: "{cleaned}"')
        
        # Check maximum length
        if len(cleaned) > 500:
            # Truncate if too long, but preserve important information
            cleaned = cleaned[:497] + "..."
        
        return cleaned
    
    @validator('sku')
    def validate_and_normalize_sku(cls, v):
        """Validate and normalize product SKU."""
        if not v or not v.strip():
            raise ValueError('Product SKU cannot be empty')
        
        # Normalize SKU format
        normalized = v.strip().upper()
        
        # Remove problematic characters
        normalized = re.sub(r'[^\w\-_]', '', normalized)
        
        # Ensure it's not empty after cleaning
        if not normalized:
            raise ValueError('Product SKU is empty after normalization')
        
        # Check length
        if len(normalized) > 100:
            raise ValueError(f'Product SKU too long: {len(normalized)} characters')
        
        return normalized
    
    @validator('price_thb')
    def validate_price_value(cls, v):
        """Validate price with enhanced rules."""
        if not isinstance(v, (int, float)):
            raise ValueError(f'Price must be numeric, got {type(v)}')
        
        if v < 0:
            raise ValueError('Price cannot be negative')
        
        # Check for reasonable maximum (1 million THB)
        if v > 1000000:
            raise ValueError(f'Price seems unreasonably high: {v:,.2f} THB')
        
        # Round to 2 decimal places
        return round(float(v), 2)
    
    @validator('stock_status')
    def normalize_stock_status_enhanced(cls, v):
        """Enhanced stock status normalization with comprehensive Thai support."""
        if not v:
            return 'Unknown'
        
        # Import here to avoid circular imports
        from .stock_normalizer import StockStatusNormalizer
        
        normalizer = StockStatusNormalizer()
        return normalizer.normalize_stock_status(v)
    
    @validator('brand')
    def clean_brand(cls, v):
        """Clean brand name if provided."""
        if not v:
            return v
        
        cleaned = v.strip()
        if not cleaned:
            return None
        
        # Clean excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned
    
    @validator('category')
    def clean_category(cls, v):
        """Clean category name if provided."""
        if not v:
            return v
        
        cleaned = v.strip()
        if not cleaned:
            return None
        
        # Clean excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned
    
    @validator('image_url', 'product_url')
    def validate_url(cls, v):
        """Basic URL validation."""
        if not v:
            return v
        
        url = v.strip()
        if not url:
            return None
        
        # Basic URL format check
        if not (url.startswith('http://') or url.startswith('https://')):
            # Don't fail validation, just warn
            return url
        
        return url

    class Config:
        # Ensure proper JSON serialization
        json_encoders = {
            float: lambda v: round(v, 2),
            datetime: lambda v: v.isoformat()
        }
        # Enable validation on assignment
        validate_assignment = True
        # Use enum values for better serialization
        use_enum_values = True


class CollectionSummary(BaseModel):
    """Summary of manual collection session"""
    search_terms_processed: List[str]
    total_products_found: int
    files_created: List[str]
    errors: List[str]
    collection_time: datetime
    
    @validator('total_products_found')
    def validate_product_count(cls, v):
        """Ensure product count is non-negative"""
        if v < 0:
            raise ValueError('Product count cannot be negative')
        return v

    class Config:
        # Handle datetime serialization
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProcessingSummary(BaseModel):
    """Summary of data processing results"""
    total_files_processed: int
    total_products_extracted: int
    successful_validations: int
    validation_failures: int
    processing_time: datetime
    output_file: str
    
    @validator('total_files_processed', 'total_products_extracted', 
              'successful_validations', 'validation_failures')
    def validate_counts(cls, v):
        """Ensure all counts are non-negative"""
        if v < 0:
            raise ValueError('Count values cannot be negative')
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
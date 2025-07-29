"""
Pydantic models for data validation and structure definition.
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class RawProductData(BaseModel):
    """Raw product data from PowerBuy API"""
    name: str
    sku: str
    price: Optional[str] = None  # Raw price string from API
    stock_status: Optional[str] = None
    raw_json: Dict[str, Any]  # Complete original JSON for debugging

    class Config:
        # Allow extra fields in case API returns additional data
        extra = "allow"


class ProductData(BaseModel):
    """Validated and cleaned product data"""
    name: str
    sku: str
    price_thb: float
    stock_status: Optional[str] = None
    
    @validator('price_thb')
    def validate_price(cls, v):
        """Validate that price is non-negative and properly formatted"""
        if v < 0:
            raise ValueError('Price cannot be negative')
        return round(v, 2)
    
    @validator('stock_status')
    def normalize_stock_status(cls, v):
        """Normalize stock status to standard values"""
        if not v:
            return 'Unknown'
        
        v_lower = v.lower()
        if v_lower in ['in stock', 'available', 'มีสินค้า', 'พร้อมส่ง']:
            return 'In Stock'
        elif v_lower in ['out of stock', 'unavailable', 'หมด', 'สินค้าหมด']:
            return 'Out of Stock'
        return 'Unknown'

    class Config:
        # Ensure proper JSON serialization
        json_encoders = {
            float: lambda v: round(v, 2)
        }


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
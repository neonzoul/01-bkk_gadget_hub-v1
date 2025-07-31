"""
Example usage of the enhanced validators module.

This script demonstrates how to use the enhanced Pydantic models,
product validation, and stock status normalization capabilities.
"""

import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, 'src')

def demonstrate_enhanced_models():
    """Demonstrate enhanced Pydantic models with validation."""
    print("=== Enhanced Pydantic Models Demonstration ===")
    
    from validators.models import RawProductData, ProductData
    
    # Example 1: RawProductData with cleaning
    print("1. RawProductData with automatic cleaning:")
    raw_product = RawProductData(
        name="  iPhone 15 Pro Max (256GB)  ",  # Extra whitespace
        sku="  iphone15pm256  ",              # Lowercase with spaces
        price="49700",
        stock_status="มีสินค้า",              # Thai stock status
        raw_json={"source": "powerbuy_api"},
        brand="Apple",
        category="Smartphones"
    )
    
    print(f"   Original name: '  iPhone 15 Pro Max (256GB)  '")
    print(f"   Cleaned name:  '{raw_product.name}'")
    print(f"   Original SKU:  '  iphone15pm256  '")
    print(f"   Cleaned SKU:   '{raw_product.sku}'")
    
    # Example 2: ProductData with comprehensive validation
    print("\n2. ProductData with enhanced validation:")
    product = ProductData(
        name="Samsung Galaxy S24 Ultra",
        sku="GALAXYS24ULTRA",
        price_thb=45900.0,
        stock_status="พร้อมส่ง",  # Thai "ready to ship"
        brand="Samsung",
        category="Smartphones",
        collection_date=datetime.now()
    )
    
    print(f"   Product: {product.name}")
    print(f"   SKU: {product.sku}")
    print(f"   Price: {product.price_thb:,.2f} THB")
    print(f"   Stock: {product.stock_status}")  # Should be normalized to "In Stock"
    
    print()

def demonstrate_stock_normalizer():
    """Demonstrate comprehensive stock status normalization."""
    print("=== Stock Status Normalizer Demonstration ===")
    
    from validators.stock_normalizer import StockStatusNormalizer
    
    normalizer = StockStatusNormalizer()
    
    # Test various stock status formats
    test_statuses = [
        # English variations
        "In Stock",
        "Available",
        "Out of Stock", 
        "Unavailable",
        "sold out",
        "ready to ship",
        
        # Thai variations
        "มีสินค้า",
        "พร้อมส่ง", 
        "หมด",
        "สินค้าหมด",
        "ไม่มีสินค้า",
        "พร้อมจัดส่ง",
        "ขายหมด",
        
        # Edge cases
        "",
        "random text",
        "temporarily unavailable"
    ]
    
    print("Stock Status Normalization Results:")
    for status in test_statuses:
        normalized = normalizer.normalize_stock_status(status)
        print(f"   '{status}' → '{normalized}'")
    
    # Show statistics
    stats = normalizer.get_normalization_stats()
    print(f"\nNormalization Statistics:")
    print(f"   Total normalized: {stats['total_normalized']}")
    print(f"   In Stock: {stats['in_stock_normalized']}")
    print(f"   Out of Stock: {stats['out_of_stock_normalized']}")
    print(f"   Unknown: {stats['unknown_status']}")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    
    print()

def demonstrate_product_validator():
    """Demonstrate product validation capabilities."""
    print("=== Product Validator Demonstration ===")
    
    from validators.product_validator import ProductValidator
    from validators.models import ProductData
    
    validator = ProductValidator()
    
    # Test products with various validation scenarios
    test_products = [
        # Valid product
        ProductData(
            name="iPad Pro 12.9-inch",
            sku="IPADPRO129",
            price_thb=39900.0,
            stock_status="In Stock"
        ),
        
        # Product with Thai text
        ProductData(
            name="MacBook Pro 14-inch M3",
            sku="MACBOOKPRO14M3",
            price_thb=89900.0,
            stock_status="มีสินค้า"
        ),
        
        # Product with edge case pricing
        ProductData(
            name="AirPods Pro (2nd generation)",
            sku="AIRPODSPRO2",
            price_thb=8900.0,
            stock_status="Available"
        )
    ]
    
    print("Product Validation Results:")
    for i, product in enumerate(test_products, 1):
        is_valid = validator.validate_product_data(product)
        status = "✓ VALID" if is_valid else "❌ INVALID"
        print(f"   Product {i}: {status}")
        print(f"     Name: {product.name}")
        print(f"     SKU: {product.sku}")
        print(f"     Price: {product.price_thb:,.2f} THB")
        print(f"     Stock: {product.stock_status}")
    
    # Show validation statistics
    stats = validator.get_validation_stats()
    print(f"\nValidation Statistics:")
    print(f"   Products validated: {stats['products_validated']}")
    print(f"   Validation errors: {stats['validation_errors']}")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    
    print()

def demonstrate_integration_pipeline():
    """Demonstrate complete integration with parsers."""
    print("=== Integration Pipeline Demonstration ===")
    
    from parsers.powerbuy_parser import PowerBuyJSONParser, DataTransformer
    from validators.models import ProductData
    
    # Sample PowerBuy API response
    sample_api_response = {
        "products": [
            {
                "name": "iPhone 15 (128GB, Pink)",
                "sku": "IPHONE15128PINK",
                "price": "29900",
                "stock_status": "มีสินค้า"
            },
            {
                "name": "Samsung Galaxy A54 5G",
                "sku": "GALAXYA54",
                "price": "12,900",
                "stock_status": "หมด"
            }
        ]
    }
    
    print("Processing sample API response through complete pipeline:")
    
    # Step 1: Parse JSON
    parser = PowerBuyJSONParser()
    raw_products = parser.extract_products_from_json(sample_api_response, "demo")
    print(f"   Step 1: Extracted {len(raw_products)} raw products")
    
    # Step 2: Transform and validate
    transformer = DataTransformer()
    validated_products = transformer.transform_to_product_data(raw_products)
    print(f"   Step 2: Validated {len(validated_products)} products")
    
    # Step 3: Show results
    print("   Step 3: Final results with enhanced validation:")
    for i, product in enumerate(validated_products, 1):
        print(f"     Product {i}:")
        print(f"       Name: {product.name}")
        print(f"       SKU: {product.sku}")
        print(f"       Price: {product.price_thb:,.2f} THB")
        print(f"       Stock: {product.stock_status}")  # Thai statuses normalized
    
    print()

def main():
    """Run all validator demonstrations."""
    print("Enhanced Validators Module - Usage Examples")
    print("=" * 50)
    
    demonstrate_enhanced_models()
    demonstrate_stock_normalizer()
    demonstrate_product_validator()
    demonstrate_integration_pipeline()
    
    print("=" * 50)
    print("✅ All demonstrations completed successfully!")
    print("\nThe enhanced validators module provides:")
    print("• Comprehensive Pydantic models with advanced validation")
    print("• Extensive Thai language support for stock status normalization")
    print("• Product validation with detailed error reporting")
    print("• Seamless integration with existing parsers and data pipeline")
    print("• Production-ready validation for PowerBuy scraper data")

if __name__ == "__main__":
    main()
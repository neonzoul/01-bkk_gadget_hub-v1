"""
Example usage of the PowerBuy parsers module.

This script demonstrates how to use the JSON parsing functions,
price parsing utilities, and data transformation capabilities.
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

from parsers.powerbuy_parser import PowerBuyJSONParser, PriceParser, DataTransformer

def demonstrate_price_parser():
    """Demonstrate PriceParser capabilities."""
    print("=== PriceParser Demonstration ===")
    
    # Various price formats that PowerBuy might return
    price_examples = [
        "฿49,700",           # Thai Baht with comma
        "35900 THB",         # THB suffix
        "39,900.50 Baht",    # Baht suffix with decimal
        " ฿ 1,234,567.89 ",  # Complex formatting
        15900,               # Numeric value
        "8900"               # Simple string
    ]
    
    for price_input in price_examples:
        try:
            parsed_price = PriceParser.parse_price(price_input)
            print(f"  {str(price_input):20} → {parsed_price:,.2f} THB")
        except ValueError as e:
            print(f"  {str(price_input):20} → Error: {e}")
    
    print()

def demonstrate_json_parser():
    """Demonstrate PowerBuyJSONParser capabilities."""
    print("=== PowerBuyJSONParser Demonstration ===")
    
    parser = PowerBuyJSONParser()
    
    # Example 1: Standard PowerBuy API format
    standard_response = {
        "products": [
            {
                "name": "iPhone 15 Pro Max (256GB, Natural Titanium)",
                "sku": "IPHONE15PM256",
                "price": "49700",
                "stock_status": "In Stock"
            },
            {
                "name": "Samsung Galaxy S24 Ultra (512GB, Titanium Black)",
                "sku": "GALAXYS24U512",
                "price": 45900,
                "stock_status": "มีสินค้า"
            }
        ]
    }
    
    print("1. Standard PowerBuy API Response:")
    products = parser.extract_products_from_json(standard_response, "example_standard")
    for i, product in enumerate(products, 1):
        print(f"   Product {i}: {product.name}")
        print(f"   SKU: {product.sku}, Price: {product.price}")
    
    # Example 2: Complex nested price structure
    complex_response = {
        "products": [
            {
                "name": "MacBook Pro 14-inch (M3 Pro, 512GB)",
                "sku": "MACBOOKPRO14M3",
                "price": {
                    "selling": "89900",
                    "original": "99900"
                },
                "stock": {
                    "status": "Available"
                }
            }
        ]
    }
    
    print("\n2. Complex Nested Structure:")
    parser.reset_stats()
    products = parser.extract_products_from_json(complex_response, "example_complex")
    for product in products:
        print(f"   Product: {product.name}")
        print(f"   SKU: {product.sku}, Price: {product.price}, Stock: {product.stock_status}")
    
    # Show extraction statistics
    stats = parser.get_extraction_stats()
    print(f"\n   Extraction Stats: {stats['products_extracted']} products, {stats['success_rate']:.1f}% success rate")
    
    print()

def demonstrate_data_transformer():
    """Demonstrate DataTransformer capabilities."""
    print("=== DataTransformer Demonstration ===")
    
    # First, create some raw product data
    parser = PowerBuyJSONParser()
    sample_data = {
        "products": [
            {
                "name": "  iPad Pro 12.9-inch (M2, 256GB)  ",  # Extra whitespace
                "sku": "  ipadpro129m2  ",                      # Lowercase SKU
                "price": "฿39,900.50",                          # Thai currency format
                "stock_status": "หมด"                           # Thai "out of stock"
            },
            {
                "name": "AirPods Pro (2nd generation)",
                "sku": "AIRPODSPRO2",
                "price": "8900",
                "stock_status": "In Stock"
            }
        ]
    }
    
    # Extract raw products
    raw_products = parser.extract_products_from_json(sample_data, "transformer_demo")
    print(f"Extracted {len(raw_products)} raw products")
    
    # Transform to validated data
    transformer = DataTransformer()
    validated_products = transformer.transform_to_product_data(raw_products)
    
    print(f"Transformed to {len(validated_products)} validated products:")
    
    for i, product in enumerate(validated_products, 1):
        print(f"\n   Product {i}:")
        print(f"   Name: {product.name}")
        print(f"   SKU: {product.sku}")
        print(f"   Price: {product.price_thb:,.2f} THB")
        print(f"   Stock: {product.stock_status}")
    
    # Show transformation statistics
    stats = transformer.get_transformation_stats()
    print(f"\n   Transformation Stats: {stats['transformations_successful']}/{stats['transformations_attempted']} successful ({stats['success_rate']:.1f}%)")
    
    print()

def demonstrate_full_pipeline():
    """Demonstrate complete parsing pipeline."""
    print("=== Complete Pipeline Demonstration ===")
    
    # Simulate data that might come from the scrapers
    scraped_data = {
        "search_term": "smartphone",
        "collection_timestamp": "2025-07-31T10:30:00",
        "total_products": 3,
        "data": {
            "products": [
                {
                    "name": "iPhone 15 (128GB, Pink)",
                    "sku": "IPHONE15128PINK",
                    "price": "29900",
                    "stock_status": "In Stock"
                },
                {
                    "name": "Samsung Galaxy A54 5G (256GB)",
                    "sku": "GALAXYA54256",
                    "price": "12,900",
                    "stock_status": "พร้อมส่ง"
                },
                {
                    "name": "Google Pixel 8 (128GB)",
                    "sku": "PIXEL8128",
                    "price": "฿21,900.00",
                    "stock_status": "Available"
                }
            ]
        }
    }
    
    print("Processing scraped data through complete pipeline...")
    
    # Step 1: Extract products from JSON
    parser = PowerBuyJSONParser()
    raw_products = parser.extract_products_from_json(scraped_data['data'], "pipeline_demo")
    print(f"Step 1: Extracted {len(raw_products)} raw products")
    
    # Step 2: Transform to validated data
    transformer = DataTransformer()
    validated_products = transformer.transform_to_product_data(raw_products)
    print(f"Step 2: Validated {len(validated_products)} products")
    
    # Step 3: Display results
    print("\nFinal Results:")
    total_value = 0
    for i, product in enumerate(validated_products, 1):
        print(f"  {i}. {product.name}")
        print(f"     SKU: {product.sku}")
        print(f"     Price: {product.price_thb:,.2f} THB")
        print(f"     Stock: {product.stock_status}")
        total_value += product.price_thb
    
    print(f"\nTotal Portfolio Value: {total_value:,.2f} THB")
    
    # Show pipeline statistics
    parser_stats = parser.get_extraction_stats()
    transformer_stats = transformer.get_transformation_stats()
    
    print(f"\nPipeline Statistics:")
    print(f"  Extraction: {parser_stats['products_extracted']} products ({parser_stats['success_rate']:.1f}% success)")
    print(f"  Transformation: {transformer_stats['transformations_successful']} products ({transformer_stats['success_rate']:.1f}% success)")
    
    print()

def main():
    """Run all parser demonstrations."""
    print("PowerBuy Parsers Module - Usage Examples")
    print("=" * 50)
    
    demonstrate_price_parser()
    demonstrate_json_parser()
    demonstrate_data_transformer()
    demonstrate_full_pipeline()
    
    print("=" * 50)
    print("✅ All demonstrations completed successfully!")
    print("\nThe parsers module provides:")
    print("• Robust price parsing with Thai currency support")
    print("• Flexible JSON structure handling for PowerBuy API responses")
    print("• Complete data transformation pipeline with validation")
    print("• Comprehensive error handling and statistics tracking")

if __name__ == "__main__":
    main()
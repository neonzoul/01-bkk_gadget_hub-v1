"""
Generate final CSV file with proper naming convention and summary statistics.
Task 11: Generate final CSV file
"""

import pandas as pd
import os
from datetime import datetime
import json
from pathlib import Path

def generate_final_csv():
    """Generate the final CSV file with proper naming and summary statistics."""
    
    # Read the current CSV file
    current_csv = "output/competitor_prices_complete_2025-08-05.csv"
    
    if not os.path.exists(current_csv):
        print(f"Error: Current CSV file not found: {current_csv}")
        return
    
    # Read the data
    df = pd.read_csv(current_csv)
    
    # Generate final filename with proper date format
    final_filename = "competitor_prices_2025-08-05.csv"
    final_path = os.path.join("output", final_filename)
    
    # Copy the data to the final file
    df.to_csv(final_path, index=False, encoding='utf-8')
    
    # Generate summary statistics
    total_products = len(df)
    successful_validations = total_products  # All products in CSV are successfully validated
    failures = 2  # From the log output, we had 2 validation failures
    
    # Count stock status distribution
    stock_counts = df['Stock Status'].value_counts()
    in_stock = stock_counts.get('In Stock', 0)
    out_of_stock = stock_counts.get('Out of Stock', 0)
    
    # Price statistics
    df['Price_Numeric'] = pd.to_numeric(df['Price'], errors='coerce')
    price_stats = {
        'min_price': df['Price_Numeric'].min(),
        'max_price': df['Price_Numeric'].max(),
        'avg_price': df['Price_Numeric'].mean(),
        'median_price': df['Price_Numeric'].median()
    }
    
    # Generate summary report
    summary = {
        'generation_date': datetime.now().isoformat(),
        'final_csv_file': final_filename,
        'processing_summary': {
            'total_files_processed': 36,
            'total_products_extracted': 319,
            'successful_validations': 317,
            'validation_failures': 2,
            'duplicates_removed': 129,
            'final_product_count': total_products
        },
        'data_quality': {
            'validation_success_rate': f"{(317/319)*100:.1f}%",
            'deduplication_rate': f"{(129/317)*100:.1f}%",
            'final_success_rate': f"{(total_products/319)*100:.1f}%"
        },
        'stock_distribution': {
            'in_stock': int(in_stock),
            'out_of_stock': int(out_of_stock),
            'in_stock_percentage': f"{(in_stock/total_products)*100:.1f}%"
        },
        'price_statistics': {
            'min_price_thb': f"{price_stats['min_price']:.2f}",
            'max_price_thb': f"{price_stats['max_price']:.2f}",
            'average_price_thb': f"{price_stats['avg_price']:.2f}",
            'median_price_thb': f"{price_stats['median_price']:.2f}"
        },
        'file_info': {
            'file_size_kb': f"{os.path.getsize(final_path) / 1024:.1f}",
            'encoding': 'UTF-8',
            'columns': list(df.columns),
            'total_rows': total_products
        }
    }
    
    # Save summary to JSON file
    summary_path = os.path.join("output", "processing_summary_2025-08-05.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("=" * 60)
    print("FINAL CSV GENERATION COMPLETED")
    print("=" * 60)
    print(f"📄 Final CSV file: {final_path}")
    print(f"📊 Summary file: {summary_path}")
    print()
    print("PROCESSING SUMMARY:")
    print(f"  • Files processed: {summary['processing_summary']['total_files_processed']}")
    print(f"  • Products extracted: {summary['processing_summary']['total_products_extracted']}")
    print(f"  • Successful validations: {summary['processing_summary']['successful_validations']}")
    print(f"  • Validation failures: {summary['processing_summary']['validation_failures']}")
    print(f"  • Duplicates removed: {summary['processing_summary']['duplicates_removed']}")
    print(f"  • Final product count: {summary['processing_summary']['final_product_count']}")
    print()
    print("DATA QUALITY:")
    print(f"  • Validation success rate: {summary['data_quality']['validation_success_rate']}")
    print(f"  • Deduplication rate: {summary['data_quality']['deduplication_rate']}")
    print(f"  • Final success rate: {summary['data_quality']['final_success_rate']}")
    print()
    print("STOCK DISTRIBUTION:")
    print(f"  • In Stock: {summary['stock_distribution']['in_stock']} ({summary['stock_distribution']['in_stock_percentage']})")
    print(f"  • Out of Stock: {summary['stock_distribution']['out_of_stock']}")
    print()
    print("PRICE STATISTICS:")
    print(f"  • Min Price: {summary['price_statistics']['min_price_thb']} THB")
    print(f"  • Max Price: {summary['price_statistics']['max_price_thb']} THB")
    print(f"  • Average Price: {summary['price_statistics']['average_price_thb']} THB")
    print(f"  • Median Price: {summary['price_statistics']['median_price_thb']} THB")
    print()
    print("FILE INFO:")
    print(f"  • File size: {summary['file_info']['file_size_kb']} KB")
    print(f"  • Encoding: {summary['file_info']['encoding']}")
    print(f"  • Total rows: {summary['file_info']['total_rows']}")
    print(f"  • Columns: {', '.join(summary['file_info']['columns'])}")
    print("=" * 60)
    
    return final_path, summary_path

if __name__ == "__main__":
    generate_final_csv()
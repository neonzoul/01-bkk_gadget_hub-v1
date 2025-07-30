"""
Example script demonstrating the ManualCollector usage.

This script shows how to use the enhanced ManualCollector class
for collecting PowerBuy product data with multiple search terms.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.collectors.manual_collector import ManualCollector
from src.utils.config_loader import load_config, get_search_terms


def main():
    """Main function demonstrating ManualCollector usage."""
    
    print("=== PowerBuy Manual Collector Example ===\n")
    
    try:
        # Load configuration
        print("1. Loading configuration...")
        config = load_config()
        print("   ✓ Configuration loaded successfully")
        
        # Get search terms
        print("\n2. Loading search terms...")
        search_terms = get_search_terms(config)
        print(f"   ✓ Found {len(search_terms)} search terms")
        
        # For demonstration, use only first 2 terms to avoid long execution
        demo_terms = search_terms[:2]
        print(f"   ✓ Using first 2 terms for demo: {demo_terms}")
        
        # Initialize collector
        print("\n3. Initializing ManualCollector...")
        collector = ManualCollector(config)
        print("   ✓ ManualCollector initialized")
        print(f"   ✓ Storage directories created:")
        print(f"     - Search results: {collector.search_results_dir}")
        print(f"     - Individual products: {collector.individual_products_dir}")
        
        # Show what the collector would do (without actually running browser)
        print("\n4. Collection Process Overview:")
        print("   The ManualCollector would perform the following steps:")
        print("   a) Launch browser with anti-detection measures")
        print("   b) Navigate to PowerBuy homepage")
        print("   c) Handle cookie banners automatically")
        print("   d) For each search term:")
        print("      - Enter search term in search box")
        print("      - Wait for search results page")
        print("      - Intercept API responses containing product data")
        print("      - Save raw JSON data with timestamps and metadata")
        print("   e) Generate collection summary")
        
        print("\n5. Expected Output Files:")
        for term in demo_terms:
            safe_term = term.replace(' ', '_')
            print(f"   - raw_data/search_results/{safe_term}_YYYY-MM-DD_HH-MM-SS.json")
        
        print("\n6. File Structure Example:")
        example_structure = {
            "search_term": "iPhone 15",
            "collection_timestamp": "2025-07-30_14-30-15",
            "total_products": 25,
            "products": [
                {
                    "name": "iPhone 15 Pro Max 256GB",
                    "sku": "IPHONE15PM256",
                    "price": "45900",
                    "stock_status": "In Stock"
                }
            ],
            "metadata": {
                "url": "https://www.powerbuy.co.th/search/iPhone%2015",
                "user_agent": "Mozilla/5.0...",
                "collection_method": "API_interception"
            }
        }
        
        print("   Each JSON file will contain:")
        for key, value in example_structure.items():
            if key == "products":
                print(f"   - {key}: [{len(value)} product objects]")
            elif isinstance(value, dict):
                print(f"   - {key}: {{metadata object}}")
            else:
                print(f"   - {key}: {value}")
        
        print("\n7. Collection Summary:")
        print("   After collection, you can get a summary with:")
        print("   - Search terms processed")
        print("   - Total products found")
        print("   - Files created")
        print("   - Any errors encountered")
        print("   - Collection timestamp")
        
        print("\n=== Demo Complete ===")
        print("\nTo run actual collection:")
        print("1. Ensure you have a stable internet connection")
        print("2. Run: python test_manual_collector.py")
        print("3. The browser will open and perform automated collection")
        print("4. Check raw_data/search_results/ for collected JSON files")
        
        print("\nNote: The actual collection requires browser automation")
        print("and may take several minutes depending on the number of search terms.")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
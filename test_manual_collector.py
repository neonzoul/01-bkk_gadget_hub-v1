"""
Test script for the ManualCollector class.

This script demonstrates the enhanced manual collector functionality
including multiple search terms processing and organized storage.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.collectors.manual_collector import ManualCollector
from src.utils.config_loader import load_config, get_search_terms


def test_manual_collector():
    """Test the ManualCollector with a few search terms."""
    
    try:
        # Load configuration
        config = load_config()
        print("Configuration loaded successfully")
        
        # Get search terms (limit to first 3 for testing)
        all_search_terms = get_search_terms(config)
        test_search_terms = all_search_terms[:3]  # Test with first 3 terms
        
        print(f"Testing with search terms: {test_search_terms}")
        
        # Initialize collector
        collector = ManualCollector(config)
        print("ManualCollector initialized")
        
        # Collect data for test search terms
        print("\nStarting data collection...")
        results = collector.collect_search_data(test_search_terms)
        
        # Display results
        print(f"\nCollection completed!")
        print(f"Successfully processed {len(results)} search terms:")
        for term, file_path in results.items():
            print(f"  - {term}: {file_path}")
        
        # Get collection summary
        summary = collector.get_collection_summary()
        print(f"\nCollection Summary:")
        print(f"  - Search terms processed: {len(summary.search_terms_processed)}")
        print(f"  - Total products found: {summary.total_products_found}")
        print(f"  - Files created: {len(summary.files_created)}")
        print(f"  - Errors: {len(summary.errors)}")
        print(f"  - Collection time: {summary.collection_time}")
        
        if summary.errors:
            print(f"\nErrors encountered:")
            for error in summary.errors:
                print(f"  - {error}")
        
        print(f"\nFiles created:")
        for file_path in summary.files_created:
            print(f"  - {file_path}")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_manual_collector()
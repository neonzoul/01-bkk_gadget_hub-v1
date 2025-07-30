"""
Test script for the ManualCollector class structure and configuration.

This script tests the ManualCollector initialization and configuration
without running the actual browser automation.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.collectors.manual_collector import ManualCollector
from src.utils.config_loader import load_config, get_search_terms


def test_manual_collector_structure():
    """Test the ManualCollector structure and initialization."""
    
    try:
        # Load configuration
        config = load_config()
        print("✓ Configuration loaded successfully")
        
        # Get search terms
        search_terms = get_search_terms(config)
        print(f"✓ Found {len(search_terms)} search terms")
        print(f"  First 5 terms: {search_terms[:5]}")
        
        # Initialize collector
        collector = ManualCollector(config)
        print("✓ ManualCollector initialized successfully")
        
        # Test directory creation
        print(f"✓ Search results directory: {collector.search_results_dir}")
        print(f"✓ Individual products directory: {collector.individual_products_dir}")
        
        # Verify directories exist
        assert collector.search_results_dir.exists(), "Search results directory should exist"
        assert collector.individual_products_dir.exists(), "Individual products directory should exist"
        print("✓ Storage directories created successfully")
        
        # Test configuration access
        print(f"✓ Base URL: {collector.base_url}")
        print(f"✓ User Agent: {collector.user_agent[:50]}...")
        
        # Test session tracking initialization
        assert collector.session_start_time is None, "Session should not be started yet"
        assert collector.collected_data == [], "Collected data should be empty initially"
        assert collector.errors == [], "Errors list should be empty initially"
        assert collector.files_created == [], "Files created list should be empty initially"
        print("✓ Session tracking initialized correctly")
        
        # Test save_raw_data method with dummy data
        test_data = {
            "test": "data",
            "products": [
                {"name": "Test Product", "sku": "TEST123", "price": "1000"}
            ]
        }
        
        test_file = collector.search_results_dir / "test_data.json"
        collector.save_raw_data(test_data, str(test_file))
        
        assert test_file.exists(), "Test file should be created"
        print("✓ save_raw_data method works correctly")
        
        # Clean up test file
        test_file.unlink()
        
        # Test get_collection_summary method
        from datetime import datetime
        collector.session_start_time = datetime.now()
        collector.collected_data = ["test_term_1", "test_term_2"]
        collector.files_created = ["file1.json", "file2.json"]
        collector.errors = ["test error"]
        
        summary = collector.get_collection_summary()
        print("✓ Collection summary generated successfully")
        print(f"  - Search terms processed: {len(summary.search_terms_processed)}")
        print(f"  - Total products found: {summary.total_products_found}")
        print(f"  - Files created: {len(summary.files_created)}")
        print(f"  - Errors: {len(summary.errors)}")
        
        print("\n🎉 All tests passed! ManualCollector structure is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_manual_collector_structure()
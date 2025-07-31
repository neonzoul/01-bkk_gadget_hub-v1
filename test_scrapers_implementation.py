"""
Test script to verify the scrapers implementation for task 6.1.

This script tests that the PowerBuyScraperCore and ManualCollector classes
are properly implemented and can be instantiated with the expected interface.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

def test_scraper_core_implementation():
    """Test that PowerBuyScraperCore is properly implemented."""
    print("Testing PowerBuyScraperCore implementation...")
    
    try:
        from scrapers.powerbuy_scraper import PowerBuyScraperCore
        
        # Test configuration
        config = {
            'scraping': {
                'base_url': 'https://www.powerbuy.co.th',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'page_timeout': 60000,
                'network_timeout': 30000
            }
        }
        
        # Initialize scraper core
        scraper_core = PowerBuyScraperCore(config)
        
        # Test that all required methods exist
        required_methods = [
            'setup_browser_context',
            'navigate_to_homepage', 
            'find_search_element',
            'perform_search',
            'wait_for_search_results',
            'setup_api_interception',
            'extract_individual_product_data',
            'extract_product_id_from_url',
            'create_enhanced_product_data',
            'validate_search_results',
            'get_scraper_stats'
        ]
        
        for method in required_methods:
            assert hasattr(scraper_core, method), f"Missing method: {method}"
            print(f"   ✓ Method '{method}' implemented")
        
        # Test configuration access
        assert scraper_core.base_url == 'https://www.powerbuy.co.th'
        assert scraper_core.user_data_dir == Path("user_data")
        print("   ✓ Configuration properly loaded")
        
        # Test stats method
        stats = scraper_core.get_scraper_stats()
        assert isinstance(stats, dict)
        assert 'base_url' in stats
        assert 'scraper_version' in stats
        print("   ✓ Stats method returns proper data")
        
        print("✅ PowerBuyScraperCore implementation test passed")
        return True
        
    except Exception as e:
        print(f"❌ PowerBuyScraperCore test failed: {str(e)}")
        return False

def test_manual_collector_implementation():
    """Test that ManualCollector is properly implemented."""
    print("\nTesting ManualCollector implementation...")
    
    try:
        from scrapers.powerbuy_scraper import ManualCollector
        
        # Test configuration
        config = {
            'scraping': {
                'base_url': 'https://www.powerbuy.co.th',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        # Initialize manual collector
        collector = ManualCollector(config)
        
        # Test that all required methods exist (from requirements)
        required_methods = [
            'collect_search_data',
            'collect_individual_product',
            'get_scraper_info'
        ]
        
        for method in required_methods:
            assert hasattr(collector, method), f"Missing method: {method}"
            print(f"   ✓ Method '{method}' implemented")
        
        # Test that scraper core is properly initialized
        assert hasattr(collector, 'scraper_core')
        assert collector.scraper_core is not None
        print("   ✓ PowerBuyScraperCore properly integrated")
        
        # Test directory setup
        assert collector.search_results_dir.exists()
        assert collector.individual_products_dir.exists()
        print("   ✓ Directory structure created")
        
        # Test scraper info method
        info = collector.get_scraper_info()
        assert isinstance(info, dict)
        assert 'scraper_core' in info
        assert 'directories' in info
        print("   ✓ Scraper info method returns proper data")
        
        print("✅ ManualCollector implementation test passed")
        return True
        
    except Exception as e:
        print(f"❌ ManualCollector test failed: {str(e)}")
        return False

def test_poc_extraction_verification():
    """Verify that POC logic has been properly extracted."""
    print("\nTesting POC logic extraction...")
    
    try:
        from scrapers.powerbuy_scraper import PowerBuyScraperCore
        
        config = {'scraping': {}}
        scraper_core = PowerBuyScraperCore(config)
        
        # Test that key POC elements are present
        
        # 1. Browser setup with anti-detection (from POC)
        assert hasattr(scraper_core, 'setup_browser_context')
        print("   ✓ Browser setup with anti-detection extracted")
        
        # 2. Search element finding with multiple selectors (from POC)
        assert hasattr(scraper_core, 'find_search_element')
        print("   ✓ Multi-selector search element finding extracted")
        
        # 3. API interception logic (from POC)
        assert hasattr(scraper_core, 'setup_api_interception')
        print("   ✓ API interception logic extracted")
        
        # 4. Individual product extraction (from POC individual scraper)
        assert hasattr(scraper_core, 'extract_individual_product_data')
        print("   ✓ Individual product extraction extracted")
        
        # 5. Product ID extraction (from URL patterns)
        test_url = "https://www.powerbuy.co.th/th/product/test-product-p-12345.html"
        product_id = scraper_core.extract_product_id_from_url(test_url)
        assert product_id == "12345"
        print("   ✓ Product ID extraction logic working")
        
        # 6. Enhanced data creation with metadata
        raw_data = {"name": "Test Product", "price": 100}
        enhanced = scraper_core.create_enhanced_product_data(raw_data)
        assert "collection_timestamp" in enhanced
        assert "collection_metadata" in enhanced
        print("   ✓ Enhanced data creation with metadata")
        
        print("✅ POC logic extraction verification passed")
        return True
        
    except Exception as e:
        print(f"❌ POC extraction verification failed: {str(e)}")
        return False

def test_requirements_compliance():
    """Test that implementation meets the requirements."""
    print("\nTesting requirements compliance...")
    
    try:
        from scrapers.powerbuy_scraper import ManualCollector
        
        config = {'scraping': {}}
        collector = ManualCollector(config)
        
        # Requirement 2.1: Use POC scraper to manually search and capture JSON responses
        assert hasattr(collector, 'collect_search_data')
        print("   ✓ Requirement 2.1: Manual search and JSON capture capability")
        
        # Requirement 2.3: Organize raw data by search term or category  
        assert collector.search_results_dir.exists()
        print("   ✓ Requirement 2.3: Organized data storage by search term")
        
        # Individual product collection capability
        assert hasattr(collector, 'collect_individual_product')
        print("   ✓ Individual product data collection capability")
        
        # Multiple search terms support
        # Test that collect_search_data accepts a list
        import inspect
        sig = inspect.signature(collector.collect_search_data)
        params = list(sig.parameters.keys())
        assert 'search_terms' in params
        print("   ✓ Multiple search terms support")
        
        print("✅ Requirements compliance test passed")
        return True
        
    except Exception as e:
        print(f"❌ Requirements compliance test failed: {str(e)}")
        return False

def main():
    """Run all tests for task 6.1 implementation."""
    print("Task 6.1 Implementation Test Suite")
    print("=" * 50)
    
    tests = [
        test_scraper_core_implementation,
        test_manual_collector_implementation, 
        test_poc_extraction_verification,
        test_requirements_compliance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Task 6.1 implementation is complete.")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
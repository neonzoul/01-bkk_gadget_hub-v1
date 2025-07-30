#!/usr/bin/env python3
"""
Example script demonstrating the enhanced ManualCollector with session management.

This script shows how to use the ManualCollector with:
- Session tracking
- Progress reporting
- Error handling and recovery
- Comprehensive logging
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.collectors.manual_collector import ManualCollector
from src.utils.config_loader import load_config, get_search_terms


def progress_callback(message: str):
    """
    Progress callback function to display collection progress.
    
    Args:
        message: Progress message to display
    """
    print(f"🔄 {message}")


def main():
    """Main function demonstrating session management features"""
    print("=" * 60)
    print("PowerBuy ManualCollector - Session Management Demo")
    print("=" * 60)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()
        
        # Get search terms (limit to 3 for demo)
        search_terms = get_search_terms(config)[:3]
        print(f"🔍 Search terms to process: {search_terms}")
        
        # Create collector with progress callback
        print("🚀 Initializing ManualCollector with session management...")
        collector = ManualCollector(config, progress_callback=progress_callback)
        
        # Check initial session status
        print("\n📊 Initial session status:")
        status = collector.get_session_status()
        print(f"   Status: {status['status']}")
        
        # Start collection with session management
        print(f"\n🎯 Starting collection for {len(search_terms)} search terms...")
        results = collector.collect_search_data(search_terms)
        
        # Display results
        print(f"\n✅ Collection completed! Results:")
        for term, file_path in results.items():
            print(f"   ✓ {term}: {file_path}")
        
        # Get final session status
        print(f"\n📊 Final session status:")
        final_status = collector.get_session_status()
        print(f"   Session ID: {final_status['session_id']}")
        print(f"   Status: {final_status['status']}")
        print(f"   Duration: {final_status['duration_seconds']:.1f} seconds")
        print(f"   Success Rate: {final_status['success_rate']:.1f}%")
        print(f"   Products Found: {final_status['total_products_found']}")
        print(f"   Files Created: {len(final_status['files_created'])}")
        print(f"   Errors: {final_status['error_count']}")
        
        # Get collection summary
        print(f"\n📋 Collection Summary:")
        summary = collector.get_collection_summary()
        print(f"   Successful Terms: {len(summary.search_terms_processed)}")
        print(f"   Total Products: {summary.total_products_found}")
        print(f"   Files Created: {len(summary.files_created)}")
        print(f"   Collection Time: {summary.collection_time}")
        
        if summary.errors:
            print(f"   Errors Encountered:")
            for error in summary.errors:
                print(f"     - {error}")
        
        print(f"\n🎉 Session management demo completed successfully!")
        print(f"📁 Check the 'logs/' directory for detailed session logs")
        print(f"📁 Check 'raw_data/search_results/' for collected data files")
        
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")
        
        # Even if there's an error, try to get session info
        if 'collector' in locals() and collector.current_session:
            print(f"\n📊 Session info at time of error:")
            status = collector.get_session_status()
            print(f"   Session ID: {status.get('session_id', 'N/A')}")
            print(f"   Errors: {status.get('error_count', 0)}")


if __name__ == "__main__":
    main()
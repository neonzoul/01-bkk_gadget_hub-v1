#!/usr/bin/env python3
"""
Test script for data organization and storage functionality.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.collectors.data_organizer import DataOrganizer
from src.collectors.manual_collector import ManualCollector
from src.utils.config_loader import load_config


def test_data_organizer():
    """Test the DataOrganizer functionality"""
    print("=" * 60)
    print("Testing DataOrganizer functionality")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Create DataOrganizer
    organizer = DataOrganizer(config)
    
    # Test 1: Directory structure creation
    print("\n=== Test 1: Directory Structure ===")
    structure = organizer.get_directory_structure()
    print(f"Base directory: {structure['base_data_dir']}")
    print("Directories created:")
    for name, path in structure['directories'].items():
        print(f"  {name}: {path}")
    
    # Test 2: Session management
    print("\n=== Test 2: Session Management ===")
    search_terms = ["test_iphone", "test_samsung"]
    session_info = organizer.start_session("test_session_001", search_terms)
    print(f"Session started: {session_info['session_id']}")
    print(f"Session directory: {session_info['session_dir']}")
    
    # Test 3: File naming and storage
    print("\n=== Test 3: File Storage ===")
    
    # Test search results storage
    test_search_data = {
        "products": [
            {"name": "Test iPhone", "sku": "TEST001", "price": 25000},
            {"name": "Test Samsung", "sku": "TEST002", "price": 20000}
        ]
    }
    
    search_file = organizer.save_search_results("test_iphone", test_search_data, "test_session_001")
    print(f"Search results saved to: {search_file}")
    
    # Test individual product storage
    test_product_data = {
        "name": "Test Product",
        "sku": "TEST003",
        "price": 15000,
        "details": "Test product details"
    }
    
    product_file = organizer.save_individual_product("TEST003", test_product_data, "test_session_001")
    print(f"Individual product saved to: {product_file}")
    
    # Test 4: Session completion
    print("\n=== Test 4: Session Completion ===")
    organizer.end_session("test_session_001", {
        "total_products": 3,
        "success_rate": 100.0,
        "duration": 30.5
    })
    print("Session completed successfully")
    
    # Test 5: Session listing
    print("\n=== Test 5: Session Information ===")
    sessions = organizer.list_sessions()
    print(f"Total sessions found: {len(sessions)}")
    
    if sessions:
        latest_session = sessions[0]
        print(f"Latest session: {latest_session['session_id']}")
        print(f"Files created: {len(latest_session.get('files_created', []))}")
        print(f"Products collected: {latest_session.get('products_collected', 0)}")
    
    # Test 6: Directory statistics
    print("\n=== Test 6: Directory Statistics ===")
    updated_structure = organizer.get_directory_structure()
    print("Directory statistics:")
    for name, stats in updated_structure['statistics'].items():
        print(f"  {name}: {stats['total_files']} files, {stats['total_size_mb']:.2f} MB")
    
    print("\n✅ DataOrganizer tests completed successfully!")


def test_manual_collector_integration():
    """Test ManualCollector integration with DataOrganizer"""
    print("\n" + "=" * 60)
    print("Testing ManualCollector integration with DataOrganizer")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    def progress_callback(message: str):
        print(f"[PROGRESS] {message}")
    
    # Create ManualCollector with progress callback
    collector = ManualCollector(config, progress_callback=progress_callback)
    
    # Test 1: Data organization info
    print("\n=== Test 1: Data Organization Info ===")
    org_info = collector.get_data_organization_info()
    print(f"Base directory: {org_info['base_data_dir']}")
    print("Available directories:")
    for name, path in org_info['directories'].items():
        print(f"  {name}: {path}")
    
    # Test 2: Session listing
    print("\n=== Test 2: Session Listing ===")
    sessions = collector.list_collection_sessions()
    print(f"Found {len(sessions)} previous sessions")
    
    for session in sessions[:3]:  # Show first 3 sessions
        print(f"  Session: {session['session_id']}")
        print(f"    Start: {session.get('start_time', 'N/A')}")
        print(f"    Status: {session.get('status', 'N/A')}")
        print(f"    Files: {len(session.get('files_created', []))}")
    
    # Test 3: Session details
    if sessions:
        print("\n=== Test 3: Session Details ===")
        latest_session_id = sessions[0]['session_id']
        details = collector.get_session_details(latest_session_id)
        
        if details:
            print(f"Session {latest_session_id} details:")
            print(f"  Search terms: {details.get('search_terms', [])}")
            print(f"  Duration: {details.get('duration_seconds', 0):.1f} seconds")
            print(f"  Products collected: {details.get('products_collected', 0)}")
            print(f"  Files created: {len(details.get('files_created', []))}")
    
    print("\n✅ ManualCollector integration tests completed successfully!")


def main():
    """Main test function"""
    try:
        test_data_organizer()
        test_manual_collector_integration()
        
        print("\n" + "=" * 60)
        print("🎉 All data organization tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
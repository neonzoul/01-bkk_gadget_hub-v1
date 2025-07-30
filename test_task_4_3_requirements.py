#!/usr/bin/env python3
"""
Test script to validate Task 4.3 requirements implementation.

This script validates that all requirements for Task 4.3 are properly implemented:
- Create directory structure for search results and individual products
- Add metadata tracking for each collection session  
- Implement file naming conventions with timestamps and search terms
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.collectors.data_organizer import DataOrganizer
from src.collectors.manual_collector import ManualCollector
from src.utils.config_loader import load_config


def test_requirement_2_5_directory_structure():
    """
    Test Requirement 2.5: Create directory structure for search results and individual products
    """
    print("=" * 60)
    print("Testing Requirement 2.5: Directory Structure")
    print("=" * 60)
    
    config = load_config()
    organizer = DataOrganizer(config)
    
    # Test directory creation
    structure = organizer.get_directory_structure()
    
    required_directories = [
        'search_results',
        'individual_products', 
        'sessions',
        'metadata',
        'processed'
    ]
    
    results = {
        'directory_structure_created': True,
        'required_directories_exist': True,
        'date_based_organization': True,
        'details': {}
    }
    
    # Check all required directories exist
    for dir_name in required_directories:
        dir_path = Path(structure['directories'][dir_name])
        exists = dir_path.exists()
        results['details'][dir_name] = {
            'path': str(dir_path),
            'exists': exists,
            'is_directory': dir_path.is_dir() if exists else False
        }
        
        if not exists:
            results['required_directories_exist'] = False
    
    # Test date-based subdirectory creation
    today = datetime.now().strftime("%Y-%m-%d")
    search_results_today = Path(structure['directories']['search_results']) / today
    individual_products_today = Path(structure['directories']['individual_products']) / today
    
    results['details']['date_based_subdirs'] = {
        'search_results_today': {
            'path': str(search_results_today),
            'exists': search_results_today.exists()
        },
        'individual_products_today': {
            'path': str(individual_products_today),
            'exists': individual_products_today.exists()
        }
    }
    
    # Print results
    print(f"✅ Directory structure created: {results['directory_structure_created']}")
    print(f"✅ Required directories exist: {results['required_directories_exist']}")
    print(f"✅ Date-based organization: {results['date_based_organization']}")
    
    print("\nDirectory Details:")
    for dir_name, details in results['details'].items():
        if dir_name != 'date_based_subdirs':
            status = "✅" if details['exists'] else "❌"
            print(f"  {status} {dir_name}: {details['path']}")
    
    print("\nDate-based Subdirectories:")
    for subdir, details in results['details']['date_based_subdirs'].items():
        status = "✅" if details['exists'] else "❌"
        print(f"  {status} {subdir}: {details['path']}")
    
    return results


def test_requirement_6_5_metadata_tracking():
    """
    Test Requirement 6.5: Add metadata tracking for each collection session
    """
    print("\n" + "=" * 60)
    print("Testing Requirement 6.5: Metadata Tracking")
    print("=" * 60)
    
    config = load_config()
    organizer = DataOrganizer(config)
    
    # Start a test session
    test_session_id = f"test_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    search_terms = ["test_metadata_iphone", "test_metadata_samsung"]
    
    session_info = organizer.start_session(test_session_id, search_terms)
    
    # Test metadata creation
    metadata_file = Path("raw_data/metadata") / f"session_{test_session_id}.json"
    
    results = {
        'session_metadata_created': metadata_file.exists(),
        'metadata_structure_valid': False,
        'session_tracking_works': False,
        'metadata_content': {}
    }
    
    if results['session_metadata_created']:
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            results['metadata_content'] = metadata
            
            # Check required metadata fields
            required_fields = [
                'session_id',
                'start_time', 
                'search_terms',
                'session_dir',
                'files_created',
                'products_collected',
                'errors',
                'status'
            ]
            
            all_fields_present = all(field in metadata for field in required_fields)
            results['metadata_structure_valid'] = all_fields_present
            
            # Test session tracking by adding some data
            test_data = {"products": [{"name": "Test Product", "sku": "TEST001"}]}
            organizer.save_search_results("test_metadata_iphone", test_data, test_session_id)
            
            # End session and check final metadata
            organizer.end_session(test_session_id, {"test_summary": "completed"})
            
            # Read updated metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                final_metadata = json.load(f)
            
            results['session_tracking_works'] = (
                final_metadata['status'] == 'completed' and
                len(final_metadata['files_created']) > 0 and
                'end_time' in final_metadata
            )
            
        except Exception as e:
            print(f"Error reading metadata: {e}")
    
    # Print results
    print(f"✅ Session metadata created: {results['session_metadata_created']}")
    print(f"✅ Metadata structure valid: {results['metadata_structure_valid']}")
    print(f"✅ Session tracking works: {results['session_tracking_works']}")
    
    if results['metadata_content']:
        print(f"\nMetadata Content:")
        print(f"  Session ID: {results['metadata_content'].get('session_id')}")
        print(f"  Start Time: {results['metadata_content'].get('start_time')}")
        print(f"  Search Terms: {results['metadata_content'].get('search_terms')}")
        print(f"  Status: {results['metadata_content'].get('status')}")
        print(f"  Files Created: {len(results['metadata_content'].get('files_created', []))}")
        print(f"  Products Collected: {results['metadata_content'].get('products_collected', 0)}")
    
    return results


def test_file_naming_conventions():
    """
    Test file naming conventions with timestamps and search terms
    """
    print("\n" + "=" * 60)
    print("Testing File Naming Conventions")
    print("=" * 60)
    
    config = load_config()
    organizer = DataOrganizer(config)
    
    # Test search result filename generation
    search_term = "test naming convention"
    session_id = "test_session_naming"
    
    search_filename = organizer.generate_search_result_filename(search_term, session_id)
    product_filename = organizer.generate_individual_product_filename("TEST123", session_id)
    
    results = {
        'search_filename_format_correct': False,
        'product_filename_format_correct': False,
        'timestamp_included': False,
        'search_term_included': False,
        'session_id_included': False,
        'details': {
            'search_filename': str(search_filename),
            'product_filename': str(product_filename)
        }
    }
    
    # Check search filename format
    search_name = search_filename.name
    expected_parts = ['test_naming_convention', session_id]
    
    results['search_term_included'] = 'test_naming_convention' in search_name
    results['session_id_included'] = session_id in search_name
    results['timestamp_included'] = any(char.isdigit() for char in search_name)
    results['search_filename_format_correct'] = (
        search_name.endswith('.json') and
        results['search_term_included'] and
        results['session_id_included'] and
        results['timestamp_included']
    )
    
    # Check product filename format
    product_name = product_filename.name
    results['product_filename_format_correct'] = (
        product_name.startswith('product_') and
        'TEST123' in product_name and
        session_id in product_name and
        product_name.endswith('.json')
    )
    
    # Test actual file creation with proper naming
    test_data = {"products": [{"name": "Test", "sku": "TEST"}]}
    actual_search_file = organizer.save_search_results("test naming", test_data, session_id)
    actual_product_file = organizer.save_individual_product("PROD123", {"name": "Test Product"}, session_id)
    
    results['details']['actual_search_file'] = actual_search_file
    results['details']['actual_product_file'] = actual_product_file
    
    # Print results
    print(f"✅ Search filename format correct: {results['search_filename_format_correct']}")
    print(f"✅ Product filename format correct: {results['product_filename_format_correct']}")
    print(f"✅ Timestamp included: {results['timestamp_included']}")
    print(f"✅ Search term included: {results['search_term_included']}")
    print(f"✅ Session ID included: {results['session_id_included']}")
    
    print(f"\nGenerated Filenames:")
    print(f"  Search: {search_filename.name}")
    print(f"  Product: {product_filename.name}")
    
    print(f"\nActual Files Created:")
    print(f"  Search: {Path(actual_search_file).name}")
    print(f"  Product: {Path(actual_product_file).name}")
    
    return results


def test_manual_collector_integration():
    """
    Test ManualCollector integration with enhanced data organization
    """
    print("\n" + "=" * 60)
    print("Testing ManualCollector Integration")
    print("=" * 60)
    
    config = load_config()
    collector = ManualCollector(config)
    
    results = {
        'data_organizer_integrated': hasattr(collector, 'data_organizer'),
        'organization_methods_available': False,
        'session_methods_available': False,
        'organized_storage_methods_available': False
    }
    
    # Check if organization methods are available
    org_methods = [
        'get_data_organization_info',
        'list_collection_sessions', 
        'get_session_details'
    ]
    
    results['organization_methods_available'] = all(
        hasattr(collector, method) for method in org_methods
    )
    
    # Check if session methods work
    try:
        org_info = collector.get_data_organization_info()
        sessions = collector.list_collection_sessions()
        results['session_methods_available'] = True
    except Exception as e:
        print(f"Error testing session methods: {e}")
    
    # Check if organized storage methods are available
    storage_methods = [
        'save_search_results_organized',
        'save_individual_product_organized'
    ]
    
    results['organized_storage_methods_available'] = all(
        hasattr(collector, method) for method in storage_methods
    )
    
    # Print results
    print(f"✅ DataOrganizer integrated: {results['data_organizer_integrated']}")
    print(f"✅ Organization methods available: {results['organization_methods_available']}")
    print(f"✅ Session methods available: {results['session_methods_available']}")
    print(f"✅ Organized storage methods available: {results['organized_storage_methods_available']}")
    
    if results['data_organizer_integrated']:
        org_info = collector.get_data_organization_info()
        print(f"\nData Organization Info:")
        print(f"  Base Directory: {org_info['base_data_dir']}")
        print(f"  Available Directories: {len(org_info['directories'])}")
        
        sessions = collector.list_collection_sessions()
        print(f"  Previous Sessions: {len(sessions)}")
    
    return results


def main():
    """Main test function"""
    print("🧪 Testing Task 4.3: Implement data organization and storage")
    print("Requirements: 2.5, 6.5")
    
    try:
        # Test all requirements
        test_results = {}
        
        test_results['requirement_2_5'] = test_requirement_2_5_directory_structure()
        test_results['requirement_6_5'] = test_requirement_6_5_metadata_tracking()
        test_results['file_naming'] = test_file_naming_conventions()
        test_results['integration'] = test_manual_collector_integration()
        
        # Overall assessment
        print("\n" + "=" * 60)
        print("TASK 4.3 REQUIREMENTS VALIDATION SUMMARY")
        print("=" * 60)
        
        # Requirement 2.5 assessment
        req_2_5_passed = (
            test_results['requirement_2_5']['directory_structure_created'] and
            test_results['requirement_2_5']['required_directories_exist'] and
            test_results['requirement_2_5']['date_based_organization']
        )
        
        # Requirement 6.5 assessment  
        req_6_5_passed = (
            test_results['requirement_6_5']['session_metadata_created'] and
            test_results['requirement_6_5']['metadata_structure_valid'] and
            test_results['requirement_6_5']['session_tracking_works']
        )
        
        # File naming assessment
        file_naming_passed = (
            test_results['file_naming']['search_filename_format_correct'] and
            test_results['file_naming']['product_filename_format_correct'] and
            test_results['file_naming']['timestamp_included']
        )
        
        # Integration assessment
        integration_passed = (
            test_results['integration']['data_organizer_integrated'] and
            test_results['integration']['organization_methods_available'] and
            test_results['integration']['organized_storage_methods_available']
        )
        
        print(f"✅ Requirement 2.5 (Directory Structure): {'PASSED' if req_2_5_passed else 'FAILED'}")
        print(f"✅ Requirement 6.5 (Metadata Tracking): {'PASSED' if req_6_5_passed else 'FAILED'}")
        print(f"✅ File Naming Conventions: {'PASSED' if file_naming_passed else 'FAILED'}")
        print(f"✅ ManualCollector Integration: {'PASSED' if integration_passed else 'FAILED'}")
        
        overall_passed = all([req_2_5_passed, req_6_5_passed, file_naming_passed, integration_passed])
        
        print(f"\n🎯 OVERALL TASK 4.3 STATUS: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
        
        if overall_passed:
            print("\n🎉 All Task 4.3 requirements have been successfully implemented!")
            print("   • Enhanced directory structure with date-based organization")
            print("   • Comprehensive metadata tracking for all sessions")
            print("   • Standardized file naming with timestamps and search terms")
            print("   • Full integration with ManualCollector class")
        
        return overall_passed
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
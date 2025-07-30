#!/usr/bin/env python3
"""
Example script demonstrating enhanced data organization and storage features.

This script shows how to use the ManualCollector with the new DataOrganizer
for organized data storage, session management, and metadata tracking.
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


def demonstrate_data_organization():
    """Demonstrate the enhanced data organization features"""
    print("=" * 70)
    print("PowerBuy ManualCollector - Enhanced Data Organization Demo")
    print("=" * 70)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()
        
        # Get search terms (limit to 2 for demo)
        search_terms = get_search_terms(config)[:2]
        print(f"🔍 Search terms to process: {search_terms}")
        
        # Create collector with progress callback
        print("🚀 Initializing ManualCollector with enhanced data organization...")
        collector = ManualCollector(config, progress_callback=progress_callback)
        
        # Display data organization structure
        print("\n📁 Data Organization Structure:")
        org_info = collector.get_data_organization_info()
        print(f"   Base Directory: {org_info['base_data_dir']}")
        print("   Organized Directories:")
        for name, path in org_info['directories'].items():
            stats = org_info['statistics'][name]
            print(f"     📂 {name}: {path}")
            print(f"        Files: {stats['total_files']}, Size: {stats['total_size_mb']:.2f} MB")
        
        # Show existing sessions
        print(f"\n📊 Previous Collection Sessions:")
        sessions = collector.list_collection_sessions()
        if sessions:
            print(f"   Found {len(sessions)} previous sessions:")
            for session in sessions[:3]:  # Show first 3
                print(f"     🗓️  {session['session_id']} - {session.get('status', 'unknown')}")
                print(f"        Start: {session.get('start_time', 'N/A')[:19]}")
                print(f"        Files: {len(session.get('files_created', []))}")
                print(f"        Products: {session.get('products_collected', 0)}")
        else:
            print("   No previous sessions found")
        
        # Start new collection with organized storage
        print(f"\n🎯 Starting organized collection for {len(search_terms)} search terms...")
        results = collector.collect_search_data(search_terms)
        
        # Display results with organization info
        print(f"\n✅ Collection completed with organized storage!")
        print("📄 Files created:")
        for term, file_path in results.items():
            print(f"   ✓ {term}: {Path(file_path).name}")
            print(f"     Location: {Path(file_path).parent}")
        
        # Get session status
        print(f"\n📊 Current Session Status:")
        session_status = collector.get_session_status()
        if session_status['status'] != 'no_active_session':
            print(f"   Session ID: {session_status['session_id']}")
            print(f"   Status: {session_status['status']}")
            print(f"   Duration: {session_status['duration_seconds']:.1f} seconds")
            print(f"   Success Rate: {session_status['success_rate']:.1f}%")
            print(f"   Products Found: {session_status['total_products_found']}")
            print(f"   Files Created: {len(session_status['files_created'])}")
        
        # Show updated organization statistics
        print(f"\n📈 Updated Data Organization Statistics:")
        updated_org_info = collector.get_data_organization_info()
        for name, stats in updated_org_info['statistics'].items():
            print(f"   📂 {name}: {stats['total_files']} files, {stats['total_size_mb']:.2f} MB")
        
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
                print(f"     ⚠️  {error}")
        
        # Show session details
        if session_status['status'] != 'no_active_session':
            print(f"\n🔍 Session Details:")
            session_details = collector.get_session_details(session_status['session_id'])
            if session_details:
                print(f"   Search Terms: {session_details.get('search_terms', [])}")
                print(f"   Files Created:")
                for file_path in session_details.get('files_created', []):
                    print(f"     📄 {Path(file_path).name}")
        
        print(f"\n🎉 Enhanced data organization demo completed successfully!")
        print(f"📁 Check the organized directory structure in 'raw_data/' for:")
        print(f"   • Date-organized search results and individual products")
        print(f"   • Session-specific directories and metadata")
        print(f"   • Comprehensive metadata tracking")
        print(f"   • Organized file naming with timestamps")
        
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")
        
        # Even if there's an error, show organization info
        try:
            if 'collector' in locals():
                print(f"\n📊 Data organization info at time of error:")
                org_info = collector.get_data_organization_info()
                print(f"   Base directory: {org_info['base_data_dir']}")
                for name, stats in org_info['statistics'].items():
                    print(f"   {name}: {stats['total_files']} files")
        except:
            pass


def show_directory_structure():
    """Show the enhanced directory structure"""
    print("\n" + "=" * 50)
    print("Enhanced Directory Structure")
    print("=" * 50)
    
    base_dir = Path("raw_data")
    if base_dir.exists():
        print(f"📁 {base_dir}/")
        
        # Show organized structure
        subdirs = [
            "search_results/",
            "individual_products/", 
            "sessions/",
            "metadata/",
            "processed/"
        ]
        
        for subdir in subdirs:
            subdir_path = base_dir / subdir
            if subdir_path.exists():
                files = list(subdir_path.rglob("*"))
                print(f"   📂 {subdir} ({len([f for f in files if f.is_file()])} files)")
                
                # Show date-based organization
                for date_dir in sorted(subdir_path.iterdir()):
                    if date_dir.is_dir():
                        date_files = list(date_dir.glob("*.json"))
                        if date_files:
                            print(f"      📅 {date_dir.name}/ ({len(date_files)} files)")
                            for file in date_files[:3]:  # Show first 3 files
                                print(f"         📄 {file.name}")
                            if len(date_files) > 3:
                                print(f"         ... and {len(date_files) - 3} more files")


if __name__ == "__main__":
    demonstrate_data_organization()
    show_directory_structure()
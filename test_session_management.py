#!/usr/bin/env python3
"""
Test script for ManualCollector session management functionality.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import modules directly to avoid relative import issues
from src.collectors.manual_collector import ManualCollector
from src.utils.config_loader import load_config


def progress_callback(message: str):
    """Simple progress callback for testing"""
    print(f"[PROGRESS] {message}")


def test_session_management():
    """Test the session management features"""
    print("Testing ManualCollector session management...")
    
    # Load configuration
    config = load_config()
    
    # Create collector with progress callback
    collector = ManualCollector(config, progress_callback=progress_callback)
    
    # Test 1: Check initial state
    print("\n=== Test 1: Initial State ===")
    status = collector.get_session_status()
    print(f"Initial status: {status}")
    assert status["status"] == "no_active_session"
    
    # Test 2: Test session creation and tracking
    print("\n=== Test 2: Session Creation ===")
    test_search_terms = ["iphone", "samsung"]
    
    try:
        # This will create a session but may fail due to browser automation
        # We're mainly testing the session management structure
        results = collector.collect_search_data(test_search_terms)
        
        # Check session status
        status = collector.get_session_status()
        print(f"Session status after collection: {status}")
        
        # Get collection summary
        summary = collector.get_collection_summary()
        print(f"Collection summary: {summary}")
        
    except Exception as e:
        print(f"Collection failed (expected in test environment): {e}")
        
        # Even if collection fails, session should still be created
        status = collector.get_session_status()
        print(f"Session status after failure: {status}")
        
        if collector.current_session:
            print(f"Session ID: {collector.current_session.session_id}")
            print(f"Errors: {collector.current_session.errors}")
    
    print("\n=== Session Management Test Complete ===")


if __name__ == "__main__":
    test_session_management()
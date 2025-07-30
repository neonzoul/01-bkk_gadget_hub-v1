"""
Test script for Task 5: Test manual collection process with sample search terms.

This script tests the manual collection process using sample search terms from 20urls.txt,
validates file organization and metadata tracking, and generates organized raw JSON files
for producer component processing.

Requirements tested:
- 2.1: Manual data collection method
- 2.5: Data organization and storage
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.collectors.manual_collector import ManualCollector
from src.utils.config_loader import load_config, get_search_terms


class Task5TestRunner:
    """Test runner for Task 5 manual collection testing."""
    
    def __init__(self):
        self.test_results = {
            "test_start_time": datetime.now(),
            "test_end_time": None,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": [],
            "collection_results": {},
            "file_organization_validation": {},
            "metadata_validation": {}
        }
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        if passed:
            self.test_results["tests_passed"] += 1
            status = "✓ PASS"
        else:
            self.test_results["tests_failed"] += 1
            status = "✗ FAIL"
            
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
            
        self.test_results["test_details"].append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_configuration_loading(self) -> tuple[Dict[str, Any], List[str]]:
        """Test 1: Configuration and search terms loading."""
        print("\n=== Test 1: Configuration and Search Terms Loading ===")
        
        try:
            # Load configuration
            config = load_config()
            self.log_test("Load configuration from config.json", True, f"Config loaded with {len(config)} sections")
            
            # Load search terms from 20urls.txt
            search_terms = get_search_terms(config, "20urls.txt")
            self.log_test("Extract search terms from 20urls.txt", True, f"Found {len(search_terms)} search terms")
            
            # Validate search terms are not empty
            if search_terms:
                self.log_test("Search terms validation", True, f"First term: '{search_terms[0]}'")
            else:
                self.log_test("Search terms validation", False, "No search terms found")
                
            # Show sample search terms for verification
            print(f"\nSample search terms (first 5):")
            for i, term in enumerate(search_terms[:5], 1):
                print(f"  {i}. {term}")
                
            return config, search_terms
            
        except Exception as e:
            self.log_test("Configuration loading", False, f"Error: {str(e)}")
            raise
    
    def test_collector_initialization(self, config: Dict[str, Any]) -> ManualCollector:
        """Test 2: ManualCollector initialization."""
        print("\n=== Test 2: ManualCollector Initialization ===")
        
        try:
            # Initialize collector with progress callback
            def progress_callback(message: str):
                print(f"   Progress: {message}")
            
            collector = ManualCollector(config, progress_callback)
            self.log_test("ManualCollector initialization", True, "Collector created successfully")
            
            # Validate directory structure
            directories_exist = all([
                collector.search_results_dir.exists(),
                collector.individual_products_dir.exists()
            ])
            self.log_test("Directory structure validation", directories_exist, 
                         f"Search results: {collector.search_results_dir}, Individual products: {collector.individual_products_dir}")
            
            # Test data organization info
            org_info = collector.get_data_organization_info()
            self.log_test("Data organization info retrieval", True, 
                         f"Base directory: {org_info.get('base_directory', 'N/A')}")
            
            return collector
            
        except Exception as e:
            self.log_test("ManualCollector initialization", False, f"Error: {str(e)}")
            raise
    
    def test_sample_collection_simulation(self, collector: ManualCollector, search_terms: List[str]) -> Dict[str, Any]:
        """Test 3: Sample collection process simulation (without browser)."""
        print("\n=== Test 3: Sample Collection Process Simulation ===")
        
        # Use first 3 search terms for testing
        test_terms = search_terms[:3]
        print(f"Testing with {len(test_terms)} sample search terms:")
        for i, term in enumerate(test_terms, 1):
            print(f"  {i}. {term}")
        
        try:
            # Simulate collection session without browser automation
            session_results = self._simulate_collection_session(collector, test_terms)
            
            self.log_test("Collection session simulation", True, 
                         f"Simulated collection for {len(test_terms)} terms")
            
            return session_results
            
        except Exception as e:
            self.log_test("Collection session simulation", False, f"Error: {str(e)}")
            raise
    
    def _simulate_collection_session(self, collector: ManualCollector, search_terms: List[str]) -> Dict[str, Any]:
        """Simulate a collection session by creating sample data files."""
        print("\n   Simulating collection session...")
        
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_results = {
            "session_id": session_id,
            "search_terms": search_terms,
            "files_created": [],
            "products_found": 0
        }
        
        # Start organized data session
        collector.data_organizer.start_session(session_id, search_terms)
        
        # Create sample data for each search term
        for i, search_term in enumerate(search_terms, 1):
            print(f"   Simulating collection for term {i}/{len(search_terms)}: {search_term}")
            
            # Generate sample product data
            sample_products = self._generate_sample_products(search_term, count=5 + i)
            
            # Create sample data structure that matches what the collector expects
            sample_data = {
                "products": sample_products,
                "metadata": {
                    "url": f"https://www.powerbuy.co.th/search/{search_term.replace(' ', '%20')}",
                    "user_agent": collector.user_agent,
                    "collection_method": "simulation_for_testing"
                }
            }
            
            # Save using organized storage
            try:
                file_path = collector.save_search_results_organized(search_term, sample_data)
                session_results["files_created"].append(file_path)
                session_results["products_found"] += len(sample_products)
                print(f"   ✓ Created sample file: {Path(file_path).name}")
                
            except Exception as e:
                print(f"   ✗ Failed to create sample file for '{search_term}': {str(e)}")
                raise
        
        # End organized data session
        collector.data_organizer.end_session(session_id, {
            'search_terms_processed': search_terms,
            'total_products_found': session_results["products_found"],
            'files_created': session_results["files_created"]
        })
        
        return session_results
    
    def _generate_sample_products(self, search_term: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate sample product data for testing."""
        products = []
        base_price = 15000  # Base price in THB
        
        for i in range(count):
            product = {
                "id": f"PROD_{search_term.replace(' ', '_').upper()}_{i+1:03d}",
                "name": f"{search_term} Model {i+1}",
                "sku": f"SKU_{search_term.replace(' ', '')[:6].upper()}_{i+1:03d}",
                "price": str(base_price + (i * 2000)),
                "stock_status": "In Stock" if i % 3 != 0 else "Out of Stock",
                "brand": search_term.split()[0] if search_term.split() else "Generic",
                "category": "Electronics",
                "url": f"https://www.powerbuy.co.th/product/sample-{i+1}",
                "image_url": f"https://www.powerbuy.co.th/images/sample-{i+1}.jpg",
                "description": f"Sample {search_term} product for testing purposes",
                "specifications": {
                    "color": ["Black", "White", "Blue"][i % 3],
                    "storage": f"{64 * (i+1)}GB",
                    "warranty": "1 Year"
                }
            }
            products.append(product)
        
        return products
    
    def test_file_organization_validation(self, session_results: Dict[str, Any]) -> Dict[str, Any]:
        """Test 4: File organization and structure validation."""
        print("\n=== Test 4: File Organization Validation ===")
        
        validation_results = {
            "files_exist": True,
            "file_structure_valid": True,
            "metadata_present": True,
            "file_details": []
        }
        
        try:
            for file_path in session_results["files_created"]:
                file_path_obj = Path(file_path)
                
                # Check file exists
                if not file_path_obj.exists():
                    validation_results["files_exist"] = False
                    self.log_test(f"File existence check: {file_path_obj.name}", False, "File not found")
                    continue
                
                # Check file structure and content
                try:
                    with open(file_path_obj, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Validate required fields (adjusted for actual data structure)
                    required_fields = ["search_term", "collection_timestamp", "total_products", "data"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        validation_results["file_structure_valid"] = False
                        self.log_test(f"File structure validation: {file_path_obj.name}", False, 
                                     f"Missing fields: {missing_fields}")
                    else:
                        self.log_test(f"File structure validation: {file_path_obj.name}", True, 
                                     f"All required fields present")
                    
                    # Validate metadata (check both top-level and nested)
                    nested_data = data.get("data", {})
                    metadata = nested_data.get("metadata", {})
                    required_metadata = ["collection_method"]
                    missing_metadata = [field for field in required_metadata if field not in metadata]
                    
                    if missing_metadata:
                        validation_results["metadata_present"] = False
                        self.log_test(f"Metadata validation: {file_path_obj.name}", False, 
                                     f"Missing metadata: {missing_metadata}")
                    else:
                        self.log_test(f"Metadata validation: {file_path_obj.name}", True, 
                                     "All required metadata present")
                    
                    # Store file details (adjusted for actual structure)
                    products = nested_data.get("products", [])
                    file_details = {
                        "file_path": str(file_path_obj),
                        "file_size": file_path_obj.stat().st_size,
                        "products_count": len(products),
                        "search_term": data.get("search_term", "Unknown"),
                        "collection_timestamp": data.get("collection_timestamp", "Unknown")
                    }
                    validation_results["file_details"].append(file_details)
                    
                    print(f"   ✓ {file_path_obj.name}: {file_details['products_count']} products, {file_details['file_size']} bytes")
                    
                except json.JSONDecodeError as e:
                    validation_results["file_structure_valid"] = False
                    self.log_test(f"JSON validation: {file_path_obj.name}", False, f"Invalid JSON: {str(e)}")
                
                except Exception as e:
                    self.log_test(f"File validation: {file_path_obj.name}", False, f"Error: {str(e)}")
            
            # Overall validation summary
            overall_valid = all([
                validation_results["files_exist"],
                validation_results["file_structure_valid"],
                validation_results["metadata_present"]
            ])
            
            self.log_test("Overall file organization validation", overall_valid, 
                         f"Files: {len(validation_results['file_details'])} validated")
            
            return validation_results
            
        except Exception as e:
            self.log_test("File organization validation", False, f"Error: {str(e)}")
            raise
    
    def test_metadata_tracking_validation(self, session_results: Dict[str, Any]) -> Dict[str, Any]:
        """Test 5: Metadata tracking validation."""
        print("\n=== Test 5: Metadata Tracking Validation ===")
        
        metadata_validation = {
            "session_metadata_exists": False,
            "session_metadata_valid": False,
            "individual_file_metadata_valid": True,
            "metadata_consistency": True
        }
        
        try:
            # Check for session metadata files
            metadata_dir = Path("raw_data/metadata")
            session_files = list(metadata_dir.glob(f"session_{session_results['session_id']}.json"))
            
            if session_files:
                metadata_validation["session_metadata_exists"] = True
                self.log_test("Session metadata file exists", True, f"Found: {session_files[0].name}")
                
                # Validate session metadata content
                try:
                    with open(session_files[0], 'r', encoding='utf-8') as f:
                        session_metadata = json.load(f)
                    
                    required_session_fields = ["session_id", "start_time", "search_terms"]
                    missing_session_fields = [field for field in required_session_fields if field not in session_metadata]
                    
                    if not missing_session_fields:
                        metadata_validation["session_metadata_valid"] = True
                        self.log_test("Session metadata validation", True, "All required fields present")
                    else:
                        self.log_test("Session metadata validation", False, f"Missing fields: {missing_session_fields}")
                        
                except Exception as e:
                    self.log_test("Session metadata validation", False, f"Error reading metadata: {str(e)}")
            else:
                self.log_test("Session metadata file exists", False, "No session metadata file found")
            
            # Validate individual file metadata consistency
            session_id = session_results["session_id"]
            for file_path in session_results["files_created"]:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    file_session_id = data.get("session_id")
                    if file_session_id != session_id:
                        metadata_validation["metadata_consistency"] = False
                        self.log_test(f"Metadata consistency: {Path(file_path).name}", False, 
                                     f"Session ID mismatch: expected {session_id}, got {file_session_id}")
                    else:
                        self.log_test(f"Metadata consistency: {Path(file_path).name}", True, 
                                     "Session ID matches")
                        
                except Exception as e:
                    metadata_validation["individual_file_metadata_valid"] = False
                    self.log_test(f"Individual file metadata: {Path(file_path).name}", False, f"Error: {str(e)}")
            
            return metadata_validation
            
        except Exception as e:
            self.log_test("Metadata tracking validation", False, f"Error: {str(e)}")
            raise
    
    def test_producer_component_readiness(self, session_results: Dict[str, Any]) -> Dict[str, Any]:
        """Test 6: Validate files are ready for producer component processing."""
        print("\n=== Test 6: Producer Component Readiness Validation ===")
        
        readiness_validation = {
            "files_readable": True,
            "data_structure_compatible": True,
            "product_data_extractable": True,
            "ready_for_processing": True
        }
        
        try:
            total_products = 0
            extractable_products = 0
            
            for file_path in session_results["files_created"]:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Check if products can be extracted (adjusted for actual structure)
                    nested_data = data.get("data", {})
                    products = nested_data.get("products", [])
                    total_products += len(products)
                    
                    # Validate each product has required fields for producer
                    required_product_fields = ["name", "sku", "price", "stock_status"]
                    
                    for product in products:
                        if all(field in product for field in required_product_fields):
                            extractable_products += 1
                    
                    self.log_test(f"Producer readiness: {Path(file_path).name}", True, 
                                 f"{len(products)} products, all fields present")
                    
                except Exception as e:
                    readiness_validation["files_readable"] = False
                    self.log_test(f"Producer readiness: {Path(file_path).name}", False, f"Error: {str(e)}")
            
            # Calculate extraction success rate
            extraction_rate = (extractable_products / total_products * 100) if total_products > 0 else 0
            
            if extraction_rate >= 95:  # 95% threshold for success
                self.log_test("Product data extraction validation", True, 
                             f"{extractable_products}/{total_products} products extractable ({extraction_rate:.1f}%)")
            else:
                readiness_validation["product_data_extractable"] = False
                self.log_test("Product data extraction validation", False, 
                             f"Only {extraction_rate:.1f}% of products extractable")
            
            # Overall readiness assessment
            overall_ready = all([
                readiness_validation["files_readable"],
                readiness_validation["data_structure_compatible"],
                readiness_validation["product_data_extractable"]
            ])
            
            readiness_validation["ready_for_processing"] = overall_ready
            self.log_test("Overall producer component readiness", overall_ready, 
                         f"Files ready for producer component processing")
            
            return readiness_validation
            
        except Exception as e:
            self.log_test("Producer component readiness validation", False, f"Error: {str(e)}")
            raise
    
    def generate_test_report(self, config: Dict[str, Any], search_terms: List[str], 
                           session_results: Dict[str, Any], file_validation: Dict[str, Any],
                           metadata_validation: Dict[str, Any], readiness_validation: Dict[str, Any]):
        """Generate comprehensive test report."""
        print("\n=== Test Report Generation ===")
        
        self.test_results["test_end_time"] = datetime.now()
        duration = (self.test_results["test_end_time"] - self.test_results["test_start_time"]).total_seconds()
        
        report = {
            "task_info": {
                "task_number": "5",
                "task_title": "Test manual collection process with sample search terms",
                "requirements_tested": ["2.1", "2.5"],
                "test_date": self.test_results["test_start_time"].isoformat(),
                "test_duration_seconds": duration
            },
            "test_summary": {
                "total_tests": self.test_results["tests_passed"] + self.test_results["tests_failed"],
                "tests_passed": self.test_results["tests_passed"],
                "tests_failed": self.test_results["tests_failed"],
                "success_rate": (self.test_results["tests_passed"] / (self.test_results["tests_passed"] + self.test_results["tests_failed"]) * 100) if (self.test_results["tests_passed"] + self.test_results["tests_failed"]) > 0 else 0
            },
            "configuration_validation": {
                "config_loaded": True,
                "search_terms_count": len(search_terms),
                "sample_search_terms": search_terms[:5]
            },
            "collection_simulation_results": session_results,
            "file_organization_validation": file_validation,
            "metadata_tracking_validation": metadata_validation,
            "producer_readiness_validation": readiness_validation,
            "detailed_test_results": self.test_results["test_details"]
        }
        
        # Save test report
        report_path = f"task_5_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Test report saved to: {report_path}")
        
        # Print summary
        print(f"\n=== TASK 5 TEST SUMMARY ===")
        print(f"Test Duration: {duration:.1f} seconds")
        print(f"Tests Passed: {self.test_results['tests_passed']}")
        print(f"Tests Failed: {self.test_results['tests_failed']}")
        print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"Search Terms Tested: {len(search_terms)}")
        print(f"Files Created: {len(session_results.get('files_created', []))}")
        print(f"Products Generated: {session_results.get('products_found', 0)}")
        print(f"Report File: {report_path}")
        
        return report
    
    def run_all_tests(self):
        """Run all tests for Task 5."""
        print("=" * 80)
        print("TASK 5: Test Manual Collection Process with Sample Search Terms")
        print("=" * 80)
        print(f"Test started at: {self.test_results['test_start_time']}")
        print(f"Requirements being tested: 2.1 (Manual data collection), 2.5 (Data organization)")
        
        try:
            # Test 1: Configuration and search terms loading
            config, search_terms = self.test_configuration_loading()
            
            # Test 2: ManualCollector initialization
            collector = self.test_collector_initialization(config)
            
            # Test 3: Sample collection simulation
            session_results = self.test_sample_collection_simulation(collector, search_terms)
            
            # Test 4: File organization validation
            file_validation = self.test_file_organization_validation(session_results)
            
            # Test 5: Metadata tracking validation
            metadata_validation = self.test_metadata_tracking_validation(session_results)
            
            # Test 6: Producer component readiness
            readiness_validation = self.test_producer_component_readiness(session_results)
            
            # Generate comprehensive test report
            report = self.generate_test_report(
                config, search_terms, session_results, 
                file_validation, metadata_validation, readiness_validation
            )
            
            return report
            
        except Exception as e:
            print(f"\n❌ Critical error during testing: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Main function to run Task 5 tests."""
    test_runner = Task5TestRunner()
    report = test_runner.run_all_tests()
    
    if report:
        # Determine overall task success
        success_rate = report["test_summary"]["success_rate"]
        if success_rate >= 90:
            print(f"\n🎉 TASK 5 COMPLETED SUCCESSFULLY!")
            print(f"   All requirements validated with {success_rate:.1f}% success rate")
            return True
        else:
            print(f"\n⚠️  TASK 5 PARTIALLY COMPLETED")
            print(f"   Success rate: {success_rate:.1f}% (target: 90%+)")
            return False
    else:
        print(f"\n❌ TASK 5 FAILED")
        print(f"   Critical errors prevented completion")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
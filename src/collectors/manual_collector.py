"""
Enhanced Manual Collector for PowerBuy product data collection.

This module refactors the existing POC scraper into a structured ManualCollector class
that supports multiple search terms, organized storage, and metadata tracking.
"""

import os
import json
import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from ..validators.models import CollectionSummary
from .data_organizer import DataOrganizer


class CollectionSession:
    """Manages collection session state and tracking"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = datetime.now()
        self.end_time = None
        self.search_terms_processed = []
        self.search_terms_failed = []
        self.total_products_found = 0
        self.files_created = []
        self.errors = []
        self.current_search_term = None
        self.progress_callback = None
        
    def start_search_term(self, search_term: str):
        """Mark the start of processing a search term"""
        self.current_search_term = search_term
        if self.progress_callback:
            self.progress_callback(f"Starting collection for: {search_term}")
    
    def complete_search_term(self, search_term: str, products_found: int, file_path: str = None):
        """Mark successful completion of a search term"""
        self.search_terms_processed.append(search_term)
        self.total_products_found += products_found
        if file_path:
            self.files_created.append(file_path)
        if self.progress_callback:
            self.progress_callback(f"Completed {search_term}: {products_found} products found")
    
    def fail_search_term(self, search_term: str, error: str):
        """Mark failure of a search term"""
        self.search_terms_failed.append(search_term)
        self.errors.append(f"Search term '{search_term}': {error}")
        if self.progress_callback:
            self.progress_callback(f"Failed {search_term}: {error}")
    
    def add_error(self, error: str):
        """Add a general error to the session"""
        self.errors.append(error)
        if self.progress_callback:
            self.progress_callback(f"Error: {error}")
    
    def end_session(self):
        """Mark the end of the collection session"""
        self.end_time = datetime.now()
        if self.progress_callback:
            duration = (self.end_time - self.start_time).total_seconds()
            self.progress_callback(f"Session completed in {duration:.1f} seconds")
    
    def get_duration(self) -> float:
        """Get session duration in seconds"""
        end_time = self.end_time or datetime.now()
        return (end_time - self.start_time).total_seconds()
    
    def get_success_rate(self) -> float:
        """Calculate success rate as percentage"""
        total_attempts = len(self.search_terms_processed) + len(self.search_terms_failed)
        if total_attempts == 0:
            return 0.0
        return (len(self.search_terms_processed) / total_attempts) * 100


class ManualCollector:
    """
    Enhanced manual collector class for PowerBuy product data collection.
    
    Refactored from the original POC scraper to support:
    - Multiple search terms processing
    - Organized JSON file storage with timestamps
    - Session management with progress tracking
    - Error handling and recovery mechanisms
    - Detailed logging and reporting
    """
    
    def __init__(self, config: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the ManualCollector with configuration.
        
        Args:
            config: Configuration dictionary containing scraping settings
            progress_callback: Optional callback function for progress updates
        """
        self.config = config
        self.base_url = config.get('scraping', {}).get('base_url', 'https://www.powerbuy.co.th')
        self.user_agent = config.get('scraping', {}).get('user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Initialize data organizer for enhanced storage management
        self.data_organizer = DataOrganizer(config)
        
        # Legacy directory references for backward compatibility
        self.search_results_dir = self.data_organizer.search_results_dir
        self.individual_products_dir = self.data_organizer.individual_products_dir
        
        # Session management
        self.current_session = None
        self.progress_callback = progress_callback
        
        # Error recovery settings
        self.max_retries = config.get('scraping', {}).get('max_retries', 3)
        self.retry_delay = config.get('scraping', {}).get('retry_delay', 5)
        
        # Browser context directory
        self.user_data_dir = Path("user_data")
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the collector"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create session-specific log file
        log_filename = f"collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = log_dir / log_filename
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ManualCollector initialized with log file: {log_path}")
    
    def collect_search_data(self, search_terms: List[str]) -> Dict[str, str]:
        """
        Collect product data for multiple search terms with session management.
        
        Args:
            search_terms: List of search terms to process
            
        Returns:
            Dictionary mapping search terms to their result file paths
        """
        # Initialize new collection session
        self.current_session = CollectionSession()
        self.current_session.progress_callback = self.progress_callback
        
        # Start organized data session
        session_info = self.data_organizer.start_session(
            self.current_session.session_id, 
            search_terms
        )
        
        self.logger.info(f"Starting collection session {self.current_session.session_id} with {len(search_terms)} search terms")
        self.logger.info(f"Session directory: {session_info['session_dir']}")
        
        if self.progress_callback:
            self.progress_callback(f"Starting collection session with {len(search_terms)} search terms")
            self.progress_callback(f"Session directory: {session_info['session_dir']}")
        
        results = {}
        
        with sync_playwright() as playwright:
            context = None
            try:
                context = self._setup_browser_context(playwright)
                page = context.pages[0] if context.pages else context.new_page()
                
                # Navigate to homepage and handle initial setup
                self._navigate_to_homepage(page)
                
                for i, search_term in enumerate(search_terms, 1):
                    self.current_session.start_search_term(search_term)
                    self.logger.info(f"Processing search term {i}/{len(search_terms)}: {search_term}")
                    
                    try:
                        file_path = self._collect_single_search_term_with_retry(page, search_term)
                        if file_path:
                            results[search_term] = file_path
                            # Count products in the file to update session
                            product_count = self._count_products_in_file(file_path)
                            self.current_session.complete_search_term(search_term, product_count, file_path)
                            self.logger.info(f"Successfully collected {product_count} products for: {search_term}")
                        else:
                            error_msg = f"No data collected for search term: {search_term}"
                            self.current_session.fail_search_term(search_term, error_msg)
                            self.logger.warning(error_msg)
                            
                    except Exception as e:
                        error_msg = f"Failed to collect data for '{search_term}': {str(e)}"
                        self.current_session.fail_search_term(search_term, error_msg)
                        self.logger.error(error_msg)
                        continue
                        
            except Exception as e:
                error_msg = f"Critical error during collection session: {str(e)}"
                self.current_session.add_error(error_msg)
                self.logger.error(error_msg)
                
            finally:
                if context:
                    context.close()
                
                # End session and log summary
                self.current_session.end_session()
                
                # End organized data session
                session_summary = self.get_collection_summary()
                self.data_organizer.end_session(
                    self.current_session.session_id,
                    {
                        'search_terms_processed': self.current_session.search_terms_processed,
                        'search_terms_failed': self.current_session.search_terms_failed,
                        'total_products_found': self.current_session.total_products_found,
                        'success_rate': self.current_session.get_success_rate(),
                        'duration_seconds': self.current_session.get_duration()
                    }
                )
                
                self._log_session_summary()
                
        return results
    
    def _collect_single_search_term_with_retry(self, page, search_term: str) -> Optional[str]:
        """
        Collect data for a single search term with retry mechanism.
        
        Args:
            page: Playwright page object
            search_term: Search term to process
            
        Returns:
            Path to the saved JSON file, or None if all retries failed
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    self.logger.info(f"Retry attempt {attempt + 1}/{self.max_retries} for search term: {search_term}")
                    if self.progress_callback:
                        self.progress_callback(f"Retrying {search_term} (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                
                return self._collect_single_search_term(page, search_term)
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} failed for '{search_term}': {str(e)}")
                
                # If this is not the last attempt, continue to retry
                if attempt < self.max_retries - 1:
                    continue
                else:
                    # All retries exhausted
                    self.logger.error(f"All {self.max_retries} attempts failed for '{search_term}': {str(last_error)}")
                    raise last_error
        
        return None
    
    def _count_products_in_file(self, file_path: str) -> int:
        """
        Count the number of products in a saved JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Number of products found in the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                products = data.get('products', [])
                return len(products)
        except Exception as e:
            self.logger.warning(f"Could not count products in {file_path}: {str(e)}")
            return 0
    
    def _log_session_summary(self):
        """Log a comprehensive session summary"""
        session = self.current_session
        
        self.logger.info("=" * 60)
        self.logger.info("COLLECTION SESSION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Session ID: {session.session_id}")
        self.logger.info(f"Duration: {session.get_duration():.1f} seconds")
        self.logger.info(f"Success Rate: {session.get_success_rate():.1f}%")
        self.logger.info(f"Search Terms Processed: {len(session.search_terms_processed)}")
        self.logger.info(f"Search Terms Failed: {len(session.search_terms_failed)}")
        self.logger.info(f"Total Products Found: {session.total_products_found}")
        self.logger.info(f"Files Created: {len(session.files_created)}")
        self.logger.info(f"Errors Encountered: {len(session.errors)}")
        
        if session.search_terms_processed:
            self.logger.info(f"Successful Terms: {', '.join(session.search_terms_processed)}")
        
        if session.search_terms_failed:
            self.logger.info(f"Failed Terms: {', '.join(session.search_terms_failed)}")
        
        if session.errors:
            self.logger.info("Errors:")
            for error in session.errors:
                self.logger.info(f"  - {error}")
        
        self.logger.info("=" * 60)
        
        # Also report to progress callback
        if self.progress_callback:
            self.progress_callback(f"Session completed: {len(session.search_terms_processed)} successful, "
                                 f"{len(session.search_terms_failed)} failed, "
                                 f"{session.total_products_found} products collected")
    
    def collect_individual_product(self, product_url: str) -> Dict:
        """
        Collect data for a single product URL with error handling and logging.
        
        Args:
            product_url: Direct URL to a product page
            
        Returns:
            Dictionary containing product data
        """
        self.logger.info(f"Starting individual product collection for: {product_url}")
        
        if self.progress_callback:
            self.progress_callback(f"Collecting individual product: {product_url}")
        
        with sync_playwright() as playwright:
            context = None
            try:
                context = self._setup_browser_context(playwright)
                page = context.pages[0] if context.pages else context.new_page()
                
                product_data = {}
                
                # Set up response handler for API interception
                def handle_response(response):
                    if 'product' in response.url.lower() and response.url.endswith('.json'):
                        try:
                            data = response.json()
                            product_data.update(data)
                            self.logger.debug(f"Intercepted product data from: {response.url}")
                        except json.JSONDecodeError as e:
                            self.logger.warning(f"Failed to decode JSON from {response.url}: {str(e)}")
                
                page.on("response", handle_response)
                
                # Navigate to product page
                self.logger.info(f"Navigating to product page: {product_url}")
                page.goto(product_url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=30000)
                time.sleep(3)
                
                # Save individual product data using organized storage
                if product_data:
                    product_id = self._extract_product_id_from_url(product_url)
                    
                    # Enhance product data with collection metadata
                    enhanced_data = {
                        "product_url": product_url,
                        "product_data": product_data,
                        "collection_metadata": {
                            "user_agent": self.user_agent,
                            "collection_method": "individual_product_collection"
                        }
                    }
                    
                    file_path = self.save_individual_product_organized(product_id, enhanced_data)
                    self.logger.info(f"Successfully collected individual product data using organized storage")
                    
                    if self.progress_callback:
                        self.progress_callback(f"Successfully collected product: {product_id}")
                else:
                    error_msg = f"No product data found for URL: {product_url}"
                    self.logger.warning(error_msg)
                    if self.current_session:
                        self.current_session.add_error(error_msg)
                    
                return product_data
                
            except Exception as e:
                error_msg = f"Error collecting individual product from {product_url}: {str(e)}"
                self.logger.error(error_msg)
                if self.current_session:
                    self.current_session.add_error(error_msg)
                raise
                
            finally:
                if context:
                    context.close()
    
    def save_raw_data(self, data: Dict, filename: str) -> None:
        """
        Save raw data to JSON file with proper formatting.
        
        Args:
            data: Dictionary containing the raw data
            filename: Full path to the output file
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Update session tracking if available
            if self.current_session:
                self.current_session.files_created.append(filename)
            
            self.logger.info(f"Saved data to: {filename}")
            if self.progress_callback:
                self.progress_callback(f"Saved data to: {os.path.basename(filename)}")
            
        except Exception as e:
            error_msg = f"Error saving data to {filename}: {str(e)}"
            
            # Update session tracking if available
            if self.current_session:
                self.current_session.add_error(error_msg)
            
            self.logger.error(error_msg)
            raise  # Re-raise to allow caller to handle
    
    def save_search_results_organized(self, search_term: str, data: Dict) -> str:
        """
        Save search results using the organized data storage system.
        
        Args:
            search_term: The search term used
            data: Raw search result data
            
        Returns:
            Path to the saved file
        """
        try:
            session_id = self.current_session.session_id if self.current_session else None
            file_path = self.data_organizer.save_search_results(search_term, data, session_id)
            
            self.logger.info(f"Saved organized search results for '{search_term}' to {file_path}")
            if self.progress_callback:
                self.progress_callback(f"Saved organized data: {file_path.name}")
            
            return str(file_path)
            
        except Exception as e:
            error_msg = f"Error saving organized search results for '{search_term}': {str(e)}"
            
            if self.current_session:
                self.current_session.add_error(error_msg)
            
            self.logger.error(error_msg)
            raise
    
    def save_individual_product_organized(self, product_id: str, data: Dict) -> str:
        """
        Save individual product data using the organized data storage system.
        
        Args:
            product_id: Unique product identifier
            data: Raw product data
            
        Returns:
            Path to the saved file
        """
        try:
            session_id = self.current_session.session_id if self.current_session else None
            file_path = self.data_organizer.save_individual_product(product_id, data, session_id)
            
            self.logger.info(f"Saved organized individual product {product_id} to {file_path}")
            if self.progress_callback:
                self.progress_callback(f"Saved organized product: {file_path.name}")
            
            return str(file_path)
            
        except Exception as e:
            error_msg = f"Error saving organized individual product {product_id}: {str(e)}"
            
            if self.current_session:
                self.current_session.add_error(error_msg)
            
            self.logger.error(error_msg)
            raise
    
    def get_collection_summary(self) -> CollectionSummary:
        """
        Generate a summary of the collection session.
        
        Returns:
            CollectionSummary object with session details
        """
        if not self.current_session:
            # Return empty summary if no session exists
            return CollectionSummary(
                search_terms_processed=[],
                total_products_found=0,
                files_created=[],
                errors=[],
                collection_time=datetime.now()
            )
        
        session = self.current_session
        return CollectionSummary(
            search_terms_processed=session.search_terms_processed,
            total_products_found=session.total_products_found,
            files_created=session.files_created,
            errors=session.errors,
            collection_time=session.start_time
        )
    
    def get_session_status(self) -> Dict[str, Any]:
        """
        Get detailed session status information.
        
        Returns:
            Dictionary with comprehensive session status
        """
        if not self.current_session:
            return {"status": "no_active_session"}
        
        session = self.current_session
        return {
            "session_id": session.session_id,
            "status": "completed" if session.end_time else "active",
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration_seconds": session.get_duration(),
            "current_search_term": session.current_search_term,
            "search_terms_processed": session.search_terms_processed,
            "search_terms_failed": session.search_terms_failed,
            "total_products_found": session.total_products_found,
            "files_created": session.files_created,
            "error_count": len(session.errors),
            "success_rate": session.get_success_rate()
        }
    
    def get_data_organization_info(self) -> Dict[str, Any]:
        """
        Get information about the data organization structure.
        
        Returns:
            Dictionary with data organization information
        """
        return self.data_organizer.get_directory_structure()
    
    def list_collection_sessions(self, date: str = None) -> List[Dict[str, Any]]:
        """
        List all collection sessions, optionally filtered by date.
        
        Args:
            date: Optional date filter (YYYY-MM-DD format)
            
        Returns:
            List of session information dictionaries
        """
        return self.data_organizer.list_sessions(date)
    
    def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session details dictionary or None if not found
        """
        return self.data_organizer.get_session_info(session_id)
    
    def _setup_browser_context(self, playwright):
        """Set up browser context with anti-detection measures."""
        return playwright.chromium.launch_persistent_context(
            str(self.user_data_dir),
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            user_agent=self.user_agent,
            viewport={'width': 1920, 'height': 1080},
        )
    
    def _navigate_to_homepage(self, page):
        """Navigate to homepage and handle initial setup."""
        print("Navigating to homepage...")
        page.goto(f"{self.base_url}/th", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(2)
        
        # Handle cookie banner if present
        try:
            page.locator("button#btn-accept-cookie").click(timeout=10000)
            print("Cookie banner accepted.")
            time.sleep(1)
        except PlaywrightTimeoutError:
            print("Cookie banner not found or already accepted.")
    
    def _collect_single_search_term(self, page, search_term: str) -> Optional[str]:
        """
        Collect data for a single search term with enhanced error handling.
        
        Args:
            page: Playwright page object
            search_term: Search term to process
            
        Returns:
            Path to the saved JSON file, or None if collection failed
        """
        product_data_found = []
        api_responses_received = 0
        
        # Set up response handler for API interception
        def handle_response(response):
            nonlocal api_responses_received
            # Look for PowerBuy search API endpoints
            if re.search(r'/_next/data/[a-zA-Z0-9_-]+/th/search/.*\.json', response.url):
                try:
                    data = response.json()
                    products = data.get('pageProps', {}).get('productListData', {}).get('products', [])
                    if products:
                        product_data_found.extend(products)
                        api_responses_received += 1
                        self.logger.debug(f"Intercepted {len(products)} products from: {response.url}")
                        if self.progress_callback:
                            self.progress_callback(f"Found {len(products)} products for {search_term}")
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Could not decode JSON from {response.url}: {str(e)}")
                except Exception as e:
                    self.logger.error(f"Error processing response from {response.url}: {str(e)}")
        
        page.on("response", handle_response)
        
        try:
            # Find and use search input
            self.logger.info(f"Looking for search element for term: {search_term}")
            search_element = self._find_search_element(page)
            if not search_element:
                raise Exception("Search input element not found on page")
            
            self.logger.info(f"Performing search for: {search_term}")
            if self.progress_callback:
                self.progress_callback(f"Searching for: {search_term}")
            
            # Clear existing content and enter search term
            search_element.click()
            search_element.fill("")  # Clear existing content
            search_element.fill(search_term)
            search_element.press("Enter")
            
            # Wait for search results page with more flexible URL matching
            expected_url_pattern = f"{self.base_url}/search/"
            try:
                page.wait_for_url(lambda url: expected_url_pattern in url, timeout=60000)
                self.logger.info(f"Navigated to search results: {page.url}")
            except PlaywrightTimeoutError:
                # Try alternative approach - check if we're on a search results page
                current_url = page.url
                if "search" not in current_url.lower():
                    raise Exception(f"Failed to navigate to search results page. Current URL: {current_url}")
                self.logger.warning(f"URL pattern didn't match exactly, but appears to be on search page: {current_url}")
            
            # Wait for API responses with progress updates
            self.logger.info("Waiting for API responses...")
            if self.progress_callback:
                self.progress_callback(f"Loading results for {search_term}...")
            
            page.wait_for_load_state("networkidle", timeout=30000)
            
            # Additional wait with progress updates
            for i in range(5):
                time.sleep(1)
                if self.progress_callback and i % 2 == 0:
                    self.progress_callback(f"Collecting data for {search_term}... ({i+1}/5)")
            
            if product_data_found:
                # Prepare data with metadata
                collection_data = {
                    "search_term": search_term,
                    "total_products": len(product_data_found),
                    "api_responses_received": api_responses_received,
                    "products": product_data_found,
                    "collection_metadata": {
                        "url": page.url,
                        "user_agent": self.user_agent,
                        "collection_method": "API_interception"
                    }
                }
                
                # Save using organized storage system
                file_path = self.save_search_results_organized(search_term, collection_data)
                self.logger.info(f"Successfully saved {len(product_data_found)} products for '{search_term}' using organized storage")
                
                return file_path
            else:
                error_msg = f"No product data found for search term: {search_term}"
                self.logger.warning(error_msg)
                return None
                
        except Exception as e:
            error_msg = f"Error during search for '{search_term}': {str(e)}"
            self.logger.error(error_msg)
            raise  # Re-raise to allow retry mechanism to handle
    
    def _find_search_element(self, page):
        """Find the search input element using multiple selectors."""
        search_selectors = [
            "input[placeholder*='ค้นหา']", 
            "input#txt-search-box",
            "input[placeholder*='search']",
            "input[placeholder*='Search']",
            "[data-testid*='search']",
            ".search-input",
            "input[type='search']",
            "input[name*='search']",
            "input.search-box"
        ]
        
        for selector in search_selectors:
            try:
                search_element = page.locator(selector).first
                if search_element.is_visible(timeout=5000):
                    print(f"Found search element with selector: {selector}")
                    return search_element
            except:
                continue
        
        return None
    
    def _extract_product_id_from_url(self, url: str) -> str:
        """Extract product ID from URL for filename generation."""
        # Try to extract product ID from URL patterns
        patterns = [
            r'/product/(\d+)',
            r'/p/(\d+)',
            r'product-(\d+)',
            r'id=(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Fallback: use timestamp if no ID found
        return datetime.now().strftime("%Y%m%d_%H%M%S")
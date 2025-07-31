"""
PowerBuy Scraper - Core scraping logic extracted from POC.

This module contains the core browser automation logic for scraping PowerBuy.co.th,
extracted and refactored from the original POC implementation. It provides a clean
interface for browser-based data collection with anti-detection measures.
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


class PowerBuyScraperCore:
    """
    Core scraping logic for PowerBuy.co.th extracted from POC implementation.
    
    This class handles the low-level browser automation, API interception,
    and data extraction logic that was proven successful in the POC.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the scraper core with configuration.
        
        Args:
            config: Configuration dictionary containing scraping settings
        """
        self.config = config
        self.base_url = config.get('scraping', {}).get('base_url', 'https://www.powerbuy.co.th')
        self.user_agent = config.get('scraping', {}).get('user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Browser context directory (from POC)
        self.user_data_dir = Path("user_data")
        
        # Timeout settings
        self.page_timeout = config.get('scraping', {}).get('page_timeout', 60000)
        self.network_timeout = config.get('scraping', {}).get('network_timeout', 30000)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def setup_browser_context(self, playwright):
        """
        Set up browser context with anti-detection measures (from POC).
        
        This method implements the exact browser setup that was successful
        in the POC for bypassing Cloudflare protection.
        
        Args:
            playwright: Playwright instance
            
        Returns:
            Browser context with persistent user data
        """
        self.logger.info("Setting up browser context with anti-detection measures")
        
        # Use persistent context to maintain session (key POC success factor)
        context = playwright.chromium.launch_persistent_context(
            str(self.user_data_dir),
            headless=False,  # Keep visible for debugging and human-like behavior
            args=['--disable-blink-features=AutomationControlled'],  # Hide automation flags
            user_agent=self.user_agent,
            viewport={'width': 1920, 'height': 1080},  # Standard desktop resolution
        )
        
        self.logger.info(f"Browser context created with user data dir: {self.user_data_dir}")
        return context
    
    def navigate_to_homepage(self, page):
        """
        Navigate to PowerBuy homepage and handle initial setup (from POC).
        
        This method handles the initial navigation and cookie banner acceptance
        that was proven necessary in the POC.
        
        Args:
            page: Playwright page object
        """
        self.logger.info("Navigating to PowerBuy homepage")
        
        # Navigate to homepage with timeout
        page.goto(f"{self.base_url}/th", timeout=self.page_timeout)
        
        # Wait for page to fully load (critical for dynamic content)
        page.wait_for_load_state("networkidle", timeout=self.network_timeout)
        time.sleep(2)  # Additional buffer for async operations
        
        # Handle cookie banner if present (from POC experience)
        try:
            self.logger.info("Looking for cookie banner")
            page.locator("button#btn-accept-cookie").click(timeout=10000)
            self.logger.info("Cookie banner accepted")
            time.sleep(1)
        except PlaywrightTimeoutError:
            self.logger.info("Cookie banner not found or already accepted")
    
    def find_search_element(self, page):
        """
        Find the search input element using multiple selectors (from POC).
        
        This method implements the robust search element detection
        that was developed during POC testing.
        
        Args:
            page: Playwright page object
            
        Returns:
            Search element locator or None if not found
        """
        self.logger.info("Looking for search input element")
        
        # Multiple selectors from POC testing (in order of preference)
        search_selectors = [
            "input[placeholder*='ค้นหา']",  # Thai placeholder
            "input#txt-search-box",        # Specific ID
            "input[placeholder*='search']", # English placeholder (lowercase)
            "input[placeholder*='Search']", # English placeholder (capitalized)
            "[data-testid*='search']",     # Test ID attribute
            ".search-input",               # CSS class
            "input[type='search']",        # Input type
            "input[name*='search']",       # Name attribute
            "input.search-box"             # Combined class selector
        ]
        
        for selector in search_selectors:
            try:
                self.logger.debug(f"Trying search selector: {selector}")
                search_element = page.locator(selector).first
                
                # Check if element is visible and interactable
                if search_element.is_visible(timeout=5000):
                    self.logger.info(f"Found search element with selector: {selector}")
                    return search_element
                    
            except Exception as e:
                self.logger.debug(f"Selector {selector} failed: {str(e)}")
                continue
        
        self.logger.error("Search input element not found with any known selector")
        return None
    
    def perform_search(self, page, search_term: str):
        """
        Perform search operation with the given term (from POC).
        
        This method implements the exact search procedure that was
        successful in triggering API endpoints in the POC.
        
        Args:
            page: Playwright page object
            search_term: Term to search for
            
        Raises:
            Exception: If search cannot be performed
        """
        self.logger.info(f"Performing search for: {search_term}")
        
        # Find search element
        search_element = self.find_search_element(page)
        if not search_element:
            raise Exception("Cannot perform search: search element not found")
        
        # Clear existing content and enter search term
        search_element.click()
        search_element.fill("")  # Clear any existing content
        search_element.fill(search_term)
        search_element.press("Enter")
        
        self.logger.info(f"Search submitted for: {search_term}")
    
    def wait_for_search_results(self, page, search_term: str):
        """
        Wait for search results page to load (from POC).
        
        This method handles the navigation to search results with
        flexible URL matching that was developed during POC testing.
        
        Args:
            page: Playwright page object
            search_term: The search term used (for logging)
            
        Raises:
            Exception: If search results page doesn't load
        """
        self.logger.info("Waiting for search results page to load")
        
        # Expected URL pattern (flexible matching from POC experience)
        expected_url_pattern = f"{self.base_url}/search/"
        
        try:
            # Wait for URL to change to search results
            page.wait_for_url(lambda url: expected_url_pattern in url, timeout=self.page_timeout)
            self.logger.info(f"Successfully navigated to search results: {page.url}")
            
        except PlaywrightTimeoutError:
            # Fallback: check if we're on a search results page anyway
            current_url = page.url
            if "search" not in current_url.lower():
                raise Exception(f"Failed to navigate to search results page. Current URL: {current_url}")
            
            self.logger.warning(f"URL pattern didn't match exactly, but appears to be on search page: {current_url}")
        
        # Wait for network to be idle (critical for API calls)
        self.logger.info("Waiting for network to be idle")
        page.wait_for_load_state("networkidle", timeout=self.network_timeout)
        
        # Additional wait for async operations (from POC experience)
        time.sleep(5)
    
    def setup_api_interception(self, page, search_term: str) -> List[Dict]:
        """
        Set up API response interception for product data (from POC).
        
        This method implements the exact API interception logic that was
        successful in the POC for capturing structured product data.
        
        Args:
            page: Playwright page object
            search_term: Search term being processed (for URL pattern matching)
            
        Returns:
            List to collect intercepted product data
        """
        self.logger.info(f"Setting up API interception for search term: {search_term}")
        
        product_data_found = []
        api_responses_received = 0
        
        def handle_response(response):
            nonlocal api_responses_received
            
            # PowerBuy API endpoint pattern (discovered in POC)
            api_pattern = r'/_next/data/[a-zA-Z0-9_-]+/th/search/.*\.json'
            
            if re.search(api_pattern, response.url):
                try:
                    self.logger.debug(f"Intercepting API response from: {response.url}")
                    data = response.json()
                    
                    # Extract products from PowerBuy API structure (from POC)
                    products = data.get('pageProps', {}).get('productListData', {}).get('products', [])
                    
                    if products:
                        product_data_found.extend(products)
                        api_responses_received += 1
                        self.logger.info(f"Intercepted {len(products)} products from API response")
                    else:
                        self.logger.debug("API response contained no products")
                        
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Could not decode JSON from {response.url}: {str(e)}")
                except Exception as e:
                    self.logger.error(f"Error processing API response from {response.url}: {str(e)}")
        
        # Attach response handler to page
        page.on("response", handle_response)
        
        self.logger.info("API interception handler attached")
        return product_data_found
    
    def extract_individual_product_data(self, page, product_url: str) -> Dict:
        """
        Extract data from individual product page (from POC individual scraper).
        
        This method implements the product page data extraction logic
        that was successful in the POC individual scraper.
        
        Args:
            page: Playwright page object
            product_url: URL of the product page
            
        Returns:
            Dictionary containing extracted product data
        """
        self.logger.info(f"Extracting individual product data from: {product_url}")
        
        product_data = {}
        
        # Set up response handler for product API calls
        def handle_product_response(response):
            if 'product' in response.url.lower() and response.url.endswith('.json'):
                try:
                    data = response.json()
                    product_data.update(data)
                    self.logger.debug(f"Intercepted product data from: {response.url}")
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to decode product JSON from {response.url}: {str(e)}")
        
        page.on("response", handle_product_response)
        
        # Navigate to product page
        page.goto(product_url, timeout=self.page_timeout)
        page.wait_for_load_state("networkidle", timeout=self.network_timeout)
        time.sleep(3)  # Additional wait for product data loading
        
        # Try to extract from __NEXT_DATA__ script tag (POC fallback method)
        if not product_data:
            try:
                self.logger.info("Attempting to extract data from __NEXT_DATA__ script tag")
                
                # Get page HTML content
                html_content = page.content()
                
                # Look for __NEXT_DATA__ script tag (from POC individual scraper)
                import re
                next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_content, re.DOTALL)
                
                if next_data_match:
                    json_data = json.loads(next_data_match.group(1))
                    product_details = json_data.get('props', {}).get('pageProps', {}).get('pdp', {}).get('data', {})
                    
                    if product_details:
                        product_data = product_details
                        self.logger.info("Successfully extracted product data from __NEXT_DATA__")
                    else:
                        self.logger.warning("__NEXT_DATA__ found but no product data in expected structure")
                else:
                    self.logger.warning("__NEXT_DATA__ script tag not found")
                    
            except Exception as e:
                self.logger.error(f"Error extracting from __NEXT_DATA__: {str(e)}")
        
        return product_data
    
    def extract_product_id_from_url(self, product_url: str) -> str:
        """
        Extract product ID from PowerBuy product URL.
        
        Args:
            product_url: Full product URL
            
        Returns:
            Extracted product ID or timestamp-based fallback
        """
        try:
            # PowerBuy URL pattern: .../product/...-p-{product_id}.html
            match = re.search(r'-p-(\d+)\.html', product_url)
            if match:
                return match.group(1)
            
            # Fallback: use timestamp
            return f"unknown_{int(time.time())}"
            
        except Exception:
            return f"unknown_{int(time.time())}"
    
    def create_enhanced_product_data(self, raw_data: Dict, collection_metadata: Dict = None) -> Dict:
        """
        Create enhanced product data with metadata.
        
        Args:
            raw_data: Raw product data from API or page
            collection_metadata: Additional metadata about collection
            
        Returns:
            Enhanced data dictionary with metadata
        """
        enhanced_data = {
            "raw_product_data": raw_data,
            "collection_timestamp": datetime.now().isoformat(),
            "collection_metadata": collection_metadata or {}
        }
        
        # Add standard metadata
        enhanced_data["collection_metadata"].update({
            "user_agent": self.user_agent,
            "scraper_version": "powerbuy_scraper_v1.0",
            "collection_method": "api_interception"
        })
        
        return enhanced_data
    
    def validate_search_results(self, product_data: List[Dict], search_term: str) -> bool:
        """
        Validate that search results contain expected data structure.
        
        Args:
            product_data: List of product dictionaries
            search_term: Search term used
            
        Returns:
            True if results are valid, False otherwise
        """
        if not product_data:
            self.logger.warning(f"No product data found for search term: {search_term}")
            return False
        
        # Check that products have required fields (from POC structure)
        required_fields = ['name', 'sku', 'price']
        
        valid_products = 0
        for product in product_data:
            if all(field in product for field in required_fields):
                valid_products += 1
        
        if valid_products == 0:
            self.logger.error(f"No valid products found for search term: {search_term}")
            return False
        
        self.logger.info(f"Validation passed: {valid_products}/{len(product_data)} products have required fields")
        return True
    
    def get_scraper_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the scraper performance.
        
        Returns:
            Dictionary with scraper statistics
        """
        return {
            "base_url": self.base_url,
            "user_agent": self.user_agent,
            "user_data_dir": str(self.user_data_dir),
            "page_timeout": self.page_timeout,
            "network_timeout": self.network_timeout,
            "scraper_version": "powerbuy_scraper_v1.0"
        }


class ManualCollector:
    """
    Enhanced ManualCollector class that uses the PowerBuyScraperCore.
    
    This class provides the high-level interface for manual data collection
    while delegating the core scraping logic to PowerBuyScraperCore.
    """
    
    def __init__(self, config: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the ManualCollector with scraper core.
        
        Args:
            config: Configuration dictionary
            progress_callback: Optional callback for progress updates
        """
        self.config = config
        self.progress_callback = progress_callback
        
        # Initialize the core scraper
        self.scraper_core = PowerBuyScraperCore(config)
        
        # Directory setup for organized storage
        self.search_results_dir = Path("raw_data/search_results")
        self.individual_products_dir = Path("raw_data/individual_products")
        self.search_results_dir.mkdir(parents=True, exist_ok=True)
        self.individual_products_dir.mkdir(parents=True, exist_ok=True)
        
        # Session tracking
        self.current_session = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def collect_search_data(self, search_terms: List[str]) -> Dict[str, str]:
        """
        Collect product data for multiple search terms.
        
        Args:
            search_terms: List of search terms to process
            
        Returns:
            Dictionary mapping search terms to their result file paths
        """
        self.logger.info(f"Starting collection for {len(search_terms)} search terms")
        
        if self.progress_callback:
            self.progress_callback(f"Starting collection for {len(search_terms)} search terms")
        
        results = {}
        
        with sync_playwright() as playwright:
            context = None
            try:
                # Setup browser context using core scraper
                context = self.scraper_core.setup_browser_context(playwright)
                page = context.pages[0] if context.pages else context.new_page()
                
                # Navigate to homepage
                self.scraper_core.navigate_to_homepage(page)
                
                # Process each search term
                for i, search_term in enumerate(search_terms, 1):
                    self.logger.info(f"Processing search term {i}/{len(search_terms)}: {search_term}")
                    
                    if self.progress_callback:
                        self.progress_callback(f"Processing {search_term} ({i}/{len(search_terms)})")
                    
                    try:
                        file_path = self._collect_single_search_term(page, search_term)
                        if file_path:
                            results[search_term] = file_path
                            self.logger.info(f"Successfully collected data for: {search_term}")
                        else:
                            self.logger.warning(f"No data collected for: {search_term}")
                            
                    except Exception as e:
                        self.logger.error(f"Failed to collect data for '{search_term}': {str(e)}")
                        continue
                        
            except Exception as e:
                self.logger.error(f"Critical error during collection: {str(e)}")
                
            finally:
                if context:
                    context.close()
        
        self.logger.info(f"Collection completed. Successfully processed {len(results)} out of {len(search_terms)} search terms")
        
        if self.progress_callback:
            self.progress_callback(f"Collection completed: {len(results)}/{len(search_terms)} successful")
        
        return results
    
    def _collect_single_search_term(self, page, search_term: str) -> Optional[str]:
        """
        Collect data for a single search term using the scraper core.
        
        Args:
            page: Playwright page object
            search_term: Search term to process
            
        Returns:
            Path to saved JSON file or None if failed
        """
        try:
            # Setup API interception
            product_data = self.scraper_core.setup_api_interception(page, search_term)
            
            # Perform search
            self.scraper_core.perform_search(page, search_term)
            
            # Wait for results
            self.scraper_core.wait_for_search_results(page, search_term)
            
            # Validate results
            if not self.scraper_core.validate_search_results(product_data, search_term):
                return None
            
            # Save results
            return self._save_search_results(search_term, product_data)
            
        except Exception as e:
            self.logger.error(f"Error collecting data for '{search_term}': {str(e)}")
            raise
    
    def _save_search_results(self, search_term: str, product_data: List[Dict]) -> str:
        """
        Save search results to organized JSON file.
        
        Args:
            search_term: Search term used
            product_data: List of product data dictionaries
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{search_term}_{timestamp}.json"
        file_path = self.search_results_dir / filename
        
        # Create enhanced data with metadata
        enhanced_data = self.scraper_core.create_enhanced_product_data(
            {"products": product_data},
            {
                "search_term": search_term,
                "products_count": len(product_data),
                "collection_method": "search_results"
            }
        )
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved {len(product_data)} products to: {file_path}")
        return str(file_path)
    
    def collect_individual_product(self, product_url: str) -> Dict:
        """
        Collect data for a single product URL.
        
        Args:
            product_url: Direct URL to product page
            
        Returns:
            Dictionary containing product data
        """
        self.logger.info(f"Collecting individual product: {product_url}")
        
        if self.progress_callback:
            self.progress_callback(f"Collecting product: {product_url}")
        
        with sync_playwright() as playwright:
            context = None
            try:
                context = self.scraper_core.setup_browser_context(playwright)
                page = context.pages[0] if context.pages else context.new_page()
                
                # Extract product data using core scraper
                product_data = self.scraper_core.extract_individual_product_data(page, product_url)
                
                if product_data:
                    # Save individual product data
                    product_id = self.scraper_core.extract_product_id_from_url(product_url)
                    self._save_individual_product(product_id, product_data, product_url)
                    
                    self.logger.info(f"Successfully collected individual product: {product_id}")
                    
                    if self.progress_callback:
                        self.progress_callback(f"Successfully collected product: {product_id}")
                
                return product_data
                
            except Exception as e:
                self.logger.error(f"Error collecting individual product: {str(e)}")
                raise
                
            finally:
                if context:
                    context.close()
    
    def _save_individual_product(self, product_id: str, product_data: Dict, product_url: str):
        """
        Save individual product data to organized file.
        
        Args:
            product_id: Product identifier
            product_data: Raw product data
            product_url: Original product URL
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"product_{product_id}_{timestamp}.json"
        file_path = self.individual_products_dir / filename
        
        # Create enhanced data with metadata
        enhanced_data = self.scraper_core.create_enhanced_product_data(
            product_data,
            {
                "product_id": product_id,
                "product_url": product_url,
                "collection_method": "individual_product"
            }
        )
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved individual product data to: {file_path}")
    
    def get_scraper_info(self) -> Dict[str, Any]:
        """
        Get information about the scraper configuration.
        
        Returns:
            Dictionary with scraper information
        """
        return {
            "scraper_core": self.scraper_core.get_scraper_stats(),
            "directories": {
                "search_results": str(self.search_results_dir),
                "individual_products": str(self.individual_products_dir)
            },
            "session_active": self.current_session is not None
        }
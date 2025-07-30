"""
Enhanced Manual Collector for PowerBuy product data collection.

This module refactors the existing POC scraper into a structured ManualCollector class
that supports multiple search terms, organized storage, and metadata tracking.
"""

import os
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from ..validators.models import CollectionSummary


class ManualCollector:
    """
    Enhanced manual collector class for PowerBuy product data collection.
    
    Refactored from the original POC scraper to support:
    - Multiple search terms processing
    - Organized JSON file storage with timestamps
    - Metadata tracking and session management
    - Error handling and recovery
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ManualCollector with configuration.
        
        Args:
            config: Configuration dictionary containing scraping settings
        """
        self.config = config
        self.base_url = config.get('scraping', {}).get('base_url', 'https://www.powerbuy.co.th')
        self.user_agent = config.get('scraping', {}).get('user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Storage directories
        self.search_results_dir = Path(config.get('processing', {}).get('input_directory', 'raw_data/search_results'))
        self.individual_products_dir = Path(config.get('processing', {}).get('individual_products_dir', 'raw_data/individual_products'))
        
        # Create directories if they don't exist
        self.search_results_dir.mkdir(parents=True, exist_ok=True)
        self.individual_products_dir.mkdir(parents=True, exist_ok=True)
        
        # Session tracking
        self.session_start_time = None
        self.collected_data = []
        self.errors = []
        self.files_created = []
        
        # Browser context directory
        self.user_data_dir = Path("user_data")
        
    def collect_search_data(self, search_terms: List[str]) -> Dict[str, str]:
        """
        Collect product data for multiple search terms.
        
        Args:
            search_terms: List of search terms to process
            
        Returns:
            Dictionary mapping search terms to their result file paths
        """
        self.session_start_time = datetime.now()
        results = {}
        
        with sync_playwright() as playwright:
            context = self._setup_browser_context(playwright)
            page = context.pages[0] if context.pages else context.new_page()
            
            try:
                # Navigate to homepage and handle initial setup
                self._navigate_to_homepage(page)
                
                for search_term in search_terms:
                    try:
                        print(f"Processing search term: {search_term}")
                        file_path = self._collect_single_search_term(page, search_term)
                        if file_path:
                            results[search_term] = file_path
                            print(f"Successfully collected data for: {search_term}")
                        else:
                            self.errors.append(f"No data collected for search term: {search_term}")
                            
                    except Exception as e:
                        error_msg = f"Error collecting data for '{search_term}': {str(e)}"
                        self.errors.append(error_msg)
                        print(f"ERROR: {error_msg}")
                        continue
                        
            finally:
                context.close()
                
        return results
    
    def collect_individual_product(self, product_url: str) -> Dict:
        """
        Collect data for a single product URL.
        
        Args:
            product_url: Direct URL to a product page
            
        Returns:
            Dictionary containing product data
        """
        with sync_playwright() as playwright:
            context = self._setup_browser_context(playwright)
            page = context.pages[0] if context.pages else context.new_page()
            
            try:
                product_data = {}
                
                # Set up response handler for API interception
                def handle_response(response):
                    if 'product' in response.url.lower() and response.url.endswith('.json'):
                        try:
                            data = response.json()
                            product_data.update(data)
                        except json.JSONDecodeError:
                            pass
                
                page.on("response", handle_response)
                
                # Navigate to product page
                page.goto(product_url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=30000)
                time.sleep(3)
                
                # Save individual product data
                if product_data:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    product_id = self._extract_product_id_from_url(product_url)
                    filename = f"product_{product_id}_{timestamp}.json"
                    file_path = self.individual_products_dir / filename
                    
                    self.save_raw_data(product_data, str(file_path))
                    
                return product_data
                
            finally:
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
            
            self.files_created.append(filename)
            print(f"Saved data to: {filename}")
            
        except Exception as e:
            error_msg = f"Error saving data to {filename}: {str(e)}"
            self.errors.append(error_msg)
            print(f"ERROR: {error_msg}")
    
    def get_collection_summary(self) -> CollectionSummary:
        """
        Generate a summary of the collection session.
        
        Returns:
            CollectionSummary object with session details
        """
        return CollectionSummary(
            search_terms_processed=[term for term in self.collected_data],
            total_products_found=len(self.collected_data),
            files_created=self.files_created,
            errors=self.errors,
            collection_time=self.session_start_time or datetime.now()
        )
    
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
        Collect data for a single search term.
        
        Args:
            page: Playwright page object
            search_term: Search term to process
            
        Returns:
            Path to the saved JSON file, or None if collection failed
        """
        product_data_found = []
        
        # Set up response handler for API interception
        def handle_response(response):
            # Look for PowerBuy search API endpoints
            if re.search(r'/_next/data/[a-zA-Z0-9_-]+/th/search/.*\.json', response.url):
                try:
                    data = response.json()
                    products = data.get('pageProps', {}).get('productListData', {}).get('products', [])
                    if products:
                        product_data_found.extend(products)
                        print(f"Intercepted {len(products)} products from: {response.url}")
                except json.JSONDecodeError:
                    print(f"Could not decode JSON from: {response.url}")
                except Exception as e:
                    print(f"Error processing response from {response.url}: {e}")
        
        page.on("response", handle_response)
        
        try:
            # Find and use search input
            search_element = self._find_search_element(page)
            if not search_element:
                raise Exception("Search input element not found")
            
            print(f"Searching for: {search_term}")
            search_element.fill(search_term)
            search_element.press("Enter")
            
            # Wait for search results page
            page.wait_for_url(f"{self.base_url}/search/{search_term}", timeout=60000)
            print(f"Navigated to search results: {page.url}")
            
            # Wait for API responses
            page.wait_for_load_state("networkidle", timeout=30000)
            time.sleep(5)  # Additional wait for API responses
            
            if product_data_found:
                # Save collected data with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{search_term.replace(' ', '_')}_{timestamp}.json"
                file_path = self.search_results_dir / filename
                
                # Prepare data with metadata
                collection_data = {
                    "search_term": search_term,
                    "collection_timestamp": timestamp,
                    "total_products": len(product_data_found),
                    "products": product_data_found,
                    "metadata": {
                        "url": page.url,
                        "user_agent": self.user_agent,
                        "collection_method": "API_interception"
                    }
                }
                
                self.save_raw_data(collection_data, str(file_path))
                self.collected_data.append(search_term)
                
                return str(file_path)
            else:
                print(f"No product data found for: {search_term}")
                return None
                
        except Exception as e:
            error_msg = f"Error during search for '{search_term}': {str(e)}"
            self.errors.append(error_msg)
            print(f"ERROR: {error_msg}")
            return None
    
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
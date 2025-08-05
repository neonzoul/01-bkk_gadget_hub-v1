#!/usr/bin/env python3
"""
Manual Collection Runner for PowerBuy Scraper

This script processes all 20 search terms from 20urls.txt using the ManualCollector
to generate organized raw JSON files for each search term.

Task: 10.1 Use enhanced manual collector for all 20 search terms
Requirements: 1.2, 2.1, 2.5
"""

import json
import logging
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Add src to path for imports
sys.path.append('src')

from scrapers.powerbuy_scraper import ManualCollector


def setup_logging():
    """Set up logging configuration for the collection process."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"manual_collection_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def extract_search_terms_from_urls(urls_file: str) -> List[str]:
    """
    Extract search terms from PowerBuy URLs in the 20urls.txt file.
    
    Args:
        urls_file: Path to the file containing URLs
        
    Returns:
        List of decoded search terms
    """
    logger = logging.getLogger(__name__)
    search_terms = []
    
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = f.read().strip().split('\n')
        
        for url in urls:
            url = url.strip()
            if not url or not url.startswith('https://www.powerbuy.co.th/search/'):
                logger.debug(f"Skipping non-PowerBuy search URL: {url}")
                continue
            
            # Extract search term from URL
            # Format: https://www.powerbuy.co.th/search/Samsung%20Galaxy%20S25%20Ultra
            search_part = url.split('/search/')[-1]
            
            # URL decode the search term
            search_term = urllib.parse.unquote(search_part)
            
            # Clean up the search term
            search_term = search_term.strip()
            
            if search_term and search_term not in search_terms:
                search_terms.append(search_term)
                logger.info(f"Extracted search term: {search_term}")
        
        logger.info(f"Total unique search terms extracted: {len(search_terms)}")
        return search_terms
        
    except Exception as e:
        logger.error(f"Error extracting search terms from {urls_file}: {str(e)}")
        raise


def load_config() -> Dict:
    """Load configuration from config.json file."""
    logger = logging.getLogger(__name__)
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info("Configuration loaded successfully")
        return config
        
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise


def progress_callback(message: str):
    """Progress callback function for the ManualCollector."""
    logger = logging.getLogger(__name__)
    logger.info(f"PROGRESS: {message}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


def create_collection_summary(results: Dict[str, str], search_terms: List[str]) -> Dict:
    """
    Create a summary of the collection process.
    
    Args:
        results: Dictionary mapping search terms to result file paths
        search_terms: Original list of search terms
        
    Returns:
        Summary dictionary
    """
    successful_terms = list(results.keys())
    failed_terms = [term for term in search_terms if term not in successful_terms]
    
    summary = {
        "collection_timestamp": datetime.now().isoformat(),
        "total_search_terms": len(search_terms),
        "successful_collections": len(successful_terms),
        "failed_collections": len(failed_terms),
        "success_rate": len(successful_terms) / len(search_terms) * 100,
        "successful_terms": successful_terms,
        "failed_terms": failed_terms,
        "result_files": results
    }
    
    return summary


def save_collection_summary(summary: Dict):
    """Save collection summary to a JSON file."""
    logger = logging.getLogger(__name__)
    
    # Create metadata directory if it doesn't exist
    metadata_dir = Path("raw_data/metadata")
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = metadata_dir / f"collection_summary_{timestamp}.json"
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Collection summary saved to: {summary_file}")
        
    except Exception as e:
        logger.error(f"Error saving collection summary: {str(e)}")


def main():
    """Main function to run the manual collection process."""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting manual collection process for all 20 search terms")
    
    try:
        # Load configuration
        config = load_config()
        
        # Extract search terms from URLs file
        search_terms = extract_search_terms_from_urls('20urls.txt')
        
        if not search_terms:
            logger.error("No valid search terms found in 20urls.txt")
            return 1
        
        logger.info(f"Found {len(search_terms)} search terms to process:")
        for i, term in enumerate(search_terms, 1):
            logger.info(f"  {i}. {term}")
        
        # Initialize ManualCollector
        logger.info("Initializing ManualCollector...")
        collector = ManualCollector(config, progress_callback=progress_callback)
        
        # Display scraper information
        scraper_info = collector.get_scraper_info()
        logger.info(f"Scraper configuration: {scraper_info}")
        
        # Start collection process
        logger.info("Starting data collection process...")
        print(f"\n{'='*60}")
        print(f"STARTING MANUAL COLLECTION FOR {len(search_terms)} SEARCH TERMS")
        print(f"{'='*60}\n")
        
        results = collector.collect_search_data(search_terms)
        
        # Create and save collection summary
        summary = create_collection_summary(results, search_terms)
        save_collection_summary(summary)
        
        # Display results
        print(f"\n{'='*60}")
        print("COLLECTION COMPLETED")
        print(f"{'='*60}")
        print(f"Total search terms: {summary['total_search_terms']}")
        print(f"Successful collections: {summary['successful_collections']}")
        print(f"Failed collections: {summary['failed_collections']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        
        if summary['successful_collections'] > 0:
            print(f"\nSuccessful collections:")
            for term in summary['successful_terms']:
                print(f"  ✓ {term}")
        
        if summary['failed_collections'] > 0:
            print(f"\nFailed collections:")
            for term in summary['failed_terms']:
                print(f"  ✗ {term}")
        
        print(f"\nResult files saved in: raw_data/search_results/")
        print(f"Collection summary saved in: raw_data/metadata/")
        
        logger.info("Manual collection process completed successfully")
        
        # Return appropriate exit code
        return 0 if summary['successful_collections'] > 0 else 1
        
    except Exception as e:
        logger.error(f"Critical error in manual collection process: {str(e)}")
        print(f"\nERROR: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
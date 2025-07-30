"""
Configuration loader utility for the PowerBuy scraper.
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration settings
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config


def load_search_terms_from_urls(urls_file: str = "20urls.txt") -> List[str]:
    """
    Extract search terms from URLs file.
    
    Args:
        urls_file: Path to the file containing URLs
        
    Returns:
        List of search terms extracted from URLs
    """
    search_terms = []
    
    if not os.path.exists(urls_file):
        print(f"Warning: URLs file not found: {urls_file}")
        return search_terms
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and line.startswith('https://www.powerbuy.co.th/search/'):
                # Extract search term from URL
                search_term = line.split('/search/')[-1]
                # URL decode the search term
                search_term = search_term.replace('%20', ' ').replace('%25', '%')
                search_terms.append(search_term)
    
    return search_terms


def get_search_terms(config: Dict[str, Any], urls_file: str = "20urls.txt") -> List[str]:
    """
    Get search terms from configuration or URLs file.
    
    Args:
        config: Configuration dictionary
        urls_file: Path to URLs file as fallback
        
    Returns:
        List of search terms to process
    """
    # First try to get search terms from config
    search_terms = config.get('search_terms', [])
    
    # If no search terms in config, try to load from URLs file
    if not search_terms:
        search_terms = load_search_terms_from_urls(urls_file)
    
    # If still no search terms, use default
    if not search_terms:
        search_terms = [
            "iPhone 15",
            "Samsung Galaxy S24",
            "iPad Pro",
            "MacBook Air",
            "AirPods Pro"
        ]
        print("Warning: No search terms found, using default terms")
    
    return search_terms
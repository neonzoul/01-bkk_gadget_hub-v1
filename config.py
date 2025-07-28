"""
Configuration management for PowerBuy scraper implementation.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ScrapingConfig:
    """Configuration for scraping operations"""
    base_url: str = "https://www.powerbuy.co.th"
    search_delay_min: float = 2.0
    search_delay_max: float = 5.0
    request_timeout: int = 30
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class ProcessingConfig:
    """Configuration for data processing"""
    input_directory: str = "raw_data/search_results"
    individual_products_dir: str = "raw_data/individual_products"
    processed_directory: str = "raw_data/processed"
    output_directory: str = "output"
    csv_encoding: str = "utf-8"
    date_format: str = "%Y-%m-%d"
    
    
@dataclass
class SystemConfig:
    """System-wide configuration"""
    log_level: str = "INFO"
    log_file: str = "logs/scraper.log"
    data_retention_days: int = 30
    enable_debug: bool = False


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.search_terms: List[str] = []
        self.scraping = ScrapingConfig()
        self.processing = ProcessingConfig()
        self.system = SystemConfig()
        
        # Load configuration if file exists
        self.load_config()
        
        # Load search terms from 20urls.txt if available
        self.load_search_terms()
    
    def load_config(self) -> None:
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update configurations with loaded data
                if 'scraping' in config_data:
                    self.scraping = ScrapingConfig(**config_data['scraping'])
                if 'processing' in config_data:
                    self.processing = ProcessingConfig(**config_data['processing'])
                if 'system' in config_data:
                    self.system = SystemConfig(**config_data['system'])
                if 'search_terms' in config_data:
                    self.search_terms = config_data['search_terms']
                    
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                print("Using default configuration")
    
    def save_config(self) -> None:
        """Save current configuration to JSON file"""
        config_data = {
            'scraping': asdict(self.scraping),
            'processing': asdict(self.processing),
            'system': asdict(self.system),
            'search_terms': self.search_terms
        }
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_file) if os.path.dirname(self.config_file) else '.', exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def load_search_terms(self) -> None:
        """Load search terms from 20urls.txt file"""
        urls_file = "20urls.txt"
        if os.path.exists(urls_file):
            try:
                with open(urls_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Extract search terms from URLs or use as direct search terms
                search_terms = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # If it's a URL, extract search term; otherwise use as-is
                        if 'search=' in line:
                            # Extract search term from URL parameter
                            search_term = line.split('search=')[1].split('&')[0]
                            search_terms.append(search_term.replace('%20', ' ').replace('+', ' '))
                        elif line.startswith('http'):
                            # Skip URLs that don't contain search terms
                            continue
                        else:
                            # Use line as direct search term
                            search_terms.append(line)
                
                if search_terms:
                    self.search_terms = search_terms
                    
            except Exception as e:
                print(f"Warning: Could not load search terms from {urls_file}: {e}")
        
        # Fallback search terms if none loaded
        if not self.search_terms:
            self.search_terms = [
                "iPhone 15",
                "Samsung Galaxy S24",
                "iPad Pro",
                "MacBook Air",
                "AirPods Pro"
            ]
    
    def get_search_terms(self) -> List[str]:
        """Get list of search terms"""
        return self.search_terms
    
    def add_search_term(self, term: str) -> None:
        """Add a new search term"""
        if term not in self.search_terms:
            self.search_terms.append(term)
    
    def remove_search_term(self, term: str) -> None:
        """Remove a search term"""
        if term in self.search_terms:
            self.search_terms.remove(term)
    
    def get_output_filename(self, date_str: str = None) -> str:
        """Generate output filename with date"""
        if date_str is None:
            from datetime import datetime
            date_str = datetime.now().strftime(self.processing.date_format)
        
        return f"competitor_prices_{date_str}.csv"
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        directories = [
            self.processing.input_directory,
            self.processing.individual_products_dir,
            self.processing.processed_directory,
            self.processing.output_directory,
            os.path.dirname(self.system.log_file) if os.path.dirname(self.system.log_file) else 'logs'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Global configuration instance
config = ConfigManager()
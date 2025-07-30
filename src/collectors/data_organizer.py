"""
Data Organization Manager for PowerBuy scraper.

This module provides comprehensive data organization and storage management
for the PowerBuy scraper system, including directory structure management,
file naming conventions, and metadata tracking.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging


class DataOrganizer:
    """
    Manages data organization and storage for the PowerBuy scraper system.
    
    Provides:
    - Organized directory structure creation and management
    - Standardized file naming conventions
    - Comprehensive metadata tracking
    - Session-based data organization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DataOrganizer with configuration.
        
        Args:
            config: Configuration dictionary containing storage settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Base directories
        self.base_data_dir = Path(config.get('processing', {}).get('base_data_dir', 'raw_data'))
        
        # Organized directory structure
        self.search_results_dir = self.base_data_dir / 'search_results'
        self.individual_products_dir = self.base_data_dir / 'individual_products'
        self.sessions_dir = self.base_data_dir / 'sessions'
        self.metadata_dir = self.base_data_dir / 'metadata'
        self.processed_dir = self.base_data_dir / 'processed'
        
        # Create all directories
        self._create_directory_structure()
        
        # Session tracking
        self.current_session_id = None
        self.session_metadata = {}
        
    def _create_directory_structure(self):
        """Create the complete directory structure for data organization."""
        directories = [
            self.search_results_dir,
            self.individual_products_dir,
            self.sessions_dir,
            self.metadata_dir,
            self.processed_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created/verified directory: {directory}")
            
        # Create subdirectories for better organization
        self._create_subdirectories()
    
    def _create_subdirectories(self):
        """Create subdirectories for better data organization."""
        # Search results subdirectories by date
        today = datetime.now().strftime("%Y-%m-%d")
        (self.search_results_dir / today).mkdir(exist_ok=True)
        
        # Individual products subdirectories
        (self.individual_products_dir / today).mkdir(exist_ok=True)
        
        # Session subdirectories
        (self.sessions_dir / today).mkdir(exist_ok=True)
        
        self.logger.info(f"Created date-based subdirectories for {today}")
    
    def start_session(self, session_id: str, search_terms: List[str]) -> Dict[str, Any]:
        """
        Start a new collection session with organized storage.
        
        Args:
            session_id: Unique session identifier
            search_terms: List of search terms for this session
            
        Returns:
            Dictionary containing session metadata and storage paths
        """
        self.current_session_id = session_id
        
        # Create session-specific directory
        session_dir = self.sessions_dir / datetime.now().strftime("%Y-%m-%d") / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize session metadata
        self.session_metadata = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'search_terms': search_terms,
            'session_dir': str(session_dir),
            'files_created': [],
            'products_collected': 0,
            'errors': [],
            'status': 'active'
        }
        
        # Save initial session metadata
        metadata_file = self.metadata_dir / f"session_{session_id}.json"
        self._save_metadata(metadata_file, self.session_metadata)
        
        self.logger.info(f"Started session {session_id} with {len(search_terms)} search terms")
        
        return {
            'session_id': session_id,
            'session_dir': session_dir,
            'search_results_dir': self.search_results_dir / datetime.now().strftime("%Y-%m-%d"),
            'individual_products_dir': self.individual_products_dir / datetime.now().strftime("%Y-%m-%d"),
            'metadata_file': metadata_file
        }
    
    def generate_search_result_filename(self, search_term: str, session_id: str = None) -> Path:
        """
        Generate a standardized filename for search results.
        
        Args:
            search_term: The search term used
            session_id: Optional session ID for organization
            
        Returns:
            Path object for the search result file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Clean search term for filename
        clean_term = self._clean_filename(search_term)
        
        # Generate filename with session context
        if session_id:
            filename = f"{clean_term}_{session_id}_{timestamp}.json"
        else:
            filename = f"{clean_term}_{timestamp}.json"
        
        # Place in date-organized directory
        date_dir = self.search_results_dir / datetime.now().strftime("%Y-%m-%d")
        date_dir.mkdir(exist_ok=True)
        
        return date_dir / filename
    
    def generate_individual_product_filename(self, product_id: str, session_id: str = None) -> Path:
        """
        Generate a standardized filename for individual product data.
        
        Args:
            product_id: Unique product identifier
            session_id: Optional session ID for organization
            
        Returns:
            Path object for the individual product file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Generate filename with session context
        if session_id:
            filename = f"product_{product_id}_{session_id}_{timestamp}.json"
        else:
            filename = f"product_{product_id}_{timestamp}.json"
        
        # Place in date-organized directory
        date_dir = self.individual_products_dir / datetime.now().strftime("%Y-%m-%d")
        date_dir.mkdir(exist_ok=True)
        
        return date_dir / filename
    
    def save_search_results(self, search_term: str, data: Dict[str, Any], 
                          session_id: str = None) -> Path:
        """
        Save search results with proper organization and metadata.
        
        Args:
            search_term: The search term used
            data: Raw search result data
            session_id: Optional session ID
            
        Returns:
            Path to the saved file
        """
        file_path = self.generate_search_result_filename(search_term, session_id)
        
        # Enhance data with metadata
        enhanced_data = {
            'search_term': search_term,
            'collection_timestamp': datetime.now().isoformat(),
            'session_id': session_id or 'standalone',
            'total_products': len(data.get('products', [])),
            'file_path': str(file_path),
            'data': data,
            'metadata': {
                'collection_method': 'manual_collector',
                'data_source': 'powerbuy.co.th',
                'file_format': 'json',
                'encoding': 'utf-8'
            }
        }
        
        # Save the enhanced data
        self._save_json_file(file_path, enhanced_data)
        
        # Update session metadata if applicable
        if session_id and session_id == self.current_session_id:
            self.session_metadata['files_created'].append(str(file_path))
            self.session_metadata['products_collected'] += enhanced_data['total_products']
            self._update_session_metadata()
        
        self.logger.info(f"Saved search results for '{search_term}' to {file_path}")
        return file_path
    
    def save_individual_product(self, product_id: str, data: Dict[str, Any], 
                              session_id: str = None) -> Path:
        """
        Save individual product data with proper organization and metadata.
        
        Args:
            product_id: Unique product identifier
            data: Raw product data
            session_id: Optional session ID
            
        Returns:
            Path to the saved file
        """
        file_path = self.generate_individual_product_filename(product_id, session_id)
        
        # Enhance data with metadata
        enhanced_data = {
            'product_id': product_id,
            'collection_timestamp': datetime.now().isoformat(),
            'session_id': session_id or 'standalone',
            'file_path': str(file_path),
            'data': data,
            'metadata': {
                'collection_method': 'manual_collector',
                'data_source': 'powerbuy.co.th',
                'file_format': 'json',
                'encoding': 'utf-8'
            }
        }
        
        # Save the enhanced data
        self._save_json_file(file_path, enhanced_data)
        
        # Update session metadata if applicable
        if session_id and session_id == self.current_session_id:
            self.session_metadata['files_created'].append(str(file_path))
            self.session_metadata['products_collected'] += 1
            self._update_session_metadata()
        
        self.logger.info(f"Saved individual product {product_id} to {file_path}")
        return file_path
    
    def end_session(self, session_id: str, summary: Dict[str, Any] = None):
        """
        End a collection session and finalize metadata.
        
        Args:
            session_id: Session identifier to end
            summary: Optional session summary data
        """
        if session_id == self.current_session_id:
            self.session_metadata['end_time'] = datetime.now().isoformat()
            self.session_metadata['status'] = 'completed'
            
            if summary:
                self.session_metadata['summary'] = summary
            
            # Calculate session statistics
            start_time = datetime.fromisoformat(self.session_metadata['start_time'])
            end_time = datetime.fromisoformat(self.session_metadata['end_time'])
            duration = (end_time - start_time).total_seconds()
            
            self.session_metadata['duration_seconds'] = duration
            self.session_metadata['files_count'] = len(self.session_metadata['files_created'])
            
            # Final metadata save
            self._update_session_metadata()
            
            self.logger.info(f"Ended session {session_id} - Duration: {duration:.1f}s, "
                           f"Files: {self.session_metadata['files_count']}, "
                           f"Products: {self.session_metadata['products_collected']}")
            
            # Reset current session
            self.current_session_id = None
            self.session_metadata = {}
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session metadata dictionary or None if not found
        """
        metadata_file = self.metadata_dir / f"session_{session_id}.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error reading session metadata for {session_id}: {e}")
                return None
        
        return None
    
    def list_sessions(self, date: str = None) -> List[Dict[str, Any]]:
        """
        List all sessions, optionally filtered by date.
        
        Args:
            date: Optional date filter (YYYY-MM-DD format)
            
        Returns:
            List of session metadata dictionaries
        """
        sessions = []
        
        # Get all session metadata files
        for metadata_file in self.metadata_dir.glob("session_*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    
                    # Apply date filter if specified
                    if date:
                        session_date = session_data.get('start_time', '')[:10]  # Extract YYYY-MM-DD
                        if session_date != date:
                            continue
                    
                    sessions.append(session_data)
                    
            except Exception as e:
                self.logger.error(f"Error reading session metadata from {metadata_file}: {e}")
        
        # Sort by start time (newest first)
        sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        return sessions
    
    def get_directory_structure(self) -> Dict[str, Any]:
        """
        Get information about the current directory structure.
        
        Returns:
            Dictionary containing directory structure information
        """
        structure = {
            'base_data_dir': str(self.base_data_dir),
            'directories': {
                'search_results': str(self.search_results_dir),
                'individual_products': str(self.individual_products_dir),
                'sessions': str(self.sessions_dir),
                'metadata': str(self.metadata_dir),
                'processed': str(self.processed_dir)
            },
            'statistics': {}
        }
        
        # Add statistics for each directory
        for name, path in structure['directories'].items():
            dir_path = Path(path)
            if dir_path.exists():
                files = list(dir_path.rglob('*.json'))
                structure['statistics'][name] = {
                    'total_files': len(files),
                    'total_size_mb': sum(f.stat().st_size for f in files) / (1024 * 1024)
                }
            else:
                structure['statistics'][name] = {'total_files': 0, 'total_size_mb': 0}
        
        return structure
    
    def _clean_filename(self, filename: str) -> str:
        """
        Clean a string to be safe for use as a filename.
        
        Args:
            filename: Raw filename string
            
        Returns:
            Cleaned filename string
        """
        # Replace problematic characters
        cleaned = filename.replace(' ', '_')
        cleaned = cleaned.replace('/', '_')
        cleaned = cleaned.replace('\\', '_')
        cleaned = cleaned.replace(':', '_')
        cleaned = cleaned.replace('*', '_')
        cleaned = cleaned.replace('?', '_')
        cleaned = cleaned.replace('"', '_')
        cleaned = cleaned.replace('<', '_')
        cleaned = cleaned.replace('>', '_')
        cleaned = cleaned.replace('|', '_')
        
        # Remove multiple underscores
        while '__' in cleaned:
            cleaned = cleaned.replace('__', '_')
        
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        
        # Limit length
        if len(cleaned) > 50:
            cleaned = cleaned[:50]
        
        return cleaned or 'unnamed'
    
    def _save_json_file(self, file_path: Path, data: Dict[str, Any]):
        """
        Save data to a JSON file with proper formatting.
        
        Args:
            file_path: Path to save the file
            data: Data to save
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving JSON file {file_path}: {e}")
            raise
    
    def _save_metadata(self, file_path: Path, metadata: Dict[str, Any]):
        """
        Save metadata to a file.
        
        Args:
            file_path: Path to save the metadata
            metadata: Metadata dictionary
        """
        self._save_json_file(file_path, metadata)
    
    def _update_session_metadata(self):
        """Update the current session metadata file."""
        if self.current_session_id:
            metadata_file = self.metadata_dir / f"session_{self.current_session_id}.json"
            self._save_metadata(metadata_file, self.session_metadata)
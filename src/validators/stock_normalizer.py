"""
Enhanced stock status normalization for PowerBuy products.

This module provides comprehensive stock status normalization with
extensive Thai language support and flexible pattern matching.
"""

import re
import logging
from typing import Dict, List, Optional


class StockStatusNormalizer:
    """
    Enhanced stock status normalizer with comprehensive Thai language support.
    
    Provides advanced normalization for PowerBuy stock status values,
    supporting both Thai and English variations with flexible pattern matching.
    """
    
    def __init__(self):
        """Initialize the normalizer with comprehensive status mappings."""
        self.logger = logging.getLogger(__name__)
        
        # Comprehensive mapping of stock status variations
        self.in_stock_patterns = [
            # English variations
            'in stock', 'available', 'in-stock', 'instock',
            'yes', 'true', '1', 'ready', 'ready to ship',
            'on hand', 'stocked', 'inventory available',
            
            # Thai variations
            'มีสินค้า', 'พร้อมส่ง', 'มีของ', 'มีสต็อก',
            'พร้อมจัดส่ง', 'มีในสต็อก', 'สินค้าพร้อม',
            'พร้อมขาย', 'มีจำหน่าย', 'สินค้ามี',
            
            # Mixed and alternative formats
            'available now', 'ready now', 'พร้อมทันที',
            'มีสินค้าพร้อมส่ง', 'สินค้าพร้อมจัดส่ง'
        ]
        
        self.out_of_stock_patterns = [
            # English variations
            'out of stock', 'unavailable', 'out-of-stock', 'outofstock',
            'no', 'false', '0', 'sold out', 'not available',
            'no stock', 'empty', 'depleted', 'exhausted',
            
            # Thai variations
            'หมด', 'สินค้าหมด', 'ไม่มีสินค้า', 'ไม่มีของ',
            'ไม่มีสต็อก', 'สต็อกหมด', 'ขายหมด',
            'ไม่พร้อมส่ง', 'ไม่มีในสต็อก', 'สินค้าไม่พร้อม',
            
            # Mixed and alternative formats
            'temporarily unavailable', 'ชั่วคราวหมด',
            'สินค้าหมดชั่วคราว', 'ไม่มีสินค้าในขณะนี้'
        ]
        
        # Statistics tracking
        self.normalization_stats = {
            'total_normalized': 0,
            'in_stock_normalized': 0,
            'out_of_stock_normalized': 0,
            'unknown_status': 0,
            'pattern_matches': {}
        }
    
    def normalize_stock_status(self, status: Optional[str]) -> str:
        """
        Normalize stock status to standard values with comprehensive pattern matching.
        
        Args:
            status: Raw stock status string
            
        Returns:
            Normalized stock status: 'In Stock', 'Out of Stock', or 'Unknown'
        """
        if not status:
            self.normalization_stats['unknown_status'] += 1
            return 'Unknown'
        
        self.normalization_stats['total_normalized'] += 1
        
        # Clean and prepare status for matching
        cleaned_status = self._clean_status_string(status)
        
        # Check for out of stock patterns first (more specific)
        if self._matches_patterns(cleaned_status, self.out_of_stock_patterns):
            self.normalization_stats['out_of_stock_normalized'] += 1
            self._track_pattern_match(status, 'Out of Stock')
            return 'Out of Stock'
        
        # Check for in stock patterns
        if self._matches_patterns(cleaned_status, self.in_stock_patterns):
            self.normalization_stats['in_stock_normalized'] += 1
            self._track_pattern_match(status, 'In Stock')
            return 'In Stock'
        
        # No pattern matched
        self.normalization_stats['unknown_status'] += 1
        self.logger.debug(f"Unknown stock status pattern: '{status}'")
        return 'Unknown'
    
    def _clean_status_string(self, status: str) -> str:
        """
        Clean status string for pattern matching.
        
        Args:
            status: Raw status string
            
        Returns:
            Cleaned status string
        """
        # Convert to lowercase for case-insensitive matching
        cleaned = status.lower().strip()
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove common punctuation that might interfere
        cleaned = re.sub(r'[.,!?;:]', '', cleaned)
        
        return cleaned
    
    def _matches_patterns(self, status: str, patterns: List[str]) -> bool:
        """
        Check if status matches any of the given patterns.
        
        Args:
            status: Cleaned status string
            patterns: List of patterns to match against
            
        Returns:
            True if any pattern matches
        """
        for pattern in patterns:
            pattern_lower = pattern.lower()
            
            # Exact match
            if status == pattern_lower:
                return True
            
            # Substring match for longer descriptions
            if pattern_lower in status:
                return True
            
            # For English words, try word boundary match
            if re.match(r'^[a-zA-Z\s]+$', pattern):
                if re.search(rf'\b{re.escape(pattern_lower)}\b', status):
                    return True
        
        return False
    
    def _track_pattern_match(self, original_status: str, normalized_status: str):
        """Track pattern matches for analysis."""
        if original_status not in self.normalization_stats['pattern_matches']:
            self.normalization_stats['pattern_matches'][original_status] = normalized_status
    
    def add_custom_patterns(self, in_stock_patterns: List[str] = None, 
                           out_of_stock_patterns: List[str] = None):
        """
        Add custom patterns for stock status normalization.
        
        Args:
            in_stock_patterns: Additional patterns for in stock status
            out_of_stock_patterns: Additional patterns for out of stock status
        """
        if in_stock_patterns:
            self.in_stock_patterns.extend(in_stock_patterns)
            self.logger.info(f"Added {len(in_stock_patterns)} custom in-stock patterns")
        
        if out_of_stock_patterns:
            self.out_of_stock_patterns.extend(out_of_stock_patterns)
            self.logger.info(f"Added {len(out_of_stock_patterns)} custom out-of-stock patterns")
    
    def get_normalization_stats(self) -> Dict[str, any]:
        """
        Get normalization statistics.
        
        Returns:
            Dictionary with normalization statistics
        """
        return {
            'total_normalized': self.normalization_stats['total_normalized'],
            'in_stock_normalized': self.normalization_stats['in_stock_normalized'],
            'out_of_stock_normalized': self.normalization_stats['out_of_stock_normalized'],
            'unknown_status': self.normalization_stats['unknown_status'],
            'pattern_matches': dict(self.normalization_stats['pattern_matches']),
            'success_rate': (
                (self.normalization_stats['in_stock_normalized'] + 
                 self.normalization_stats['out_of_stock_normalized']) /
                max(self.normalization_stats['total_normalized'], 1)
            ) * 100
        }
    
    def reset_stats(self):
        """Reset normalization statistics."""
        self.normalization_stats = {
            'total_normalized': 0,
            'in_stock_normalized': 0,
            'out_of_stock_normalized': 0,
            'unknown_status': 0,
            'pattern_matches': {}
        }
    
    def get_supported_patterns(self) -> Dict[str, List[str]]:
        """
        Get all supported patterns for documentation.
        
        Returns:
            Dictionary with in_stock and out_of_stock patterns
        """
        return {
            'in_stock_patterns': self.in_stock_patterns.copy(),
            'out_of_stock_patterns': self.out_of_stock_patterns.copy()
        }
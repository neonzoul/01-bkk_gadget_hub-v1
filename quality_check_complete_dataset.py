#!/usr/bin/env python3
"""
Quality Check Script for Complete PowerBuy Dataset
Validates all extracted data for consistency, completeness, and data quality issues.
"""

import pandas as pd
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/quality_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatasetQualityChecker:
    """Comprehensive quality checker for the complete PowerBuy dataset"""
    
    def __init__(self, csv_file: str, processing_summary_file: str):
        self.csv_file = csv_file
        self.processing_summary_file = processing_summary_file
        self.quality_issues = []
        self.validation_results = {}
        
    def load_data(self) -> Tuple[pd.DataFrame, Dict]:
        """Load CSV data and processing summary"""
        logger.info(f"Loading dataset from {self.csv_file}")
        
        # Load CSV data
        try:
            df = pd.read_csv(self.csv_file, encoding='utf-8')
            logger.info(f"Successfully loaded {len(df)} records from CSV")
        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            raise
            
        # Load processing summary
        try:
            with open(self.processing_summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            logger.info("Successfully loaded processing summary")
        except Exception as e:
            logger.error(f"Failed to load processing summary: {e}")
            raise
            
        return df, summary
    
    def validate_data_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for missing values and data completeness"""
        logger.info("Validating data completeness...")
        
        completeness_results = {
            'total_records': len(df),
            'missing_values': {},
            'empty_strings': {},
            'null_percentages': {}
        }
        
        # Check for missing values in each column
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            empty_string_count = (df[column] == '').sum() if df[column].dtype == 'object' else 0
            
            completeness_results['missing_values'][column] = missing_count
            completeness_results['empty_strings'][column] = empty_string_count
            completeness_results['null_percentages'][column] = round((missing_count / len(df)) * 100, 2)
            
            if missing_count > 0:
                self.quality_issues.append(f"Column '{column}' has {missing_count} missing values ({completeness_results['null_percentages'][column]}%)")
            
            if empty_string_count > 0:
                self.quality_issues.append(f"Column '{column}' has {empty_string_count} empty strings")
        
        return completeness_results
    
    def validate_data_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for data consistency issues"""
        logger.info("Validating data consistency...")
        
        consistency_results = {
            'price_validation': {},
            'sku_validation': {},
            'stock_status_validation': {},
            'name_validation': {}
        }
        
        # Price validation
        if 'Price' in df.columns:
            try:
                # Convert price to numeric for validation
                df['Price_Numeric'] = pd.to_numeric(df['Price'], errors='coerce')
                
                negative_prices = (df['Price_Numeric'] < 0).sum()
                zero_prices = (df['Price_Numeric'] == 0).sum()
                invalid_prices = df['Price_Numeric'].isnull().sum()
                
                consistency_results['price_validation'] = {
                    'negative_prices': negative_prices,
                    'zero_prices': zero_prices,
                    'invalid_prices': invalid_prices,
                    'min_price': df['Price_Numeric'].min(),
                    'max_price': df['Price_Numeric'].max(),
                    'avg_price': round(df['Price_Numeric'].mean(), 2)
                }
                
                if negative_prices > 0:
                    self.quality_issues.append(f"Found {negative_prices} products with negative prices")
                if zero_prices > 0:
                    self.quality_issues.append(f"Found {zero_prices} products with zero prices")
                if invalid_prices > 0:
                    self.quality_issues.append(f"Found {invalid_prices} products with invalid price formats")
                    
            except Exception as e:
                logger.error(f"Price validation failed: {e}")
                self.quality_issues.append(f"Price validation failed: {e}")
        
        # SKU validation
        if 'SKU' in df.columns:
            duplicate_skus = df['SKU'].duplicated().sum()
            empty_skus = (df['SKU'] == '').sum()
            
            consistency_results['sku_validation'] = {
                'duplicate_skus': duplicate_skus,
                'empty_skus': empty_skus,
                'unique_skus': df['SKU'].nunique(),
                'total_skus': len(df)
            }
            
            if duplicate_skus > 0:
                self.quality_issues.append(f"Found {duplicate_skus} duplicate SKUs")
            if empty_skus > 0:
                self.quality_issues.append(f"Found {empty_skus} empty SKUs")
        
        # Stock status validation
        if 'Stock Status' in df.columns:
            stock_values = df['Stock Status'].value_counts()
            invalid_stock = df[~df['Stock Status'].isin(['In Stock', 'Out of Stock'])]['Stock Status'].value_counts()
            
            consistency_results['stock_status_validation'] = {
                'stock_distribution': stock_values.to_dict(),
                'invalid_stock_values': invalid_stock.to_dict() if len(invalid_stock) > 0 else {}
            }
            
            if len(invalid_stock) > 0:
                self.quality_issues.append(f"Found {len(invalid_stock)} products with invalid stock status values")
        
        # Name validation
        if 'Name' in df.columns:
            empty_names = (df['Name'] == '').sum()
            duplicate_names = df['Name'].duplicated().sum()
            
            consistency_results['name_validation'] = {
                'empty_names': empty_names,
                'duplicate_names': duplicate_names,
                'unique_names': df['Name'].nunique(),
                'avg_name_length': round(df['Name'].str.len().mean(), 2)
            }
            
            if empty_names > 0:
                self.quality_issues.append(f"Found {empty_names} products with empty names")
        
        return consistency_results
    
    def validate_encoding_and_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for encoding issues and format problems"""
        logger.info("Validating encoding and format...")
        
        format_results = {
            'encoding_issues': [],
            'thai_character_support': False,
            'special_characters': {}
        }
        
        # Check for Thai character support
        thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
        thai_products = 0
        
        for column in df.select_dtypes(include=['object']).columns:
            for value in df[column].dropna():
                if thai_pattern.search(str(value)):
                    thai_products += 1
                    format_results['thai_character_support'] = True
                    break
        
        if thai_products > 0:
            logger.info(f"Found Thai characters in {thai_products} records - UTF-8 encoding working correctly")
        
        # Check for special characters that might cause issues
        special_chars = ['�', '\x00', '\ufffd']  # Common encoding error characters
        for char in special_chars:
            char_count = 0
            for column in df.select_dtypes(include=['object']).columns:
                char_count += df[column].astype(str).str.contains(char, regex=False).sum()
            
            if char_count > 0:
                format_results['special_characters'][char] = char_count
                self.quality_issues.append(f"Found {char_count} instances of problematic character '{char}'")
        
        return format_results
    
    def validate_business_rules(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate business-specific rules and logic"""
        logger.info("Validating business rules...")
        
        business_results = {
            'source_validation': {},
            'price_range_validation': {},
            'product_category_analysis': {}
        }
        
        # Source validation
        if 'Source' in df.columns:
            source_counts = df['Source'].value_counts()
            business_results['source_validation'] = {
                'sources': source_counts.to_dict(),
                'expected_source': 'powerbuy.co.th'
            }
            
            if 'powerbuy.co.th' not in source_counts:
                self.quality_issues.append("Expected source 'powerbuy.co.th' not found in data")
        
        # Price range validation (business logic)
        if 'Price_Numeric' in df.columns:
            # Reasonable price ranges for electronics
            very_cheap = (df['Price_Numeric'] < 100).sum()  # Less than 100 THB
            very_expensive = (df['Price_Numeric'] > 100000).sum()  # More than 100,000 THB
            
            business_results['price_range_validation'] = {
                'very_cheap_products': very_cheap,
                'very_expensive_products': very_expensive,
                'price_distribution': {
                    'under_1000': (df['Price_Numeric'] < 1000).sum(),
                    '1000_to_10000': ((df['Price_Numeric'] >= 1000) & (df['Price_Numeric'] < 10000)).sum(),
                    '10000_to_50000': ((df['Price_Numeric'] >= 10000) & (df['Price_Numeric'] < 50000)).sum(),
                    'over_50000': (df['Price_Numeric'] >= 50000).sum()
                }
            }
        
        # Product category analysis based on names
        if 'Name' in df.columns:
            iphone_count = df['Name'].str.contains('iPhone|APPLE', case=False, na=False).sum()
            samsung_count = df['Name'].str.contains('Samsung|Galaxy', case=False, na=False).sum()
            other_brands = len(df) - iphone_count - samsung_count
            
            business_results['product_category_analysis'] = {
                'iphone_products': iphone_count,
                'samsung_products': samsung_count,
                'other_products': other_brands
            }
        
        return business_results
    
    def check_error_handling_logs(self) -> Dict[str, Any]:
        """Check if error handling caught and logged failures appropriately"""
        logger.info("Checking error handling and logging...")
        
        error_analysis = {
            'log_files_found': [],
            'errors_logged': [],
            'warnings_logged': [],
            'error_handling_effectiveness': {}
        }
        
        # Check for log files
        log_dir = Path('logs')
        if log_dir.exists():
            log_files = list(log_dir.glob('*.log'))
            error_analysis['log_files_found'] = [str(f) for f in log_files]
            
            # Analyze recent log files for errors and warnings
            recent_logs = sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
            
            for log_file in recent_logs:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Count errors and warnings
                    error_lines = [line for line in content.split('\n') if 'ERROR' in line]
                    warning_lines = [line for line in content.split('\n') if 'WARNING' in line]
                    
                    error_analysis['errors_logged'].extend(error_lines)
                    error_analysis['warnings_logged'].extend(warning_lines)
                    
                except Exception as e:
                    logger.warning(f"Could not read log file {log_file}: {e}")
        
        # Analyze error handling effectiveness
        total_errors = len(error_analysis['errors_logged'])
        total_warnings = len(error_analysis['warnings_logged'])
        
        error_analysis['error_handling_effectiveness'] = {
            'total_errors_logged': total_errors,
            'total_warnings_logged': total_warnings,
            'error_handling_active': total_errors > 0 or total_warnings > 0
        }
        
        if total_errors == 0 and total_warnings == 0:
            logger.info("No errors or warnings found in recent logs - system appears stable")
        else:
            logger.info(f"Found {total_errors} errors and {total_warnings} warnings in recent logs")
        
        return error_analysis
    
    def generate_quality_report(self, df: pd.DataFrame, summary: Dict, 
                              completeness: Dict, consistency: Dict, 
                              format_check: Dict, business_rules: Dict,
                              error_analysis: Dict) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        logger.info("Generating quality report...")
        
        # Calculate overall quality score
        total_checks = 0
        passed_checks = 0
        
        # Completeness score
        missing_data_penalty = sum(completeness['missing_values'].values())
        total_checks += len(df.columns)
        passed_checks += len(df.columns) - len([c for c in completeness['missing_values'].values() if c > 0])
        
        # Consistency score
        consistency_issues = len([k for k, v in consistency.items() if isinstance(v, dict) and any(val > 0 for val in v.values() if isinstance(val, (int, float)))])
        total_checks += 4  # price, sku, stock, name validations
        passed_checks += 4 - consistency_issues
        
        # Format score
        format_issues = len(format_check['special_characters'])
        total_checks += 1
        passed_checks += 1 if format_issues == 0 else 0
        
        quality_score = round((passed_checks / total_checks) * 100, 2) if total_checks > 0 else 0
        
        quality_report = {
            'report_timestamp': datetime.now().isoformat(),
            'dataset_overview': {
                'csv_file': self.csv_file,
                'total_records': len(df),
                'total_columns': len(df.columns),
                'file_size_mb': round(os.path.getsize(self.csv_file) / (1024 * 1024), 2),
                'processing_summary': summary
            },
            'quality_score': quality_score,
            'quality_grade': self._get_quality_grade(quality_score),
            'completeness_analysis': completeness,
            'consistency_analysis': consistency,
            'format_analysis': format_check,
            'business_rules_analysis': business_rules,
            'error_handling_analysis': error_analysis,
            'quality_issues': self.quality_issues,
            'recommendations': self._generate_recommendations()
        }
        
        return quality_report
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 95:
            return 'A+ (Excellent)'
        elif score >= 90:
            return 'A (Very Good)'
        elif score >= 85:
            return 'B+ (Good)'
        elif score >= 80:
            return 'B (Acceptable)'
        elif score >= 70:
            return 'C (Needs Improvement)'
        else:
            return 'D (Poor Quality)'
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on quality issues found"""
        recommendations = []
        
        if len(self.quality_issues) == 0:
            recommendations.append("Dataset quality is excellent - no major issues found")
        else:
            recommendations.append("Address the following quality issues:")
            for issue in self.quality_issues[:10]:  # Top 10 issues
                recommendations.append(f"  - {issue}")
        
        # General recommendations
        recommendations.extend([
            "Continue monitoring data quality with regular checks",
            "Implement automated validation in the data pipeline",
            "Consider adding more comprehensive error handling for edge cases"
        ])
        
        return recommendations
    
    def run_complete_quality_check(self) -> Dict[str, Any]:
        """Run complete quality check on the dataset"""
        logger.info("Starting complete dataset quality check...")
        
        # Load data
        df, summary = self.load_data()
        
        # Run all validation checks
        completeness = self.validate_data_completeness(df)
        consistency = self.validate_data_consistency(df)
        format_check = self.validate_encoding_and_format(df)
        business_rules = self.validate_business_rules(df)
        error_analysis = self.check_error_handling_logs()
        
        # Generate comprehensive report
        quality_report = self.generate_quality_report(
            df, summary, completeness, consistency, 
            format_check, business_rules, error_analysis
        )
        
        logger.info(f"Quality check completed. Overall score: {quality_report['quality_score']}% ({quality_report['quality_grade']})")
        
        return quality_report

def main():
    """Main function to run quality check"""
    # File paths
    csv_file = "output/competitor_prices_complete_2025-08-05.csv"
    summary_file = "output/processing_summary_2025-08-05.json"
    
    # Check if files exist
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        return
    
    if not os.path.exists(summary_file):
        logger.error(f"Processing summary file not found: {summary_file}")
        return
    
    # Create quality checker and run checks
    checker = DatasetQualityChecker(csv_file, summary_file)
    quality_report = checker.run_complete_quality_check()
    
    # Save quality report (convert numpy types to native Python types)
    def convert_numpy_types(obj):
        """Convert numpy types to native Python types for JSON serialization"""
        if hasattr(obj, 'item'):
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(v) for v in obj]
        else:
            return obj
    
    quality_report_serializable = convert_numpy_types(quality_report)
    
    report_file = f"output/quality_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(quality_report_serializable, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Quality report saved to: {report_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("DATASET QUALITY CHECK SUMMARY")
    print("="*80)
    print(f"Dataset: {csv_file}")
    print(f"Total Records: {quality_report['dataset_overview']['total_records']:,}")
    print(f"Quality Score: {quality_report['quality_score']}%")
    print(f"Quality Grade: {quality_report['quality_grade']}")
    print(f"Issues Found: {len(quality_report['quality_issues'])}")
    
    if quality_report['quality_issues']:
        print("\nTop Quality Issues:")
        for i, issue in enumerate(quality_report['quality_issues'][:5], 1):
            print(f"  {i}. {issue}")
    
    print(f"\nDetailed report saved to: {report_file}")
    print("="*80)

if __name__ == "__main__":
    main()
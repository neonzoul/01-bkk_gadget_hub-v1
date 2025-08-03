#!/usr/bin/env python3
"""
Script to prepare client communication package for Task 9
This script helps organize the deliverables for the early milestone delivery
"""

import os
import shutil
from datetime import datetime
import zipfile

def create_client_package():
    """Create a client communication package with all deliverables"""
    
    # Create package directory
    package_dir = "client_package_task9"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    print("🚀 Creating Client Communication Package for Task 9...")
    print("=" * 60)
    
    # Files to include in the package
    files_to_include = [
        ("BKK_Gadget_Hub_Sample.csv", "Sample CSV file with 101 products"),
        ("task_8_sample_csv_report.md", "Detailed technical implementation report"),
        ("Task_8_Sample_CSV_Technical_Report.md", "Professional technical report for client"),
        ("client_communication_task9.md", "Email template and communication materials")
    ]
    
    # Copy files to package directory
    files_copied = 0
    for filename, description in files_to_include:
        if os.path.exists(filename):
            shutil.copy2(filename, package_dir)
            print(f"✅ Copied: {filename}")
            print(f"   Description: {description}")
            files_copied += 1
        else:
            print(f"❌ Missing: {filename}")
    
    print("\n" + "=" * 60)
    print(f"📦 Package Summary:")
    print(f"   Files copied: {files_copied}/{len(files_to_include)}")
    print(f"   Package directory: {package_dir}/")
    
    # Create a README for the client package
    readme_content = f"""# PowerBuy Scraper - Early Milestone Delivery Package

**Date:** {datetime.now().strftime('%B %d, %Y')}
**Project:** PowerBuy Competitor Price Monitoring System
**Milestone:** Task 8 & 9 - Sample Data and Client Communication

## Package Contents

### 1. Sample Data File
- **BKK_Gadget_Hub_Sample.csv** - Sample CSV with 101 PowerBuy products
  - UTF-8 encoded with Thai language support
  - Business-compliant format (Name, SKU, Price, Stock Status, Source)
  - Ready for import testing into client systems

### 2. Technical Documentation
- **Task_8_Sample_CSV_Technical_Report.md** - Professional technical report
  - Detailed implementation analysis
  - Data quality metrics and validation results
  - Thai language support verification
  - Client review checklist

- **task_8_sample_csv_report.md** - Detailed implementation report
  - Complete technical implementation details
  - Requirements satisfaction documentation
  - Performance characteristics and statistics

### 3. Communication Materials
- **client_communication_task9.md** - Email template and feedback forms
  - Professional email template for client communication
  - Feedback tracking templates
  - Next steps and contact information

## Client Review Required

Please review the sample CSV file and provide feedback on:
1. **Data Format:** CSV structure and column organization
2. **Thai Language:** Character encoding and display
3. **Business Requirements:** Data content and formatting
4. **Import Compatibility:** System integration requirements

## Next Steps

Based on your feedback, we will:
1. Implement any required format adjustments
2. Process the complete dataset from all 20 search terms
3. Generate the final comprehensive CSV file
4. Deliver the complete solution by August 8th

## Contact Information

For questions or feedback, please contact the development team.

---
**Project Progress:** 70.6% Complete (12/17 tasks finished)
**Implementation Context:** Kiro spec with Claude 3.5 Sonnet
"""
    
    # Write README to package directory
    with open(os.path.join(package_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Created: README.md with package overview")
    
    # Calculate package size
    total_size = 0
    for root, dirs, files in os.walk(package_dir):
        for file in files:
            filepath = os.path.join(root, file)
            total_size += os.path.getsize(filepath)
    
    print(f"\n📊 Package Statistics:")
    print(f"   Total files: {len(os.listdir(package_dir))}")
    print(f"   Package size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    # Create ZIP file for easy sharing
    zip_filename = f"PowerBuy_Scraper_Early_Milestone_{datetime.now().strftime('%Y%m%d')}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, package_dir)
                zipf.write(filepath, arcname)
    
    zip_size = os.path.getsize(zip_filename)
    print(f"\n📦 Created ZIP package: {zip_filename}")
    print(f"   ZIP size: {zip_size:,} bytes ({zip_size/1024:.1f} KB)")
    
    print("\n" + "=" * 60)
    print("✅ Client Communication Package Ready!")
    print(f"📁 Package directory: {package_dir}/")
    print(f"📦 ZIP file: {zip_filename}")
    print("\n🚀 Ready for client delivery!")
    
    return package_dir, zip_filename

def validate_package_contents():
    """Validate that all required files are present and properly formatted"""
    
    print("\n🔍 Validating Package Contents...")
    print("=" * 40)
    
    required_files = [
        "BKK_Gadget_Hub_Sample.csv",
        "task_8_sample_csv_report.md", 
        "Task_8_Sample_CSV_Technical_Report.md",
        "client_communication_task9.md"
    ]
    
    validation_results = []
    
    for filename in required_files:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✅ {filename} - {file_size:,} bytes")
            validation_results.append(True)
            
            # Special validation for CSV file
            if filename.endswith('.csv'):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"   📊 CSV: {len(lines)-1} data rows + 1 header")
                        
                        # Check for Thai characters
                        thai_found = any('ก' <= char <= '๙' for line in lines for char in line)
                        print(f"   🇹🇭 Thai characters: {'Found' if thai_found else 'Not found'}")
                        
                except Exception as e:
                    print(f"   ❌ CSV validation error: {e}")
                    validation_results[-1] = False
        else:
            print(f"❌ {filename} - Missing")
            validation_results.append(False)
    
    success_rate = sum(validation_results) / len(validation_results) * 100
    print(f"\n📈 Validation Results: {success_rate:.1f}% ({sum(validation_results)}/{len(validation_results)} files)")
    
    return all(validation_results)

if __name__ == "__main__":
    print("🎯 PowerBuy Scraper - Task 9 Client Communication Package")
    print("=" * 60)
    
    # Validate required files exist
    if validate_package_contents():
        print("\n✅ All required files validated successfully!")
        
        # Create client package
        package_dir, zip_file = create_client_package()
        
        print("\n📋 Next Steps:")
        print("1. Review the email template in client_communication_task9.md")
        print("2. Customize the email with specific client details")
        print("3. Attach the ZIP file to the email")
        print("4. Send to client for review and feedback")
        print("5. Document client feedback for implementation")
        
    else:
        print("\n❌ Package validation failed!")
        print("Please ensure all required files are present before creating the package.")
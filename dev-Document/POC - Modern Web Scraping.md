# POC - Project BKK Gadget Hub (Thai e-commerce store)

**Date:** July 26, 2025

---

## 📋 Project Overview

### Project Purpose: Proof of Concept

This project serves as a **proof of concept** to demonstrate that we can reliably extract product data from modern, protected e-commerce websites like PowerBuy. The success of this implementation will validate our methodology for handling:

-   **Dynamic JavaScript-rendered content** (prices loaded after page load)
-   **Cloudflare anti-bot protection** (browser fingerprinting, challenge pages)
-   **Complex e-commerce architectures** (SPAs, internal APIs, session management)
-   **Multi-page pagination workflows** (50 items per page, action-triggered navigation)

### Success Validation Criteria

The proof of concept will be considered successful when we can:

1. **Consistently extract** all 4 data fields from target product pages across multiple search result pages
2. **Handle pagination automatically** - detect total items, calculate pages, navigate between pages
3. **Bypass protection measures** without manual intervention
4. **Deliver clean, structured data** in CSV format ready for business use
5. **Maintain >95% success rate** across multiple test runs with varying result counts
6. **Complete extraction** within reasonable time limits (scales with total items: ~2-5 minutes per 100 items)

### Strategic Value

Success in this project establishes our capability to handle **Tier 2 complexity websites** - those with moderate protection and dynamic content. This positions us for similar e-commerce scraping projects and validates our technical approach for future complex scraping challenges.

### Data Requirements

-   **Product Name** - Full product title
-   **Price (THB)** - Current selling price in Thai Baht
-   **Stock Status** - Availability (In Stock/Out of Stock)
-   **SKU/Product Code** - Unique product identifier

---

## 🎯 Why Traditional Scraping Fails

### Challenge 1: Dynamic Content Loading

```
❌ Problem: Price data loads via JavaScript AFTER initial page load
❌ Impact: Standard HTTP requests only get empty price containers
❌ Example: <span id="price">Loading...</span> → Later becomes actual price
```

### Challenge 2: Cloudflare Protection

```
❌ Bot Detection: Cloudflare analyzes request patterns, headers, timing
❌ Browser Fingerprinting: Checks for automation signatures
❌ Challenge Pages: CAPTCHA-like verification screens
❌ Rate Limiting: Aggressive blocking of rapid requests
```

### Challenge 3: Modern E-commerce Architecture

```
❌ Single Page Applications (SPA): Content rendered client-side
❌ API Endpoints: Data fetched from internal APIs with dynamic URLs
❌ Session Management: Requires cookies and proper session handling
❌ Action-Triggered APIs: JSON endpoints only appear after user interactions
```

### Challenge 4: Action-Dependent Data Loading

```
❌ Problem: Direct URL access doesn't trigger API calls
❌ Example: https://www.powerbuy.co.th/th/search/samsung?fill=1-0%7C2-0
   - Direct access: No samsung.json?fill=2-0&keyword=samsung in Network tab
   - Requires: User search action to trigger JSON endpoint
❌ Impact: Static URL scraping misses dynamic API data sources
```

### Challenge 5: Multi-Page Pagination Complexity

```
❌ Problem: Search results span multiple pages (50 items per page maximum)
❌ Direct URL Access Fails: https://www.powerbuy.co.th/th/search/iphone?page=2
   - No JSON API calls triggered
   - Missing product data and pagination metadata
❌ Architecture Impact: Must handle variable result counts (61 items = 2 pages)
❌ Navigation Dependency: Requires user interaction simulation for each page
❌ Time Scaling: Processing time increases linearly with total item count
```

---

## 🔧 Our Solution: Playwright-Based Dynamic Scraping

### Core Technology Stack

-   **Python** - Main programming language
-   **Playwright** - Browser automation (handles JS rendering)
-   **Persistent Browser Context** - Maintains session between runs
-   **CSV Export** - Clean, structured data output

### Method Breakdown

#### 1. Browser Automation Approach

```python
# Instead of simple HTTP requests:
requests.get(url)  # ❌ Gets static HTML only

# We use full browser rendering:
playwright.chromium.launch_persistent_context()  # ✅ Executes JavaScript
```

#### 2. Persistent User Data

```
📁 user_data/
├── cookies.db          # Session cookies
├── local_storage/      # Browser storage
├── cache/             # Cached resources
└── preferences        # Browser settings
```

**Why:** Appears as returning user, bypasses bot detection

#### 3. Anti-Detection Techniques

```python
args=['--disable-blink-features=AutomationControlled']  # Hide automation flags
user_agent='Mozilla/5.0...'  # Real browser user agent
viewport={'width': 1920, 'height': 1080}  # Standard screen size
```

#### 4. Dynamic Content Handling

```python
# Wait for JavaScript to load prices
page.wait_for_load_state("networkidle")
time.sleep(2)  # Additional buffer for async operations
```

#### 5. Action-Triggered API Discovery

```python
# Problem: Direct URL access doesn't reveal JSON endpoints
# https://www.powerbuy.co.th/th/search/samsung?fill=1-0%7C2-0
# ❌ No samsung.json?fill=2-0&keyword=samsung appears in Network tab

# Solution: Simulate user search actions to trigger API calls
page.goto("https://www.powerbuy.co.th")
page.fill('input[name="search"]', 'samsung')  # Trigger search action
page.click('button[type="submit"]')

# Now JSON endpoints become visible:
# ✅ samsung.json?fill=2-0&keyword=samsung appears in Network tab
# ✅ Can intercept and extract structured data from API responses
```

#### 6. Pagination Handling & Total Item Discovery

```python
# Problem: Each search page shows maximum 50 items
# Need to determine total items and calculate required pages

# Example: Searching "iphone" reveals total item count in JSON response:
# iphone.json?keyword=iphone contains:
# pageProps: {categoryData: null, ...}
# productpaging: {skcount: "61"}
# skcount: "61" = Total available items

# Calculation: 61 items ÷ 50 items per page = 2 pages needed
# Page 1: https://www.powerbuy.co.th/search/iphone (items 1-50)
# Page 2: https://www.powerbuy.co.th/th/search/iphone?page=2 (items 51-61)

# Critical: Direct URL access to page=2 won't trigger JSON endpoints
# Must simulate user navigation by clicking "Next Page" button
```

**Pagination Strategy:**

```python
def extract_total_items(json_response):
    """Extract total item count from initial search JSON"""
    return int(json_response['pageProps']['productpaging']['skcount'])

def calculate_pages_needed(total_items, items_per_page=50):
    """Calculate how many pages to scrape"""
    return math.ceil(total_items / items_per_page)

def navigate_to_next_page(page):
    """Click next page button to trigger JSON API calls"""
    page.click('button[aria-label="Next page"]')
    page.wait_for_load_state("networkidle")
```

---

## 🏗️ Architectural Implications

### Impact on Project Architecture

The pagination discovery significantly affects the core architectural design:

#### 1. **Asynchronous Processing Complexity**

```python
# Original: Fixed 20 URLs from client
urls = ["url1", "url2", ..., "url20"]  # Known quantity

# New Reality: Variable item counts per search term
search_terms = ["iphone", "samsung", "laptop"]
# Each term may yield 61, 143, 89 items respectively
# Total pages: 2 + 3 + 2 = 7 pages to process
```

#### 2. **Time Estimation & Scaling**

```
Original Estimate: ~2-5 minutes for 20 fixed URLs
New Reality: Time = (Total Items ÷ 50) × Page Processing Time
Example: 300 items = 6 pages × 45 seconds = ~4.5 minutes
```

#### 3. **Data Structure Requirements**

```python
# Enhanced data model needed:
class ScrapingSession(BaseModel):
    search_term: str
    total_items: int
    pages_required: int
    items_per_page: int = 50
    processing_time: float
    success_rate: float
```

#### 4. **Error Handling & Recovery**

```python
# Must handle page-level failures gracefully:
async def scrape_search_results(search_term):
    total_items = await get_total_count(search_term)
    pages_needed = calculate_pages_needed(total_items)

    results = []
    for page_num in range(1, pages_needed + 1):
        try:
            page_data = await scrape_page(search_term, page_num)
            results.extend(page_data)
        except PageError:
            log_error(f"Failed page {page_num} for {search_term}")
            continue  # Continue with remaining pages

    return results
```

#### 5. **Resource Management**

```python
# Browser context must persist across multiple page navigations
# Higher memory usage due to extended browser sessions
# Need cleanup strategies for long-running scraping sessions
```

---

## 🚀 What We CAN Do

### ✅ Capabilities

1. **Handle Dynamic Content**

    - Extract prices loaded via JavaScript
    - Wait for AJAX calls to complete
    - Process single-page applications
    - Trigger action-dependent API endpoints

2. **API Endpoint Discovery**

    - Simulate user interactions to reveal hidden JSON APIs
    - Intercept network requests for structured data
    - Handle action-triggered data loading patterns
    - Extract data from dynamic API responses

3. **Multi-Page Navigation & Pagination**

    - Detect total item count from JSON responses (e.g., `skcount: "61"`)
    - Calculate required pages automatically (total items ÷ 50 items per page)
    - Simulate user clicks for page navigation (direct URL access fails)
    - Extract data across multiple pages seamlessly
    - Handle pagination boundaries and edge cases

4. **Bypass Basic Protection**

    - Navigate Cloudflare challenges
    - Maintain session cookies
    - Simulate human browsing patterns

5. **Reliable Data Extraction**

    - Multiple selector fallbacks
    - Error handling and recovery
    - Data validation and cleaning

6. **Production-Ready Features**
    - Comprehensive logging
    - Screenshot capture for debugging
    - Structured CSV output
    - Progress tracking

### 📊 Data Quality Assurance

```python
# Data validation example
product_data = {
    'name': validate_text(extracted_name),
    'price': validate_currency(extracted_price),
    'stock': validate_stock_status(extracted_stock),
    'sku': validate_sku(extracted_sku)
}
```

---

## ⚠️ What We CAN'T Do (Limitations)

### ❌ Technical Limitations

1. **Advanced Bot Detection**

    - Machine learning-based detection systems
    - Behavioral analysis over time
    - Device fingerprinting beyond basic masking

2. **Complex Authentication**

    - Two-factor authentication (2FA)
    - Dynamic login systems
    - Member-only content requiring human verification

3. **Real-time Requirements**

    - Sub-second response times
    - Continuous monitoring (minutes apart)
    - Live price streaming

4. **Scale Limitations**
    - 1000+ products per run (browser memory limits)
    - Multiple concurrent browser instances
    - Very high-frequency requests (>1 per second)

### 🔒 Ethical & Legal Boundaries

```
❌ Cannot scrape if:
   - robots.txt explicitly forbids
   - Terms of Service prohibit data extraction
   - Personal/private data is involved
   - Scraping causes server overload
```

---

## 🛠️ Implementation Strategy Idea

### Phase 1: Development Setup

1. **Environment Preparation**

    ```bash
    pip install playwright beautifulsoup4 pandas pydantic
    playwright install chromium
    ```

2. **Initial Testing**
    - Test single product page
    - Verify data extraction accuracy
    - Validate anti-detection measures
    - Map action-triggered API endpoints
    - Test JSON data interception methods
    - Test pagination flow and total item counting
    - Validate multi-page navigation without direct URL access

### Phase 2: Production Implementation

1. **Robust Error Handling**

    ```python
    try:
        data = extract_product_data(page)
    except TimeoutError:
        log_error("Page load timeout")
        take_screenshot_for_debug()
    except ElementNotFound:
        try_alternative_selectors()
    ```

2. **Data Validation**
    ```python
    class ProductData(BaseModel):
        name: str
        price: float
        stock_status: str
        sku: str
    ```

### Phase 3: Monitoring & Maintenance

1. **Success Metrics**

    - Data extraction success rate (>95%)
    - Average execution time (<2 minutes per product)
    - Error recovery rate

2. **Maintenance Schedule**
    - Weekly selector validation
    - Monthly anti-detection review
    - Quarterly full system audit

---

## 📈 Expected Outcomes

### Immediate Benefits

-   **Time Savings:** 2-3 hours daily → 5 minutes automated
-   **Data Accuracy:** 100% consistent formatting
-   **Competitive Advantage:** Real-time pricing intelligence

### Success Criteria

```
✅ Variable product counts scraped successfully (50-500+ items per search)
✅ All 4 data fields extracted accurately across multiple pages
✅ <5% error rate across runs with different pagination scenarios
✅ CSV format ready for business use with proper item counting
✅ Runs reliably without manual intervention regardless of result count
✅ Proper time estimation based on total items discovered
```

---

## 🔍 Risk Assessment & Mitigation

### High Risk

-   **Website Structure Changes:** Monthly monitoring required
-   **Anti-bot Upgrades:** Continuous adaptation needed

### Medium Risk

-   **IP Blocking:** Use residential proxies if needed
-   **Rate Limiting:** Implement smart delays

### Low Risk

-   **Server Downtime:** Retry mechanisms in place
-   **Data Format Changes:** Flexible parsing logic

---

## 🎯 Team Guidelines

### Development Best Practices

1. **Always test on sample data first**
2. **Implement comprehensive logging**
3. **Use version control for scraper iterations**
4. **Document all selector changes**
5. **Maintain ethical scraping standards**

### Deployment Checklist

```
□ Test on all 20 target URLs
□ Verify data quality and completeness
□ Check execution time performance
□ Validate CSV output format
□ Test error recovery scenarios
□ Document any site-specific quirks
```

---

_This methodology ensures reliable, ethical, and maintainable web scraping for competitive intelligence while respecting target website resources and terms of service._

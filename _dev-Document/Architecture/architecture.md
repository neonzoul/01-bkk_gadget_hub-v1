# Project Overview: BKK Gadget Hub Web Scraper

The core objective of Project-portfolio1 is to develop a reliable web scraping solution for Chaiwat S.'s e-commerce store, BKK Gadget Hub. Chaiwat's primary problem is the time and sales lost due to manually checking competitor prices on PowerBuy.co.th for his top 20 products. His previous attempt with a freelancer failed because the competitor's site loads prices using JavaScript. The goal is to provide clean, accurate price and stock data daily in a CSV file, enabling instant pricing adjustments. This project falls under your "Tier 2: Standard Scraper Setup" service package, specifically designed for handling complex, dynamic websites.

## Architectural Philosophy

The architecture for this project is designed not just to deliver a script, but a reliable and professional business intelligence solution. It adheres to your Unique Selling Proposition (USP) by focusing on:

-   **Handling "Unhandleable" Web**: Reliably extracting data from dynamic, JavaScript-heavy websites.
-   **Asynchronous Advantage**: Ensuring speed and efficiency while maintaining polite scraping practices.
-   **AI-Powered Workflow**: Leveraging AI to accelerate development and enhance quality.
-   **Ethical Scraping Policy**: Operating with respect for website resources and legal boundaries.  
    The design emphasizes modularity, maintainability, scalability (for future enhancements), and robust data quality assurance.

## Core Technology Stack

The foundation of this architecture is a modern Python-based stack, chosen specifically to address the challenges of dynamic web content and ensure high performance:

-   **Python**: The main programming language, due to its extensive ecosystem of libraries for web scraping.
-   **Playwright (Asynchronous API)**: This is the primary tool for browser automation, crucial for interacting with powerbuy.co.th, which loads data dynamically via JavaScript. Playwright's asynchronous API is vital for concurrent operations and its auto-wait capabilities ensure data is captured only after it has fully rendered.
-   **Pydantic**: Used to define data models and enforce runtime type validation, ensuring that all extracted data conforms to the expected structure (e.g., price is a float, product name is text). This guarantees the delivery of clean, reliable, and structured data.
-   **Pandas**: For final data cleaning, manipulation, and export to the client's desired CSV format.
-   **asyncio (Built-in)**: The core Python library enabling asynchronous programming, allowing the scraper to handle multiple network requests and operations concurrently, drastically reducing execution time.
-   **aiohttp (for potential hybrid workflows)**: While PowerBuy is dynamic, for future projects or if sub-pages were static, aiohttp could be used as an asynchronous HTTP client for making high-concurrency requests with lower overhead than a full browser.
-   **asyncio.Semaphore**: To control the number of concurrent requests, preventing the scraper from overwhelming the target server and mitigating the risk of being blocked.
-   **Beautiful Soup**: For parsing HTML content once retrieved by Playwright, making it easier to navigate the document and extract specific data points.

## Detailed Architectural Design

The architecture is designed with clear separation of concerns, robust data flow, and resilience against common scraping challenges:

### Modular Project Structure:

The project will follow a modular structure to enhance readability, maintainability, and extensibility:

-   `project_root/scrapers/`: Contains the core scraping logic for specific websites, such as `powerbuy_scraper.py`. This module will manage browser instantiation (Playwright), page navigation, and raw data extraction.
-   `parsers/`: Houses functions responsible for parsing the raw HTML content received from the scraper and extracting specific data points (Product Name, Price, Stock Status, SKU).
-   `validators/`: Defines Pydantic models (`schemas.py`) that validate the structure and data types of the extracted information.
-   `output/`: Designated for storing the final CSV output.
-   `.env`: For environment-specific variables and sensitive information like API keys or proxy settings (though not strictly needed for PowerBuy, it's a best practice for future expansion).
-   `main.py`: The entry point script that orchestrates the scraping process, reading URLs, initiating scraping tasks, and handling data processing and export.
-   `requirements.txt`: Lists all Python dependencies for easy environment recreation.

### Asynchronous Core Engine:

The project will heavily leverage asynchronous programming for efficiency and speed:

-   **Concurrent Page Scraping**: `main.py` will read the list of 20 PowerBuy product URLs provided by Chaiwat. It will then use `asyncio.gather` to concurrently execute scraping tasks for these URLs. This allows multiple pages to be processed in parallel rather than sequentially, significantly reducing the total execution time.
-   **Playwright's Async API**: Each individual scraping task within the `scrapers/` module will utilize Playwright's native asynchronous capabilities (`await browser.new_page()`, `await page.goto()`, `await page.wait_for_selector()`, etc.).
-   **Concurrency Control**: To ensure "polite" scraping and prevent overloading PowerBuy's servers, `asyncio.Semaphore` will be implemented around the network request logic within the scraper. This will limit the number of simultaneous active connections to the target domain.

### Robust Data Extraction and Validation:

-   **Dynamic Content Handling**: The `scrapers/` module, specifically within the Playwright interactions, will employ `page.wait_for_selector()` calls. This explicitly tells Playwright to wait until critical elements like price and stock status, which are loaded dynamically by JavaScript, are present and visible on the page before attempting to extract them. This directly addresses the failure point of the previous freelancer.
-   **Raw Data Extraction & Parsing**: Once elements are loaded, their raw text will be extracted. The `parsers/` module will then take this raw content and use Beautiful Soup to reliably extract the Product Name, Price (THB), Stock Status, and SKU/Product Code.
-   **Data Cleaning**: Immediately after extraction, raw data will undergo initial cleaning (e.g., removing currency symbols, commas, and converting price strings to numerical formats like floats).
-   **Pydantic Validation**: The cleaned, raw data for each product will then be passed into the predefined Pydantic models in `validators/schemas.py`. This step programmatically validates the data's structure and types, ensuring consistency and catching any errors (e.g., if a price isn't a valid number) before it's stored.

### Error Handling and Resilience:

-   The scraping loop will include `try...except` blocks to catch common exceptions (e.g., network errors, element not found errors). If one URL fails, the scraper will log the error and continue processing the remaining URLs, ensuring that partial data is still collected rather than the entire process crashing.
-   Playwright's built-in stealth features and network request interception (to block unnecessary resources like images/CSS) can be used to further enhance the scraper's robustness and speed, making it less prone to detection and blocking.

### Output and Deliverables:

-   All successfully scraped and validated data objects will be collected into a list.
-   Pandas will be used to convert this list into a DataFrame and then export it to the final CSV file, named `competitor_prices_2025-08-08.csv` (or the appropriate delivery date).
-   The architecture supports generating this file cleanly and accurately for Chaiwat, who values "a clean data file I receive each morning that is accurate".

## Integration with PowerBuy POC

The architectural design directly builds upon the success criteria and findings of the Proof of Concept (POC) for PowerBuy.co.th:

-   The POC successfully demonstrated the ability to reliably extract all 4 data fields (Product Name, Price, Stock Status, SKU) from a dynamic site, which is precisely what the Playwright-Pydantic-Pandas stack in this architecture is designed to do.
-   The POC validated the methodology for handling dynamic JavaScript-rendered content, affirming the choice of Playwright as the core browser automation tool.
-   The emphasis on delivering clean, structured data is directly supported by the Pydantic validation and Pandas cleaning steps in the proposed architecture.

## Ethical Considerations (Guiding Principles)

While not direct architectural components, the following ethical principles will guide the implementation details of the architecture, aligning with your "Ethical Scraping Policy":

-   **Rate Limiting**: As mentioned, `asyncio.Semaphore` will ensure requests are spaced out, minimizing impact on the PowerBuy server.
-   **Respect for `robots.txt`**: Although PowerBuy is a competitor, the architecture design should always include a check for the target site's `robots.txt` file and adhere to its directives.
-   **Public Data Only**: The solution will only scrape publicly visible data, as confirmed by Chaiwat. There's no attempt to bypass logins or access restricted content.
-   **No PII Collection**: The data points required (Product Name, Price, Stock Status, SKU) are not Personally Identifiable Information, adhering to data privacy compliance.

By implementing this modular, asynchronous, and robust architecture, Project-portfolio1 will effectively deliver the required competitive intelligence to BKK Gadget Hub, validating your expertise in handling complex web scraping challenges and solidifying your reputation as a high-value service provider.

### Project Flow Design: BKK Gadget Hub Scraper (Project-portfolio1)

**Project Goal:** To develop a robust web scraping solution to automatically extract product name, price, stock status, and SKU for 20 specified items from powerbuy.co.th, delivering accurate data daily in a CSV format.

**Core Architectural Principles:**

-   **Modularity and Maintainability:** Separate code into logical components (scrapers, parsers, validators) for clarity and ease of future updates.
-   **Reliability and Robustness:** Implement strong error handling and explicit waiting mechanisms for dynamic content. Data will be rigorously validated.
-   **Efficiency and Scalability (Asynchronous Advantage):** Leverage asynchronous Python with Playwright to handle concurrent requests and dynamic content, ensuring fast and "polite" scraping.
-   **Professionalism:** Deliver clean, validated data with comprehensive documentation.
-   **Ethical Scraping:** Adhere to principles like rate limiting to minimize server impact.

---

#### Phase 1: Setup & Initial Proof of Concept (POC) – Handling Dynamic Content

1.  **Environment Setup (Day 1)**:

    -   **Create `project_root/` Directory:** Establish the main project folder.
    -   **Initialize Python Virtual Environment (`venv`):** Isolate project dependencies to prevent conflicts.
    -   **Install Core Libraries:** Install `playwright` (for browser automation), `pydantic` (for data validation), `pandas` (for data processing and CSV export), and `python-dotenv` (for configuration management).
    -   **Configure `.gitignore` and `.env`:** Exclude sensitive files (e.g., environment variables, virtual environment files) from version control for security and reproducibility.
    -   **Initial Project Structure:** Set up modular directories like `scrapers/`, `parsers/`, `validators/`, and `output/`. AI agents can assist with generating this boilerplate code.

2.  **Site Analysis & Single-Page Proof of Concept (POC) (Day 2-3)**:
    -   **Manual Website Inspection:** Thoroughly inspect PowerBuy.co.th using browser developer tools. The key is to **identify CSS selectors** for the "Product Name," "Price (THB)," "Stock Status," and "SKU/Product Code".
    -   **Analyze Network Requests:** Observe how prices and stock statuses are loaded. The client's previous experience indicates JavaScript-driven dynamic content, so we anticipate **AJAX calls**.
    -   **Basic Playwright Script Development (Asynchronous Core):**
        -   Write an **asynchronous Python script** using Playwright's API to launch a **headless browser**.
        -   Navigate to **one specific product URL** provided by Chaiwat.
        -   **Critical Dynamic Content Handling:** Use `page.wait_for_selector()` to explicitly wait for the dynamically loaded "Price" and "Stock Status" elements to appear on the page before attempting to extract them. This is the **key step that solves the problem** the previous freelancer failed on.
        -   **Optimize Network Traffic:** Implement `page.route()` to **intercept and block unnecessary resources** like images, CSS, and fonts. This speeds up page loading and reduces bandwidth consumption, contributing to "polite" scraping and efficiency.
        -   **Raw Data Extraction:** Extract the raw text content for all four required data points.
        -   **Initial Validation & Logging:** Print the extracted raw data to the console for immediate verification. Implement **comprehensive logging** (e.g., `logging.INFO`, `logging.DEBUG`) to track each step and aid in debugging.

#### Phase 2: Data Modeling, Scaling & Robustness

3.  **Data Modeling & Validation (Day 4)**:

    -   **Define Pydantic Schema (`validators/schemas.py`):** Create a Pydantic `Product` model to define the expected structure and data types for the scraped information. This will enforce that `price_thb` is a `float`, and `product_name`, `stock_status`, `sku` are `str`. AI can be used to generate this model from sample data.
    -   **Data Cleaning and Coercion:** Implement pre-validation cleaning steps within the script to handle raw data. This includes removing currency symbols (e.g., "฿"), commas from prices, and converting price strings to floats before passing them to the Pydantic model for validation. This ensures the data is "clean, reliable, and structured".

4.  **Scaling the Scraper with Asynchronous Operations (Day 5-6)**:
    -   **Load Target URLs:** Modify the scraper to read the list of all **20 product URLs** from a simple text file provided by the client.
    -   **Concurrent Scraping with `asyncio.gather`:**
        -   Refactor the single-page scraping logic into an `async` function (coroutine) that can process one URL and return a validated `Product` object.
        -   Use `asyncio.gather()` to **execute all 20 scraping tasks concurrently**. This parallel processing will drastically reduce the total time required to scrape all pages compared to sequential execution.
    -   **Concurrency Control with `asyncio.Semaphore`:** To avoid overwhelming PowerBuy's servers and prevent rate limiting or IP blocking, implement `asyncio.Semaphore` to **limit the number of concurrent connections** to the target domain. This demonstrates a professional and ethical approach to web scraping.
    -   **Robust Error Handling:** Integrate `try...except` blocks around each scraping task to **catch and handle exceptions gracefully**. If a specific URL fails, the script will log the error (e.g., `logging.WARNING`, `logging.ERROR`) and continue processing the remaining URLs, ensuring that a single failure does not stop the entire scrape.
    -   **Intermediate Data Export:** Use `pandas` to collect the list of validated `Product` objects and export a **sample CSV file (`BKK_Gadget_Hub_Sample.csv`)** containing data from 5 of the 20 URLs. This serves as the "Early Milestone Delivery".

#### Phase 3: Finalization & Professional Handoff

5.  **Full-Scale Execution & Final Quality Assurance (Day 8-9)**:

    -   **Client Feedback Integration:** Incorporate any feedback received from Chaiwat on the sample CSV.
    -   **Execute Full Scrape:** Run the optimized scraper on all 20 URLs to generate the complete dataset. Monitor logs closely for any anomalies.
    -   **Final Data Cleaning with Pandas:** Perform any final data cleaning or transformation passes using Pandas to ensure the dataset is perfectly clean and ready for business use. This includes verifying data types, handling any remaining missing values, and ensuring consistent formatting.

6.  **Deliverables Preparation (Day 10)**:
    -   **Final Data File Generation:** Create the final, cleaned data file in CSV format, named `competitor_prices_2025-08-08.csv`.
    -   **Project Handoff Report:** Draft a comprehensive **Project Handoff Report** in PDF format. This report will include:
        -   A project overview and objectives achieved.
        -   A summary of the data collected, including the total number of records and a **data dictionary** (Product Name, Price, Stock Status, SKU).
        -   Crucially, **technical notes** explaining how Playwright was used to handle the dynamic JavaScript content on PowerBuy.co.th, highlighting how it overcame previous scraper failures and validating the chosen approach.
        -   Instructions on how to open and use the provided CSV file.
    -   **Package Deliverables:** Create a ZIP archive containing both the final CSV file and the Project Handoff Report PDF.

---

This structured flow ensures that the project progresses logically, addresses the core technical challenges, leverages advanced asynchronous Python and Playwright capabilities, and culminates in a high-quality, professionally delivered solution that provides significant business value to the client.

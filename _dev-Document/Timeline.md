**Project:** BKK Gadget Hub - Tier 2 Scraper
**Start Date:** Friday, July 25, 2025
**Delivery Date:** Friday, August 8, 2025

---

### **Week 1: Development & Building Trust**

**Tomorrow, Day 1 (Friday, July 25): Kickoff & Setup**

-   `[x]` **Client Communication:** Respond to Chaiwat's message. Attach the Client Intake Questionnaire and explain its purpose.
-   `[x]` **Formalize:** Based on his (simulated) returned form, send the official proposal via Fastwork confirming the scope and price.
-   `[x]` **Set Expectations:** Once the order is placed, send your "Kickoff Confirmation" email. State clearly that you will provide a sample data file for his review on **Monday, August 4th**.
-   `[x]` **Technical Setup:** Create the project folder, initialize a Python virtual environment (`venv`), and create your initial `requirements.txt` file.

**Day 2 (Monday, July 28): Initial Scraping & POC Completion**

-   `[x]` **Goal:** Prove you can access and read the target site.
-   `[x]` **Task:** Write the basic `playwright` script to launch a browser, navigate to ONE of the PowerBuy URLs Chaiwat provided, and save the page's HTML content to a local file.
-   `[x]` **Analysis:** Examine the saved HTML to identify the CSS selectors for `Product Name` and `SKU`.
-   `[x]` **Major Breakthrough:** Discovered that PowerBuy loads product data via dynamic JSON API calls, not static HTML
-   `[x]` **POC Success:** Implemented network response interception to capture structured JSON data from `/_next/data/[id]/th/search/iphone.json`
-   `[x]` **Data Validation:** Successfully extracted Product Name, SKU, and Price from 50+ iPhone products
-   `[x]` **CSV Export:** Generated `test_collect.csv` with clean, structured data

**Day 3 (Tuesday, July 29): Architecture Implementation & Multi-Product Support**

-   `[X]` **Git Init:** Commmit Github Init Project Repo | Commit 'hello, world'
-   `[x]` **Achievement:** POC validates the architecture approach from `architecture.md`
-   `[x]` **Dynamic Content Mastery:** Proved Playwright + API interception handles JavaScript-heavy sites
-   `[x]` **Next Task:** Adapt POC for Chaiwat's 20 specific product URLs (individual products vs search results)
        - **Need to manual find item list**....(for this deliver in 2 weeks and then manual grab )
        - **after have JSON and then use Producer component to producing filter just query data for outcome update to CSV file**.
-   `[ ]` **Architecture Alignment:** Using Kiro with current project context. (Kiro can Edit This timeline to relate with real implementation)

**Day 4 (Wednesday, July 30): Data Modeling & Validation**

-   `[ ]` **Goal:** Ensure data is clean and correctly formatted according to architecture.
-   `[ ]` **Priority Task:** Implement Pydantic models as specified in `architecture.md`
-   `[ ]` **Task:** Create `validators/schemas.py` with Product model enforcing `price_thb` as `float` and other fields as `str`
-   `[ ]` **Implementation:** Integrate POC learnings - handle JSON data structure validation instead of raw HTML parsing
-   `[ ]` **Validation:** Apply Pydantic models to POC data to ensure type safety and data cleaning

**Day 5 (Thursday, July 31): Scaling & Individual Product Pages**

-   `[ ]` **Goal:** Adapt POC for individual product URLs (Chaiwat's requirement)
-   `[ ]` **Challenge:** POC works for search results - need to handle individual product page structure
-   `[ ]` **Task:** Investigate if individual product pages also use dynamic JSON loading
-   `[ ]` **Implementation:** Create URL list handler for Chaiwat's 20 specific product links
-   `[ ]` **Testing:** Verify data extraction works across different product types

**Day 6 (Friday, August 1): Modular Architecture & Error Handling**

-   `[ ]` **Goal:** Implement the full architecture from `architecture.md`
-   `[ ]` **Task:** Refactor POC into modular structure:
    -   `scrapers/powerbuy_scraper.py` - Core scraping logic
    -   `parsers/` - JSON data extraction functions
    -   `validators/` - Pydantic models
    -   `main.py` - Orchestration script
-   `[ ]` **Error Handling:** Add `try...except` blocks for production reliability
-   `[ ]` **CSV Enhancement:** Implement Pandas for final data export as specified in architecture

---

### **Week 2: Finalization & Professional Handoff**

**Day 7 (Monday, August 4): Early Milestone Delivery**

-   `[ ]` **Client Communication:** Send the "Early Milestone Delivery" email to Chaiwat. Attach the `BKK_Gadget_Hub_Sample.csv` and ask for his confirmation that the data and format are correct.

**Day 8 (Tuesday, August 5): Full Execution**

-   `[ ]` **Goal:** Scrape the entire dataset.
-   `[ ]` **Task:** (After Chaiwat's simulated "Looks great!" reply) Update your URL list to include all 20 product links.
-   `[ ]` **Task:** Run the full scrape and generate the complete CSV file.

**Day 9 (Wednesday, August 6): Quality Assurance**

-   `[ ]` **Goal:** Ensure the final deliverable is flawless.
-   `[ ]` **Task:** Perform a final quality check on the full dataset. Look for any inconsistencies or missing values that your error handling might have caught.
-   `[ ]` **Task:** Finalize the data and name the file `competitor_prices_2025-08-08.csv`.

**Day 10 (Thursday, August 7): Prepare Professional Package**

-   `[ ]` **Goal:** Go beyond expectations with the final delivery.
-   `[ ]` **Task:** Write the **Project Handoff Report**. Use the template from our simulation. This professional document is a key part of your premium service.
-   `[ ]` **Task:** Create a ZIP file containing both the final CSV and the PDF report.

**Delivery Day (Friday, August 8): Handoff & Project Completion**

-   `[ ]` **Client Communication:** Send the final delivery email to Chaiwat with the complete package attached.
-   `[ ]` **Action:** Mark the job as "Delivered" on the Fastwork platform.
-   `[ ]` **Next Step Prep:** Prepare your follow-up templates for asking for a review and suggesting the ongoing monitoring service in a few days.

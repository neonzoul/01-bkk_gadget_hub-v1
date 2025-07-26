**Project:** BKK Gadget Hub - Tier 2 Scraper
**Start Date:** Friday, July 25, 2025
**Delivery Date:** Friday, August 8, 2025

---

### **Week 1: Development & Building Trust**

**Tomorrow, Day 1 (Friday, July 25): Kickoff & Setup**

-   `[ ]` **Client Communication:** Respond to Chaiwat's message. Attach the Client Intake Questionnaire and explain its purpose.
-   `[ ]` **Formalize:** Based on his (simulated) returned form, send the official proposal via Fastwork confirming the scope and price.
-   `[ ]` **Set Expectations:** Once the order is placed, send your "Kickoff Confirmation" email. State clearly that you will provide a sample data file for his review on **Monday, August 4th**.
-   `[ ]` **Technical Setup:** Create the project folder, initialize a Python virtual environment (`venv`), and create your initial `requirements.txt` file.

**Day 2 (Monday, July 28): Initial Scraping**

-   `[ ]` **Goal:** Prove you can access and read the target site.
-   `[ ]` **Task:** Write the basic `playwright` script to launch a browser, navigate to ONE of the PowerBuy URLs Chaiwat provided, and save the page's HTML content to a local file.
-   `[ ]` **Analysis:** Examine the saved HTML to identify the CSS selectors for `Product Name` and `SKU`.

**Day 3 (Tuesday, July 29): Handling Dynamic Content**

-   `[ ]` **Goal:** Reliably extract data that loads via JavaScript.
-   `[ ]` **Task:** Modify your script to use `page.wait_for_selector()` to explicitly wait for the `Price` and `Stock Status` elements. This is the key step that fixes the problem the previous freelancer failed on.
-   `[ ]` **Validation:** Extract the raw text for all four fields (`Name`, `Price`, `Stock`, `SKU`) from a single page and print them to your console to confirm they are correct.

**Day 4 (Wednesday, July 30): Data Modeling & Validation**

-   `[ ]` **Goal:** Ensure data is clean and correctly formatted.
-   `[ ]` **Task:** Create a `validators.py` file and define a Pydantic `Product` model. It should enforce that `price_thb` is a `float` and the other fields are `str`.
-   `[ ]` **Implementation:** In your main script, pass the raw extracted data into this Pydantic model. Handle the necessary cleaning (e.g., removing "฿", commas, and converting the price to a float) before validation.

**Day 5 (Thursday, July 31): Scaling the Scraper**

-   `[ ]` **Goal:** Make the script work for multiple pages.
-   `[ ]` **Task:** Convert your script to read a list of 5-10 URLs from a simple text file.
-   `[ ]` **Task:** Loop through the URLs, scrape the data for each, validate it with your Pydantic model, and store the resulting objects in a list.

**Day 6 (Friday, August 1): Final Polish & Milestone Prep**

-   `[ ]` **Goal:** Prepare for the client check-in.
-   `[ ]` **Task:** Add error handling (`try...except`) to your loop so that if one URL fails, the script continues with the others.
-   `[ ]` **Task:** Use the `pandas` library to export your list of validated data objects to a CSV file named `BKK_Gadget_Hub_Sample.csv`. Review the file to ensure it's perfect.

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

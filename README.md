# AI-Driven E-Commerce Insights System

  <!-- **ACTION: Replace this with the URL to your screenshot** -->

This project is a comprehensive, end-to-end demonstration of a modern data stack designed to transform raw e-commerce data into actionable business intelligence and predictive insights. It showcases skills in data engineering, cloud data warehousing, business intelligence, and native cloud app deployment.

---

## Project Overview

The system addresses a classic business problem: how to leverage vast amounts of transactional data to understand performance, automate reporting, and make data-informed strategic decisions.

The project is broken down into three core components:

1.  **Automated Data Pipeline:** An ELT (Extract, Load, Transform) pipeline built with Python that extracts over 500,000 records from a source file, cleans the data, and loads it into a structured schema in a **Snowflake** cloud data warehouse.

2.  **Business Intelligence Dashboard:** A dynamic and interactive **Power BI** dashboard connected directly to Snowflake via DirectQuery. This dashboard automates the tracking of key performance indicators (KPIs) like total revenue, unique customers, and sales by country, effectively eliminating manual reporting.

3.  **AI-Powered Forecasting App:** A time-series forecasting model (SARIMA) trained on historical sales data. The model and a user-facing dashboard are deployed as a **Streamlit in Snowflake (SiS)** application, running natively within the Snowflake environment for maximum performance and security.

---

## Tech Stack

*   **Programming Language:** Python
*   **Data Warehouse & App Hosting:** Snowflake (including Streamlit in Snowflake)
*   **Business Intelligence:** Power BI
*   **Core Python Libraries:** Pandas, Snowflake Connector, Snowpark, Statsmodels, Joblib, Altair

---

## Project Execution

This project demonstrates the complete data lifecycle, from ingestion to deployment.

**1. Data Engineering (ELT):**
*   A Python script (`elt_pipeline/load_to_snowflake.py`) was engineered to automatically extract data from the source file.
*   The script performs initial cleaning and type conversion before loading over 400,000 clean records into a `RAW_DATA` schema in Snowflake.
*   A SQL transformation job is then run within Snowflake to create a final, analytics-ready `SALES_CLEANED` table, filtering out invalid transactions and creating new features like `TOTAL_PRICE`.

**2. Business Intelligence & Analytics:**
*   Power BI Desktop was connected to the `SALES_CLEANED` table in Snowflake using **DirectQuery**.
*   This connection enables the creation of a dynamic, real-time dashboard that reflects the "single source of truth" in the data warehouse.
*   The dashboard, shown above, automates key performance insights, reducing manual reporting time by an estimated 80% and allowing for interactive data exploration.

**3. Predictive Modeling & Native App Deployment:**
*   A SARIMA time-series model was trained on the historical sales data to forecast future revenue, achieving over 90% in-sample accuracy.
*   The trained model (`.pkl` file) and an interactive Streamlit application were deployed directly into **Streamlit in Snowflake (SiS)**.
*   This native deployment method provides superior security, performance, and simplified data access, representing a cutting-edge approach to deploying data applications. The app allows users to generate forecasts and visualize historical trends.

---

## How to Replicate

To run this project, you will need a Snowflake account with Streamlit in Snowflake enabled.

1.  **Clone the Repository:** Get the project files and structure.
2.  **Set Up Snowflake:** Run the initial SQL scripts to create the necessary databases and warehouses.
3.  **Run the ELT Pipeline:** Execute `load_to_snowflake.py` (after setting up local credentials) to populate the raw data table.
4.  **Run the SQL Transformation:** Execute the transform SQL to create the `SALES_CLEANED` table.
5.  **Connect Power BI:** Point Power BI Desktop to your Snowflake instance and build the dashboard visuals.
6.  **Train the Model:** Run `train_model.py` to generate the `sarima_model.pkl` file.
7.  **Deploy in Snowflake:**
    *   Create a stage in Snowflake and upload the `sarima_model.pkl` file.
    *   Create a new Streamlit App within the Snowflake UI.
    *   Paste the code from `forecasting_app/app.py` into the SiS editor.
    *   Add the required packages (`pandas`, `altair`, `joblib`, `scikit-learn`, `statsmodels`) and run the app.

This project successfully demonstrates the entire data value chain, from raw data engineering to deploying predictive AI tools for business governance.

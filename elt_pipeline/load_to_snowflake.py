import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
import os
from dotenv import load_dotenv
import sys

# --- Snowflake Connection Details ---
# !! BEST PRACTICE: Use environment variables or a secrets manager in a real project !!
# For this exercise, we will hardcode them but acknowledge it's not for production.
load_dotenv()

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")

SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "ECOMMERCE_DB"
SNOWFLAKE_SCHEMA = "RAW_DATA"

# --- Data File Details ---
FILE_PATH = os.path.join('data', 'Online Retail.xlsx')
RAW_TABLE_NAME = "RAW_RETAIL_SALES"


def clean_column_names(df):
    """Cleans DataFrame column names for Snowflake compatibility."""
    cols = df.columns
    new_cols = [c.upper().replace(' ', '_') for c in cols]
    df.columns = new_cols
    return df


def main():
    print("Starting ELT process...")

    # --- EXTRACT ---
    print(f"1. Extracting data from {FILE_PATH}...")
    try:
        df = pd.read_excel(FILE_PATH)
    except FileNotFoundError:
        print(f"Error: The file was not found at {FILE_PATH}")
        print("Please make sure the 'Online Retail.xlsx' file is in the 'data' directory.")
        return

    print(f"   - Extracted {len(df)} rows.")

    # --- Light Transformation (in Pandas before loading) ---
    # --- Light Transformation (in Pandas before loading) ---
    print("2. Performing initial data cleaning...")
    # Clean column names to be database-friendly
    df = clean_column_names(df)
    # Remove rows where CustomerID is null, as they are not useful for customer analytics
    df.dropna(subset=['CUSTOMERID'], inplace=True)

    # Convert columns to their correct, explicit types
    df['INVOICENO'] = df['INVOICENO'].astype(str)
    df['STOCKCODE'] = df['STOCKCODE'].astype(str)
    df['CUSTOMERID'] = df['CUSTOMERID'].astype(int)

    print(f"   - {len(df)} rows remaining after cleaning.")

    # --- LOAD ---
    print("3. Loading data into Snowflake...")
    try:
        with snowflake.connector.connect(
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                account=SNOWFLAKE_ACCOUNT,
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA
        ) as conn:
            print("   - Snowflake connection successful.")

            # Use write_pandas to efficiently load the DataFrame
            # It handles table creation and data insertion
            success, nchunks, nrows, _ = write_pandas(
                conn,
                df,
                table_name=RAW_TABLE_NAME,
                auto_create_table=True,  # Automatically create the table
                overwrite=True  # Overwrite the table if it already exists
            )
            print(f"   - Successfully loaded {nrows} rows into '{RAW_TABLE_NAME}'.")

    except Exception as e:
        print(f"An error occurred during Snowflake connection or loading: {e}")
        return

    print("EL process complete!")


if __name__ == "__main__":
    main()
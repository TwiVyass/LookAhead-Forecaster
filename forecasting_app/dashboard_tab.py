# forecasting_app/dashboard_tab.py

import streamlit as st
import pandas as pd
import snowflake.connector
import os
import altair as alt


# --- Snowflake Connection (same as your other scripts) ---
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def fetch_dashboard_data():
    """Fetches the clean data from Snowflake for the dashboard."""
    try:
        with snowflake.connector.connect(
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                warehouse="COMPUTE_WH",
                database="ECOMMERCE_DB",
                schema="ANALYTICS"
        ) as conn:
            query = "SELECT * FROM SALES_CLEANED;"
            df = pd.read_sql(query, conn)
            # Basic data type conversion
            df['TOTAL_PRICE'] = pd.to_numeric(df['TOTAL_PRICE'])
            df['INVOICE_TIMESTAMP'] = pd.to_datetime(df['INVOICE_TIMESTAMP'])
            return df
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {e}")
        return pd.DataFrame()  # Return empty dataframe on error


def show_dashboard():
    """Renders the main dashboard page."""
    st.subheader("Live E-Commerce Performance Dashboard")
    st.markdown("---")

    df = fetch_dashboard_data()

    if df.empty:
        st.warning("Could not load dashboard data from Snowflake.")
        return

    # --- 1. Slicers / Filters ---
    st.sidebar.header("Dashboard Filters")

    # Country Multi-select Filter
    all_countries = df['COUNTRY'].unique()
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=all_countries,
        default=['United Kingdom', 'Germany', 'France']  # Sensible defaults
    )

    # Date Range Filter
    min_date = df['INVOICE_TIMESTAMP'].min().date()
    max_date = df['INVOICE_TIMESTAMP'].max().date()
    selected_date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Apply filters to the dataframe
    if selected_countries:
        df_filtered = df[df['COUNTRY'].isin(selected_countries)]
    else:
        # If no country is selected, use the whole dataframe
        df_filtered = df.copy()

    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        df_filtered = df_filtered[
            (df_filtered['INVOICE_TIMESTAMP'].dt.date >= start_date) &
            (df_filtered['INVOICE_TIMESTAMP'].dt.date <= end_date)
            ]

    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
        return

    # --- 2. KPI Metrics ---
    col1, col2, col3 = st.columns(3)

    total_revenue = df_filtered['TOTAL_PRICE'].sum()
    total_orders = df_filtered['INVOICENO'].nunique()
    unique_customers = df_filtered['CUSTOMERID'].nunique()

    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Unique Customers", f"{unique_customers:,}")

    st.markdown("---")

    # --- 3. Charts ---
    c1, c2 = st.columns((5, 5))  # Create two columns of equal width

    with c1:
        # Revenue by Country (Bar Chart)
        st.subheader("Revenue by Country")
        country_revenue = df_filtered.groupby('COUNTRY')['TOTAL_PRICE'].sum().sort_values(ascending=False).reset_index()

        bar_chart = alt.Chart(country_revenue).mark_bar().encode(
            x=alt.X('TOTAL_PRICE:Q', title='Total Revenue ($)'),
            y=alt.Y('COUNTRY:N', sort='-x', title='Country'),
            tooltip=['COUNTRY', 'TOTAL_PRICE:Q']
        ).interactive()
        st.altair_chart(bar_chart, use_container_width=True)

    with c2:
        # Revenue Over Time (Line Chart)
        st.subheader("Revenue Over Time")
        df_filtered['date'] = df_filtered['INVOICE_TIMESTAMP'].dt.to_period('W').apply(lambda r: r.start_time).dt.date
        time_series_revenue = df_filtered.groupby('date')['TOTAL_PRICE'].sum().reset_index()

        line_chart = alt.Chart(time_series_revenue).mark_line(point=True).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('TOTAL_PRICE:Q', title='Total Revenue ($)'),
            tooltip=['date:T', 'TOTAL_PRICE:Q']
        ).interactive()
        st.altair_chart(line_chart, use_container_width=True)

    st.markdown("---")

    # --- 4. Top Products Table ---
    st.subheader("Top Selling Products")
    top_products = df_filtered.groupby('DESCRIPTION')['TOTAL_PRICE'].sum().sort_values(ascending=False).head(
        10).reset_index()
    top_products.rename(columns={'DESCRIPTION': 'Product', 'TOTAL_PRICE': 'Total Revenue'}, inplace=True)
    top_products['Total Revenue'] = top_products['Total Revenue'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(top_products, use_container_width=True, hide_index=True)
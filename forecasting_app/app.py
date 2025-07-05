# forecasting_app/app.py

import streamlit as st
import joblib
import pandas as pd
from datetime import timedelta
import altair as alt

# --- Page Configuration ---
st.set_page_config(
    page_title="LookAhead - Sales Forecaster",
    layout="wide"
)


# ==============================================================================
# DATA LOADING (Done ONCE for the whole app)
# ==============================================================================
@st.cache_resource
def load_model(model_path):
    """Loads the saved SARIMA model."""
    try:
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        st.error(f"Model file not found at {model_path}. Please run train_model.py first.")
        return None


# Load the model which contains our data
model_results = load_model("sarima_model.pkl")

# Prepare the historical data from the model for both tabs
if model_results:
    historical_data = pd.Series(
        model_results.model.endog.flatten(),
        index=model_results.model.data.dates,
        name="TOTAL_PRICE"
    ).reset_index().rename(columns={'index': 'INVOICE_TIMESTAMP'})
else:
    historical_data = pd.DataFrame()

st.markdown("<h1 style='text-align: center;'>LookAhead - Sales Forecaster</h1>", unsafe_allow_html=True)
st.markdown("""
<div style="
    background-color: #40474A;
    padding: 25px 40px;
    border-radius: 15px;
    border: 1px solid #d3d3d3;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 20px;
">
    <h2>
        LookAhead demonstrates the construction of a robust, scalable, and automated data system.
    </h2>
    <p>
        The UCI dataset provides a perfect real-world sandbox:
        <ul style='text-align: left; display: inline-block;'>
            <li><strong>Sufficient Scale:</strong> Over 500,000 records to justify a cloud data warehouse.</li>
            <li><strong>Realistic Data Quality:</strong> Contains missing values, cancellations, and inconsistent types that require a robust data cleaning and transformation stage.</li>
            <li><strong>Clear Business Patterns:</strong> Exhibits strong seasonality, making it ideal for time-series forecasting.</li>
        </ul>
    </p>
    <p>
        This project focuses on the <strong>timeless process</strong> of building a data-driven system, showcasing how to engineer a solution that moves an organization from reactive reporting to proactive, AI-supported strategic planning.
    </p>
</div>
""", unsafe_allow_html=True)
# --- Create Tabs ---
tab1, tab2 = st.tabs([" Sales Forecaster", " Performance Dashboard"])

# ==============================================================================
# TAB 1: FORECASTER
# ==============================================================================
with tab1:
    st.header("Future Sales Forecasting")
    if model_results:
        st.sidebar.header("Forecasting Options")
        forecast_days = st.sidebar.slider(
            "Select number of days to forecast:",
            min_value=7, max_value=180, value=30, key="forecast_slider"
        )
        if st.sidebar.button("Generate Forecast"):
            with st.spinner("Generating forecast..."):
                last_date = model_results.model.data.dates[-1]
                forecast = model_results.get_forecast(steps=forecast_days)
                forecast_df = pd.DataFrame({
                    'date': pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days),
                    'predicted_sales': forecast.predicted_mean
                }).set_index('date')

                st.subheader(f"Sales Forecast for the Next {forecast_days} Days")

                # We use the pre-loaded historical data
                chart_data = historical_data.set_index('INVOICE_TIMESTAMP')
                st.line_chart(pd.concat([chart_data['TOTAL_PRICE'].tail(90), forecast_df['predicted_sales']]))

                st.subheader("Forecasted Sales Data")
                display_df = forecast_df.copy()
                display_df['predicted_sales'] = display_df['predicted_sales'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(display_df)
    else:
        st.warning("Model has not been trained. Cannot run the application.")

# ==============================================================================
# TAB 2: PERFORMANCE DASHBOARD (using ONLY pre-loaded data)
# ==============================================================================
with tab2:
    st.header("Historical Performance Dashboard")
    st.markdown("This dashboard visualizes the historical data used to train the forecasting model.")

    if not historical_data.empty:
        # --- FILTERS in the main panel for simplicity ---
        st.markdown("#### Filter the historical data:")

        # Date Range Filter
        min_date = historical_data['INVOICE_TIMESTAMP'].min().date()
        max_date = historical_data['INVOICE_TIMESTAMP'].max().date()

        selected_date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="dashboard_date_filter"
        )

        # Apply date filter
        if len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
            df_filtered = historical_data[
                (historical_data['INVOICE_TIMESTAMP'].dt.date >= start_date) &
                (historical_data['INVOICE_TIMESTAMP'].dt.date <= end_date)
                ]

            if df_filtered.empty:
                st.warning("No data available for the selected date range.")
            else:
                # --- KPI Metrics ---
                st.markdown("---")
                total_revenue = df_filtered['TOTAL_PRICE'].sum()
                total_days_with_sales = df_filtered[df_filtered['TOTAL_PRICE'] > 0]['INVOICE_TIMESTAMP'].nunique()

                col1, col2 = st.columns(2)
                col1.metric("Total Revenue", f"${total_revenue:,.2f}")
                col2.metric("Days with Sales", f"{total_days_with_sales}")
                st.markdown("---")

                # --- Revenue Over Time Chart ---
                st.subheader("Revenue Over Time")
                line_chart = alt.Chart(df_filtered).mark_line(point=True).encode(
                    x=alt.X('INVOICE_TIMESTAMP:T', title='Date'),
                    y=alt.Y('TOTAL_PRICE:Q', title='Total Revenue ($)'),
                    tooltip=['INVOICE_TIMESTAMP:T', 'TOTAL_PRICE:Q']
                ).interactive()
                st.altair_chart(line_chart, use_container_width=True)
    else:
        st.warning("Model data not loaded. Cannot display dashboard.")
"""
Main Streamlit application for the Activation Dashboard.

This is the entry point for running the dashboard locally.
Run with: streamlit run app.py
"""
import streamlit as st
import pandas as pd
from styles import apply_styles, CHART_DEFINITIONS, ACTIVATION_METRICS, JOURNEY_METRICS, PAID_MEDIA_METRICS, CONNECTOR_METRICS, AMPS_METRICS
from data_processing import fetch_all_dashboard_data, transform_dashboard_data, process_journey_stats_data, process_new_journey_tenants, extract_raw_values
from components import (
    create_activation_tile, create_journey_tile, create_paid_media_tile,
    create_connectors_tile, get_amps_snippet_html, create_metric_chart,
    generate_historical_metrics_tiles, display_new_journey_tenants_table
)

# Set page configuration
st.set_page_config(
    page_title="Activation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styles
apply_styles(st)

# Main title
st.markdown('<h1 class="main-title">Activation Dashboard</h1>', unsafe_allow_html=True)

# Fetch all dashboard data
try:
    with st.spinner('Loading dashboard data from Snowflake...'):
        data = fetch_all_dashboard_data()

    if data is None:
        st.error("Unable to load dashboard data. Please check your Snowflake connection.")
        st.stop()

    df_amps, df_sql_result, df_journey_stats, df_new_journey_tenants, unique_journey_tenants = data

    # Transform the main dashboard data
    df_pivoted, df_pivoted_latest, dynamic_trend_indicators = transform_dashboard_data(df_sql_result)

    # Get the latest week's data
    latest_week = df_pivoted_latest.iloc[0]
    latest_week_index = df_pivoted[df_pivoted['Week Ending'] == latest_week['Week Ending']].index[0]

    # Format the week ending date
    week_ending_str = latest_week['Week Ending'].strftime("%b %d, %Y")
    st.markdown(f'<h2 class="sub-title">Week Ending {week_ending_str}</h2>', unsafe_allow_html=True)

    # Create the featured metrics tiles
    st.markdown("### Current Week Metrics")

    # Get AMPS snippets for activation and journey tiles
    activation_amps_html = get_amps_snippet_html(df_amps, "Activation")
    journey_amps_html = get_amps_snippet_html(df_amps, "Journeys")

    # Get total journeys run to date
    total_journeys_run = None
    if not df_journey_stats.empty:
        processed_stats = process_journey_stats_data(df_journey_stats)
        if not processed_stats.empty:
            total_journeys_run = int(processed_stats.iloc[0]['total_journeys'])

    # Create 4 columns for the main tiles
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        activation_html = create_activation_tile(latest_week, latest_week_index, dynamic_trend_indicators, activation_amps_html)
        st.markdown(activation_html, unsafe_allow_html=True)

    with col2:
        journey_html = create_journey_tile(latest_week, latest_week_index, dynamic_trend_indicators, journey_amps_html, unique_journey_tenants, total_journeys_run)
        st.markdown(journey_html, unsafe_allow_html=True)

    with col3:
        paid_media_html = create_paid_media_tile(latest_week, latest_week_index, dynamic_trend_indicators)
        st.markdown(paid_media_html, unsafe_allow_html=True)

    with col4:
        connectors_html = create_connectors_tile(latest_week, latest_week_index, dynamic_trend_indicators)
        st.markdown(connectors_html, unsafe_allow_html=True)

    # Historical Metrics Section
    st.markdown("---")
    st.markdown("### Historical Metrics")

    # Activation metrics
    st.markdown("#### Activation")
    generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, ACTIVATION_METRICS)

    # Journey metrics
    st.markdown("#### Journey")
    generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, JOURNEY_METRICS)

    # Paid Media metrics
    st.markdown("#### Paid Media")
    generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, PAID_MEDIA_METRICS)

    # Connector metrics
    st.markdown("#### Connectors")
    generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, CONNECTOR_METRICS)

    # AMPS metrics
    st.markdown("#### AMPS Consumption")
    generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, AMPS_METRICS)

    # Charts Section
    st.markdown("---")
    st.markdown("### Trend Charts")

    # Extract raw values for charts
    numeric_cols = [
        'Campaign & Segment Sends', 'Campaign & Segment Rows Sent', 'Total Sends', 'CS Tenants', 'Rows Sent',
        'Journeys', 'Journey Clients', 'Journey Adoption',
        'Paid Media Tenants', 'Paid Media Sends', 'Paid Media Rows', 'Paid Media %',
        'All Connectors', 'API Connectors', 'Bulk Storage Connectors', 'Source Connectors',
        'Destination Connectors',
        'Amps - Total', 'Amps - Activation', 'Amps - Campaigns', 'Amps - Journeys',
        'Amps - Orchestration', 'Amps - Profile API'
    ]

    raw_data, display_values, formatted_dates = extract_raw_values(df_pivoted, numeric_cols)

    # Create charts for each category
    for category_name, config in CHART_DEFINITIONS.items():
        chart = create_metric_chart(
            formatted_dates,
            raw_data,
            display_values,
            config["metrics"],
            config["title"],
            config["colors"],
            config.get("display_names", None)
        )

        if chart:
            st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
            st.altair_chart(chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Journey Details Section
    st.markdown("---")
    st.markdown("### Journey Details by Week")

    if not df_new_journey_tenants.empty:
        processed_journey_tenants = process_new_journey_tenants(df_new_journey_tenants)
        display_new_journey_tenants_table(processed_journey_tenants)
    else:
        st.info("No journey tenant data available.")

except Exception as e:
    st.error(f"An error occurred while loading the dashboard: {str(e)}")
    st.exception(e)

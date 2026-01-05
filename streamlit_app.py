"""
Activation Weekly Metrics Dashboard

This is the main entry point for the Streamlit dashboard app that displays
activation performance metrics.
"""
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Import our modules
import utils
import styles
import queries
import data_processing

# Import component functions directly (avoiding circular imports)
from components import (get_amps_snippet_html, create_activation_tile,
                      create_journey_tile, create_paid_media_tile,
                      create_connectors_tile, create_metric_chart,
                      generate_historical_metrics_tiles,
                      display_journey_weekly_stats,
                      display_new_journey_tenants_table)

# --- 0. Streamlit Page Configuration ---
st.set_page_config(layout="wide", page_title="Activation Weekly Metrics")

# Apply styles
styles.apply_styles(st)

# Page header
st.markdown("<h1 class='main-title'>Activation Weekly Metrics</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Key insights into our activation performance</p>", unsafe_allow_html=True)

# --- 1. Data Retrieval ---
data_result = data_processing.fetch_all_dashboard_data()

if data_result is None:
    st.error("❌ Failed to retrieve data from Snowflake")
    st.stop()

df_amps, df_sql_result, df_journey_stats, df_new_journey_tenants, unique_journey_tenants = data_result

# --- 2. Data Transformation ---
df_pivoted, df_pivoted_latest, dynamic_trend_indicators = data_processing.transform_dashboard_data(df_sql_result)

# Process the journey statistics data
df_journey_stats_processed = data_processing.process_journey_stats_data(df_journey_stats)
df_new_journey_tenants_processed = data_processing.process_new_journey_tenants(df_new_journey_tenants)

# --- 3. List of columns we track trends for ---
numeric_cols_for_trend = [
    'Campaign & Segment Sends', 'Rows Sent', 'Paid Media Tenants',
    'Paid Media Sends', 'Paid Media Rows', 'Journeys', 'Journey Clients', 'Journey Adoption',
    'Total Sends', 'All Tenants', 'Campaign & Segment %', 'Paid Media %', 'CS Tenants', 'CS Tenants Percent',
    'Campaign & Segment Rows Sent', 'All Connectors', 'API Connectors', 'Bulk Storage Connectors',
    'Source Connectors', 'Destination Connectors',
    'Amps - Total', 'Amps - Activation', 'Amps - Campaigns', 'Amps - Journeys', 'Amps - Orchestration', 'Amps - Profile API'
]

# --- 4. Main Dashboard Rendering ---
if not df_pivoted.empty:
    latest_week = df_pivoted_latest.iloc[0]
    latest_week_str = latest_week['Week Ending'].strftime("%b %d, %Y")
    latest_week_index = df_pivoted[df_pivoted['Week Ending'] == latest_week['Week Ending']].index[0]

    st.markdown(f"<p class='tile-title'>Week Ending {latest_week_str}</p>", unsafe_allow_html=True)

    # --- PREPARE AMPS DATA FOR INDIVIDUAL TILES ---
    activation_amps_html = get_amps_snippet_html(df_amps, 'Activation')
    journey_amps_html = get_amps_snippet_html(df_amps, 'Journeys')

    # Create 4 columns for the tiles
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # --- ACTIVATION TILE ---
        activation_tile_html = create_activation_tile(
            latest_week, latest_week_index, dynamic_trend_indicators, activation_amps_html
        )
        st.markdown(activation_tile_html, unsafe_allow_html=True)

    with col2:
        # --- JOURNEY TILE ---
        # Use the value from data_processing
        tenants_with_journey = unique_journey_tenants  # Should be 26 from data_processing

        # Calculate total journeys run to date (sum of all Journeys_NUM)
        total_journeys_run = 0
        if 'Journeys_NUM' in df_pivoted.columns:
            # Only sum non-NA values
            total_journeys_run = int(df_pivoted['Journeys_NUM'].fillna(0).sum())

        journey_tile_html = create_journey_tile(
            latest_week, latest_week_index, dynamic_trend_indicators, journey_amps_html,
            tenants_with_journey, total_journeys_run
        )
        st.markdown(journey_tile_html, unsafe_allow_html=True)

    with col3:
        # --- PAID MEDIA TILE ---
        paid_media_tile_html = create_paid_media_tile(
            latest_week, latest_week_index, dynamic_trend_indicators
        )
        st.markdown(paid_media_tile_html, unsafe_allow_html=True)

    with col4:
        # --- CONNECTORS TILE ---
        connectors_tile_html = create_connectors_tile(
            latest_week, latest_week_index, dynamic_trend_indicators
        )
        st.markdown(connectors_tile_html, unsafe_allow_html=True)

    # --- 5. Historical Data Section ---
    st.markdown("---")

    # Create two top-level tabs for Weekly and Monthly views
    main_tab_weekly, main_tab_monthly = st.tabs(["Weekly", "Monthly"])

    # ========== WEEKLY TAB ==========
    with main_tab_weekly:
        st.subheader("Historical Weekly Data")

        # Extract raw values for charts
        raw_values, display_values, dates = data_processing.extract_raw_values(df_pivoted, numeric_cols_for_trend)

        # Create tabs for different metric categories
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Activation", "Journey", "Paid Media", "Connectors", "Amps"])

        with tab1:
            st.subheader("Activation Historical Metrics")
            generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, styles.ACTIVATION_METRICS)
            st.subheader("Activation Metrics Trend")
            activation_chart = create_metric_chart(
                dates,
                raw_values,
                display_values,
                styles.CHART_DEFINITIONS["activation"]["metrics"],
                styles.CHART_DEFINITIONS["activation"]["title"],
                styles.CHART_DEFINITIONS["activation"]["colors"],
                styles.CHART_DEFINITIONS["activation"].get("display_names", {})
            )
            if activation_chart:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(activation_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            # Display journey statistics at the top
            st.subheader("Journey Stats")
            journey_amps_data = df_amps[df_amps['CATEGORY'] == 'Journeys']

            # Calculate total journeys created to date
            total_journeys_created = 0
            if not df_journey_stats_processed.empty:
                total_journeys_created = int(df_journey_stats_processed.iloc[0]['total_journeys'])

            # Calculate total journeys run to date (from Journey Adoption metric)
            latest_week = df_pivoted_latest.iloc[0]
            total_journeys_run = 0
            all_journeys_run = df_pivoted['Journeys_NUM'].fillna(0).sum() if 'Journeys_NUM' in df_pivoted.columns else 0

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                # Journey amps
                if not journey_amps_data.empty:
                    journey_amps_row = journey_amps_data.iloc[0]
                    amps_val = journey_amps_row.get('AMPS', 'N/A')
                    delta_val = journey_amps_row.get('DELTA')
                    delta_color = "normal"
                    delta_text = None
                    if not pd.isna(delta_val):
                        if delta_val < 0:  # negative DELTA means increase in consumption
                            delta_color = "normal"  # Shows green up arrow for increase in consumption
                            delta_text = f"+{abs(delta_val):.1f}%"
                        elif delta_val > 0:
                            delta_color = "inverse"  # Shows red down arrow for decrease in consumption
                            delta_text = f"-{abs(delta_val):.1f}%"
                    st.metric("Journey Amps", amps_val, delta=delta_text, delta_color=delta_color)

            with col2:
                # Tenants who have created a journey
                if not df_journey_stats_processed.empty:
                    tenant_count = int(df_journey_stats_processed.iloc[0]['unique_tenants'])
                    st.metric("Tenants with Journeys", tenant_count)

            with col3:
                # Total journeys created to date
                st.metric("Total Journeys Created", utils.format_large_number(total_journeys_created))

            with col4:
                # Journey runs this week
                journeys_val = utils.format_large_number(latest_week.get('Journeys', 'N/A'))
                st.metric("Journeys Run This Week", journeys_val)

            with col5:
                # Total journeys run to date
                st.metric("Total Journeys Run", utils.format_large_number(all_journeys_run))

            # Display other journey metrics
            st.markdown("---")

            st.subheader("Journey Historical Metrics")
            generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, styles.JOURNEY_METRICS)
            st.subheader("Journey Metrics Trend")
            journey_chart = create_metric_chart(
                dates,
                raw_values,
                display_values,
                styles.CHART_DEFINITIONS["journey"]["metrics"],
                styles.CHART_DEFINITIONS["journey"]["title"],
                styles.CHART_DEFINITIONS["journey"]["colors"],
                styles.CHART_DEFINITIONS["journey"].get("display_names", {})
            )
            if journey_chart:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(journey_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Add the new journey tenants table at the bottom
            st.markdown("---")
            st.subheader("New Journey Tenants by Week")
            display_new_journey_tenants_table(df_new_journey_tenants_processed)

        with tab3:
            st.subheader("Paid Media Historical Metrics")
            generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, styles.PAID_MEDIA_METRICS)
            st.subheader("Paid Media Metrics Trend")
            paid_media_chart = create_metric_chart(
                dates,
                raw_values,
                display_values,
                styles.CHART_DEFINITIONS["paid_media"]["metrics"],
                styles.CHART_DEFINITIONS["paid_media"]["title"],
                styles.CHART_DEFINITIONS["paid_media"]["colors"],
                styles.CHART_DEFINITIONS["paid_media"].get("display_names", {})
            )
            if paid_media_chart:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(paid_media_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            st.subheader("Connector Historical Metrics")
            generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, styles.CONNECTOR_METRICS)
            st.subheader("Connector Metrics Trend")
            connector_chart = create_metric_chart(
                dates,
                raw_values,
                display_values,
                styles.CHART_DEFINITIONS["connector"]["metrics"],
                styles.CHART_DEFINITIONS["connector"]["title"],
                styles.CHART_DEFINITIONS["connector"]["colors"],
                styles.CHART_DEFINITIONS["connector"].get("display_names", {})
            )
            if connector_chart:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(connector_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Unable to create connector metrics chart.")

        with tab5:
            st.subheader("Amps Historical Metrics")
            generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, styles.AMPS_METRICS)
            st.subheader("Amps Consumption Trend")
            amps_chart = create_metric_chart(
                dates,
                raw_values,
                display_values,
                styles.CHART_DEFINITIONS["amps"]["metrics"],
                styles.CHART_DEFINITIONS["amps"]["title"],
                styles.CHART_DEFINITIONS["amps"]["colors"],
                styles.CHART_DEFINITIONS["amps"].get("display_names", {})
            )
            if amps_chart:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(amps_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Unable to create Amps metrics chart.")

    # ========== MONTHLY TAB ==========
    with main_tab_monthly:
        st.subheader("Historical Monthly Data")

        # Aggregate weekly data to monthly
        df_monthly, df_monthly_latest, monthly_trend_indicators = data_processing.aggregate_weekly_to_monthly(
            df_pivoted, dynamic_trend_indicators
        )

        # Extract raw values for monthly charts
        raw_values_monthly, display_values_monthly, dates_monthly = data_processing.extract_raw_values(
            df_monthly, numeric_cols_for_trend
        )

        # Create tabs for different metric categories
        tab1_m, tab2_m, tab3_m, tab4_m, tab5_m = st.tabs(["Activation", "Journey", "Paid Media", "Connectors", "Amps"])

        with tab1_m:
            st.subheader("Activation Historical Metrics (Monthly)")
            generate_historical_metrics_tiles(df_monthly, monthly_trend_indicators, styles.ACTIVATION_METRICS_MONTHLY)
            st.subheader("Activation Metrics Trend (Monthly)")
            activation_chart_monthly = create_metric_chart(
                dates_monthly,
                raw_values_monthly,
                display_values_monthly,
                styles.CHART_DEFINITIONS["activation"]["metrics"],
                styles.CHART_DEFINITIONS["activation"]["title"] + " (Monthly)",
                styles.CHART_DEFINITIONS["activation"]["colors"],
                styles.CHART_DEFINITIONS["activation"].get("display_names", {}),
                time_period="Month"
            )
            if activation_chart_monthly:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(activation_chart_monthly, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab2_m:
            st.subheader("Journey Historical Metrics (Monthly)")
            generate_historical_metrics_tiles(df_monthly, monthly_trend_indicators, styles.JOURNEY_METRICS_MONTHLY)
            st.subheader("Journey Metrics Trend (Monthly)")
            journey_chart_monthly = create_metric_chart(
                dates_monthly,
                raw_values_monthly,
                display_values_monthly,
                styles.CHART_DEFINITIONS["journey"]["metrics"],
                styles.CHART_DEFINITIONS["journey"]["title"] + " (Monthly)",
                styles.CHART_DEFINITIONS["journey"]["colors"],
                styles.CHART_DEFINITIONS["journey"].get("display_names", {}),
                time_period="Month"
            )
            if journey_chart_monthly:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(journey_chart_monthly, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            # Note: No "New Journey Tenants by Week" table for monthly view

        with tab3_m:
            st.subheader("Paid Media Historical Metrics (Monthly)")
            generate_historical_metrics_tiles(df_monthly, monthly_trend_indicators, styles.PAID_MEDIA_METRICS_MONTHLY)
            st.subheader("Paid Media Metrics Trend (Monthly)")
            paid_media_chart_monthly = create_metric_chart(
                dates_monthly,
                raw_values_monthly,
                display_values_monthly,
                styles.CHART_DEFINITIONS["paid_media"]["metrics"],
                styles.CHART_DEFINITIONS["paid_media"]["title"] + " (Monthly)",
                styles.CHART_DEFINITIONS["paid_media"]["colors"],
                styles.CHART_DEFINITIONS["paid_media"].get("display_names", {}),
                time_period="Month"
            )
            if paid_media_chart_monthly:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(paid_media_chart_monthly, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab4_m:
            st.subheader("Connector Historical Metrics (Monthly)")
            generate_historical_metrics_tiles(df_monthly, monthly_trend_indicators, styles.CONNECTOR_METRICS_MONTHLY)
            st.subheader("Connector Metrics Trend (Monthly)")
            connector_chart_monthly = create_metric_chart(
                dates_monthly,
                raw_values_monthly,
                display_values_monthly,
                ["Source Connectors", "Destination Connectors"],  # Only these two for monthly
                styles.CHART_DEFINITIONS["connector"]["title"] + " (Monthly)",
                styles.CHART_DEFINITIONS["connector"]["colors"],
                styles.CHART_DEFINITIONS["connector"].get("display_names", {}),
                time_period="Month"
            )
            if connector_chart_monthly:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(connector_chart_monthly, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Unable to create connector metrics chart.")

        with tab5_m:
            st.subheader("Amps Historical Metrics (Monthly)")
            generate_historical_metrics_tiles(df_monthly, monthly_trend_indicators, styles.AMPS_METRICS_MONTHLY)
            st.subheader("Amps Consumption Trend (Monthly)")
            amps_chart_monthly = create_metric_chart(
                dates_monthly,
                raw_values_monthly,
                display_values_monthly,
                styles.CHART_DEFINITIONS["amps"]["metrics"],
                styles.CHART_DEFINITIONS["amps"]["title"] + " (Monthly)",
                styles.CHART_DEFINITIONS["amps"]["colors"],
                styles.CHART_DEFINITIONS["amps"].get("display_names", {}),
                time_period="Month"
            )
            if amps_chart_monthly:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.altair_chart(amps_chart_monthly, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Unable to create Amps metrics chart.")
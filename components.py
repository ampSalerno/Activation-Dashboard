"""
UI components for the Activation Dashboard app.
"""
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from utils import format_large_number, get_arrow_html, normalize_for_display, parse_numeric_value

# Pre-define variables to avoid circular imports
df_amps = None


def create_activation_tile(latest_week, latest_week_index, dynamic_trend_indicators, activation_amps_html=""):
    """
    Create the Activation metrics tile.

    Args:
        latest_week: DataFrame row with the latest week's data
        latest_week_index: Index of the latest week in the data
        dynamic_trend_indicators: Dictionary of trend indicators
        activation_amps_html: HTML string for AMPS data (optional)

    Returns:
        HTML string for the tile
    """
    all_tenants_num = parse_numeric_value(latest_week.get('All Tenants'))
    cs_tenants_val = format_large_number(latest_week.get('CS Tenants', 'N/A'))
    cs_tenants_arrow = dynamic_trend_indicators.get('CS Tenants', ['→'])[latest_week_index]
    cs_tenants_arrow_html = get_arrow_html(cs_tenants_arrow)
    cs_tenants_percent = latest_week.get('CS Tenants Percent', 'N/A')
    cs_sends_val = format_large_number(latest_week.get('Campaign & Segment Sends', 'N/A'))
    cs_sends_arrow = dynamic_trend_indicators.get('Campaign & Segment Sends', ['→'])[latest_week_index]
    cs_sends_arrow_html = get_arrow_html(cs_sends_arrow)
    cs_rows_sent_val = format_large_number(latest_week.get('Campaign & Segment Rows Sent', 'N/A'))
    cs_rows_sent_arrow = dynamic_trend_indicators.get('Campaign & Segment Rows Sent', ['→'])[latest_week_index]
    cs_rows_sent_arrow_html = get_arrow_html(cs_rows_sent_arrow)
    total_rows_sent_val = format_large_number(latest_week.get('Rows Sent', 'N/A'))

    html_parts = [
        "<div class='metric-box'>",
        "<div class='metric-name'>ACTIVATION</div>",
        activation_amps_html,
        f"<div class='metric-row'><div class='metric-label-new'>Tenants with Campaign/Segment Sends</div><div class='metric-value-wrapper'><div class='metric-arrow'>{cs_tenants_arrow_html}</div><div class='metric-value-main'>{cs_tenants_val}</div><div class='metric-parenthetical'>({cs_tenants_percent} of all tenants)</div></div></div>",
        f"<div class='metric-row'><div class='metric-label-new'>Campaign & Segment Sends</div><div class='metric-value-wrapper'><div class='metric-arrow'>{cs_sends_arrow_html}</div><div class='metric-value-main'>{cs_sends_val}</div></div></div>",
        f"<div class='metric-row'><div class='metric-label-new'>Campaign & Segment Rows Sent</div><div class='metric-value-wrapper'><div class='metric-arrow'>{cs_rows_sent_arrow_html}</div><div class='metric-value-main'>{cs_rows_sent_val}</div><div class='metric-parenthetical'>({total_rows_sent_val} total rows)</div></div></div>",
        "</div>"
    ]
    return "".join(html_parts)


def create_journey_tile(latest_week, latest_week_index, dynamic_trend_indicators, journey_amps_html="", tenants_with_journey=None, total_journeys_run=None):
    """
    Create the Journey metrics tile.

    Args:
        latest_week: DataFrame row with the latest week's data
        latest_week_index: Index of the latest week in the data
        dynamic_trend_indicators: Dictionary of trend indicators
        journey_amps_html: HTML string for AMPS data (optional)
        tenants_with_journey: Number of tenants that created a journey to date (optional)
        total_journeys_run: Total number of journeys run to date (optional)

    Returns:
        HTML string for the tile
    """
    all_tenants_num = parse_numeric_value(latest_week.get('All Tenants'))
    journeys_val = format_large_number(latest_week.get('Journeys', 'N/A'))
    journeys_arrow = dynamic_trend_indicators.get('Journeys', ['→'])[latest_week_index]
    journeys_arrow_html = get_arrow_html(journeys_arrow)
    # Removed Tasks reference

    journey_adoption_val = format_large_number(latest_week.get('Journey Adoption', 'N/A'))
    journey_adoption_arrow = dynamic_trend_indicators.get('Journey Adoption', ['→'])[latest_week_index]
    journey_adoption_arrow_html = get_arrow_html(journey_adoption_arrow)
    journey_adoption_num = parse_numeric_value(latest_week.get('Journey Adoption', 0))
    journey_adoption_percent = "N/A"
    if all_tenants_num and all_tenants_num > 0 and journey_adoption_num:
        journey_adoption_percent = f"{round((journey_adoption_num / all_tenants_num) * 100)}%"

    # Format metrics
    tenants_with_journey_str = format_large_number(tenants_with_journey) if tenants_with_journey is not None and tenants_with_journey > 0 else "N/A"

    # Same for total journeys run
    total_journeys_run_str = format_large_number(total_journeys_run) if total_journeys_run is not None and total_journeys_run > 0 else "N/A"

    html_parts = [
        "<div class='metric-box'>",
        "<div class='metric-name'>JOURNEY</div>",
        journey_amps_html,
        f"<div class='metric-row'><div class='metric-label-new'>Journey Runs (This Week)</div><div class='metric-value-wrapper'><div class='metric-arrow'>{journeys_arrow_html}</div><div class='metric-value-main'>{journeys_val}</div></div></div>",
        f"<div class='metric-row'><div class='metric-label-new'>Tenants with 1 or more Journey Runs</div><div class='metric-value-wrapper'><div class='metric-arrow'>{journey_adoption_arrow_html}</div><div class='metric-value-main'>{journey_adoption_val}</div><div class='metric-parenthetical'>({journey_adoption_percent} of all tenants)</div></div></div>",
        f"<div class='metric-row'><div class='metric-label-new'>Total Journeys Run (to Date)</div><div class='metric-value-wrapper'><div class='metric-value-main'>{total_journeys_run_str}</div></div></div>",
        f"<div class='metric-row'><div class='metric-label-new'>Tenants that Created a Journey (to Date)</div><div class='metric-value-wrapper'><div class='metric-value-main'>{tenants_with_journey_str}</div></div></div>",
        "</div>"
    ]
    return "".join(html_parts)


def create_paid_media_tile(latest_week, latest_week_index, dynamic_trend_indicators):
    """
    Create the Paid Media metrics tile.

    Args:
        latest_week: DataFrame row with the latest week's data
        latest_week_index: Index of the latest week in the data
        dynamic_trend_indicators: Dictionary of trend indicators

    Returns:
        HTML string for the tile
    """
    all_tenants_num = parse_numeric_value(latest_week.get('All Tenants'))
    paid_media_sends_val = format_large_number(latest_week.get('Paid Media Sends', 'N/A'))
    paid_media_sends_arrow = dynamic_trend_indicators.get('Paid Media Sends', ['→'])[latest_week_index]
    paid_media_sends_arrow_html = get_arrow_html(paid_media_sends_arrow)
    paid_media_rows_val = format_large_number(latest_week.get('Paid Media Rows', 'N/A'))
    paid_media_rows_arrow = dynamic_trend_indicators.get('Paid Media Rows', ['→'])[latest_week_index]
    paid_media_rows_arrow_html = get_arrow_html(paid_media_rows_arrow)
    paid_media_tenants_val = format_large_number(latest_week.get('Paid Media Tenants', 'N/A'))
    paid_media_tenants_arrow = dynamic_trend_indicators.get('Paid Media Tenants', ['→'])[latest_week_index]
    paid_media_tenants_arrow_html = get_arrow_html(paid_media_tenants_arrow)
    paid_media_tenants_num = parse_numeric_value(latest_week.get('Paid Media Tenants', 0))
    paid_media_tenants_percent = "N/A"
    if all_tenants_num and all_tenants_num > 0 and paid_media_tenants_num:
        paid_media_tenants_percent = f"{round((paid_media_tenants_num / all_tenants_num) * 100)}%"

    html_parts = [
        "<div class='metric-box'>",
        "<div class='metric-name'>PAID MEDIA</div>",
        f"<div class='metric-row'><div class='metric-label-new'>Tenants sending to a Paid Media Destination</div><div class='metric-value-wrapper'><div class='metric-arrow'>{paid_media_tenants_arrow_html}</div><div class='metric-value-main'>{paid_media_tenants_val}</div><div class='metric-parenthetical'>({paid_media_tenants_percent} of all tenants)</div></div></div>",
        f"<div class='metric-row'><div class='metric-label-new'>Sends to a Paid Media Destination</div><div class='metric-value-wrapper'><div class='metric-arrow'>{paid_media_sends_arrow_html}</div><div class='metric-value-main'>{paid_media_sends_val}</div><div class='metric-parenthetical'>({paid_media_rows_val} rows sent)</div></div></div>",
        "</div>"
    ]
    return "".join(html_parts)


def create_connectors_tile(latest_week, latest_week_index, dynamic_trend_indicators):
    """
    Create the Connectors metrics tile.

    Args:
        latest_week: DataFrame row with the latest week's data
        latest_week_index: Index of the latest week in the data
        dynamic_trend_indicators: Dictionary of trend indicators

    Returns:
        HTML string for the tile
    """
    all_connectors_val = latest_week.get('All Connectors', 'N/A')
    all_connectors_arrow = dynamic_trend_indicators.get('All Connectors', ['→'])[latest_week_index]
    all_connectors_arrow_html = get_arrow_html(all_connectors_arrow)
    api_connectors_val = latest_week.get('API Connectors', 'N/A')
    api_connectors_arrow = dynamic_trend_indicators.get('API Connectors', ['→'])[latest_week_index]
    api_connectors_arrow_html = get_arrow_html(api_connectors_arrow)
    bulk_storage_connectors_val = latest_week.get('Bulk Storage Connectors', 'N/A')
    bulk_connectors_arrow = dynamic_trend_indicators.get('Bulk Storage Connectors', ['→'])[latest_week_index]
    bulk_connectors_arrow_html = get_arrow_html(bulk_connectors_arrow)
    source_connectors_val = latest_week.get('Source Connectors', 'N/A')
    source_connectors_arrow = dynamic_trend_indicators.get('Source Connectors', ['→'])[latest_week_index]
    source_connectors_arrow_html = get_arrow_html(source_connectors_arrow)
    destination_connectors_val = latest_week.get('Destination Connectors', 'N/A')
    dest_connectors_arrow = dynamic_trend_indicators.get('Destination Connectors', ['→'])[latest_week_index]
    dest_connectors_arrow_html = get_arrow_html(dest_connectors_arrow)
    bi_directional_connectors_val = latest_week.get('Bi-Directional Connectors', 'N/A')
    bi_connectors_arrow = dynamic_trend_indicators.get('Bi-Directional Connectors', ['→'])[latest_week_index]
    bi_connectors_arrow_html = get_arrow_html(bi_connectors_arrow)

    html_parts = [
        "<div class='metric-box'>",
        "<div class='metric-name'>CONNECTORS</div>",
        f"<div class='metric-row'><div class='metric-label-new'>All Connectors</div><div class='metric-value-wrapper'><div class='metric-arrow'>{all_connectors_arrow_html}</div><div class='metric-value-main'>{all_connectors_val}</div></div></div>",
        "<table class='connector-table'>",
        f"<tr><td class='connector-trend'>{api_connectors_arrow_html}</td><td class='connector-name'>API Connectors</td><td class='connector-value' style='text-align: right'>{api_connectors_val}</td></tr>",
        f"<tr><td class='connector-trend'>{bulk_connectors_arrow_html}</td><td class='connector-name'>Bulk Storage Connectors</td><td class='connector-value' style='text-align: right'>{bulk_storage_connectors_val}</td></tr>",
        f"<tr><td class='connector-trend'>{source_connectors_arrow_html}</td><td class='connector-name'>Source Connectors</td><td class='connector-value' style='text-align: right'>{source_connectors_val}</td></tr>",
        f"<tr><td class='connector-trend'>{dest_connectors_arrow_html}</td><td class='connector-name'>Destination Connectors</td><td class='connector-value' style='text-align: right'>{destination_connectors_val}</td></tr>",
        f"<tr><td class='connector-trend'>{bi_connectors_arrow_html}</td><td class='connector-name'>Bi-Directional Connectors</td><td class='connector-value' style='text-align: right'>{bi_directional_connectors_val}</td></tr>",
        "</table>",
        "</div>"
    ]
    return "".join(html_parts)


def get_amps_snippet_html(df_amps, category_name):
    """
    Generate the HTML snippet for AMPS data.

    Args:
        df_amps: DataFrame with AMPS data
        category_name: Category name to filter by

    Returns:
        HTML string for the AMPS data
    """
    if df_amps is None or df_amps.empty:
        return ""

    amps_data = df_amps[df_amps['CATEGORY'] == category_name]
    if amps_data.empty:
        return ""

    amps_row = amps_data.iloc[0]
    # Apply formatting
    amps_formatted = format_large_number(amps_row['AMPS'])
    delta_val = amps_row.get('DELTA')

    trend_text = ""
    # A negative DELTA means an increase in consumption
    if not pd.isna(delta_val):
        if delta_val < 0:
            trend_text = f"(<span style='color:#10b981;'>▲ {abs(delta_val):.1f}%</span>)"
        elif delta_val > 0:
            trend_text = f"(<span style='color:#ef4444;'>▼ {abs(delta_val):.1f}%</span>)"

    # This HTML will be injected into the top of the respective tile
    return f"""
    <div class='metric-row' style='margin-bottom: 1.5rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 1rem;'>
        <div class='metric-label-new'>Amps</div>
        <div class='metric-value-wrapper'>
            <div class='metric-value-main' style='font-size: 2.2rem;'>{amps_formatted}</div>
            <div class='metric-parenthetical' style='font-weight: 500;'>{trend_text}</div>
        </div>
    </div>
    """


def create_metric_chart(dates, raw_values, display_values, metrics, title, colors, display_names=None):
    """
    Create a metric chart using Altair.

    Args:
        dates: List of formatted date strings
        raw_values: Dictionary mapping metric names to raw values
        display_values: Dictionary mapping metric names to display values
        metrics: List of metrics to include in the chart
        title: Chart title
        colors: List of colors to use
        display_names: Optional dictionary mapping metric names to display names

    Returns:
        Altair chart object or None if chart could not be created
    """
    chart_data = {"Week": dates}
    id_vars = ["Week"]
    available_metrics = []
    metric_display_names = {}

    # Use display_names dictionary if provided
    if display_names is None:
        display_names = {}

    for metric in metrics:
        if metric in raw_values and raw_values[metric]:
            values = raw_values[metric]
            disp_values = display_values.get(metric, [''] * len(dates))
            chart_data[metric] = normalize_for_display(values)
            chart_data[f"{metric}_display"] = disp_values
            id_vars.append(f"{metric}_display")
            available_metrics.append(metric)
            # Store the display name mapping
            metric_display_names[metric] = display_names.get(metric, metric)

    if available_metrics:
        import pandas as pd
        chart_df = pd.DataFrame(chart_data)
        chart_data_long = pd.melt(chart_df, id_vars=id_vars, value_vars=available_metrics, var_name="Metric", value_name="Value")
        chart_data_long["Display_Value"] = chart_data_long.apply(lambda row: row[f"{row['Metric']}_display"], axis=1)

        # Create a new column with the custom display names
        chart_data_long["Display_Name"] = chart_data_long["Metric"].map(lambda m: metric_display_names.get(m, m))

        line_chart = alt.Chart(chart_data_long).mark_line(
            strokeWidth=3, opacity=0.8, interpolate='linear'
        ).encode(
            x=alt.X('Week:N', title='Week', sort=None, axis=alt.Axis(labelAngle=45, labelFontSize=10)),
            y=alt.Y('Value:Q', title='', scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(labels=False)),
            color=alt.Color('Display_Name:N', scale=alt.Scale(domain=[metric_display_names.get(m, m) for m in available_metrics], range=colors[:len(available_metrics)]), legend=alt.Legend(orient='top', title=None, labelFontSize=12))
        )
        point_chart = alt.Chart(chart_data_long).mark_circle(size=60, opacity=1).encode(
            x=alt.X('Week:N', sort=None),
            y=alt.Y('Value:Q'),
            color=alt.Color('Display_Name:N', scale=alt.Scale(domain=[metric_display_names.get(m, m) for m in available_metrics], range=colors[:len(available_metrics)])),
            tooltip=[alt.Tooltip('Week:N', title='Week'), alt.Tooltip('Display_Name:N', title='Metric'), alt.Tooltip('Display_Value:N', title='Value')]
        )
        return (line_chart + point_chart).properties(height=300, autosize={'type': 'fit-x', 'contains': 'padding'})

    return None


def generate_historical_metrics_tiles(df_pivoted, dynamic_trend_indicators, metrics_config):
    """
    Generate historical metrics tiles.

    Args:
        df_pivoted: Pivoted DataFrame
        dynamic_trend_indicators: Dictionary of trend indicators
        metrics_config: List of metric configurations

    Returns:
        None - renders directly to Streamlit
    """
    num_columns_historical = 3
    cols_historical = st.columns(num_columns_historical)

    for i, metric_config in enumerate(metrics_config):
        with cols_historical[i % num_columns_historical]:
            metric_title = metric_config["title"]
            value_col = metric_config["value_col"]
            parenthetical_col = metric_config["parenthetical_col"]
            trend_col = metric_config["trend_col"]

            table_rows_html = ""
            rows = list(df_pivoted.sort_values(by='Week Ending', ascending=False).iterrows())

            for j, (index, row) in enumerate(rows):
                week_ending_str = row['Week Ending'].strftime("%b %d, %Y")
                current_value = format_large_number(row.get(value_col, 'N/A'))
                parenthetical_value_html = ""

                if parenthetical_col and parenthetical_col in row:
                    parenthetical_value = row.get(parenthetical_col, 'N/A')

                    # Format the parenthetical value if it's a number, but not if it's a percentage
                    if '%' not in str(parenthetical_value):
                        formatted_parenthetical = format_large_number(parenthetical_value)
                    else:
                        formatted_parenthetical = parenthetical_value

                    parenthetical_value_html = f'<div class="child-metric">({formatted_parenthetical})</div>'

                week_date = row['Week Ending']
                arrow_index = df_pivoted[df_pivoted['Week Ending'] == week_date].index.tolist()[0]
                arrow_indicator = dynamic_trend_indicators.get(trend_col, ['→'])[arrow_index]
                trend_arrow_html = get_arrow_html(arrow_indicator)
                table_rows_html += f'<tr><td class="metric-label">{week_ending_str}:</td><td class="metric-value"><div class="value-main">{current_value}</div><div class="trend-arrow">{trend_arrow_html}</div>{parenthetical_value_html}</td></tr>'

            tile_html = f'<div class="tile-container"><h4 class="tile-header">{metric_title}</h4><table class="metric-table">{table_rows_html}</table></div>'
            st.markdown(tile_html, unsafe_allow_html=True)


def display_journey_weekly_stats(df_journey_stats):
    """
    Display the weekly journey statistics.

    Args:
        df_journey_stats: DataFrame with weekly journey stats

    Returns:
        None - renders directly to Streamlit
    """
    if df_journey_stats.empty:
        st.warning("No journey statistics data available.")
        return

    # Display total tenants with journeys
    latest_week = df_journey_stats.iloc[0]
    st.metric("Total Tenants with Journeys", int(latest_week['unique_tenants']))
    st.metric("Total Journeys Created", int(latest_week['total_journeys']))


def display_new_journey_tenants_table(df_new_journey_tenants):
    """
    Display expandable sections of new tenants that created their first journey by week.
    Also shows tenants creating additional journeys and tenants with journey runs.

    Args:
        df_new_journey_tenants: DataFrame with new journey tenants data

    Returns:
        None - renders directly to Streamlit
    """
    if df_new_journey_tenants.empty:
        st.warning("No new journey tenants data available.")
        return

    # Make sure JOURNEY_RUNS_IN_WEEK is numeric and ensure we don't have NaN values
    if 'JOURNEY_RUNS_IN_WEEK' in df_new_journey_tenants.columns:
        df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'] = pd.to_numeric(
            df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'], errors='coerce').fillna(0).astype(int)

    # Print debugging info about available columns and data
    print(f"Available columns: {', '.join(df_new_journey_tenants.columns.tolist())}")

    # Show run data summary across all weeks
    if 'JOURNEY_RUNS_IN_WEEK' in df_new_journey_tenants.columns:
        print("\nOverall journey run stats:")
        run_stats = {
            'Total runs': int(df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'].sum()),
            'Tenants with runs > 0': (df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'] > 0).sum(),
            'Max runs for a tenant': int(df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'].max()),
            'Mean runs per tenant': float(df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'].mean())
        }
        print(run_stats)

    # Create an expandable section for each week
    # First get the unique activity weeks and sort them chronologically
    unique_weeks = df_new_journey_tenants['ACTIVITY_WEEK'].unique()
    unique_weeks = sorted(unique_weeks, reverse=True)  # Sort by actual datetime

    # Convert activity weeks to show week ending (Sunday) instead of week starting (Monday)
    weeks_with_dates = []
    for week_start in unique_weeks:
        # Calculate the Sunday (end of week) by adding 6 days to the Monday (start of week)
        week_end = week_start + pd.Timedelta(days=6)
        week_end_str = week_end.strftime('%b %d, %Y')
        weeks_with_dates.append((week_start, week_end_str))

    for week_start, week_end_str in weeks_with_dates:
        # Get data for this week using the actual datetime for filtering
        week_data = df_new_journey_tenants[df_new_journey_tenants['ACTIVITY_WEEK'] == week_start].copy()

        # Ensure run data is numeric
        if 'JOURNEY_RUNS_IN_WEEK' in week_data.columns:
            week_data['JOURNEY_RUNS_IN_WEEK'] = pd.to_numeric(week_data['JOURNEY_RUNS_IN_WEEK'], errors='coerce').fillna(0).astype(int)

        # Group data by tenant for each category
        first_time_creators = week_data[week_data['IS_ADDITIONAL'] == False]
        additional_creators = week_data[week_data['IS_ADDITIONAL'] == True]
        tenants_with_runs = week_data[week_data['JOURNEY_RUNS_IN_WEEK'] > 0] if 'JOURNEY_RUNS_IN_WEEK' in week_data.columns else pd.DataFrame()

        # Count unique tenants in each category
        first_time_count = len(first_time_creators['TENANT_NAME'].unique())
        additional_count = len(additional_creators['TENANT_NAME'].unique())
        run_count = len(tenants_with_runs['TENANT_NAME'].unique())

        # Create expander header
        # Calculate total runs for this week to include in header
        total_week_runs = int(week_data['JOURNEY_RUNS_IN_WEEK'].sum()) if 'JOURNEY_RUNS_IN_WEEK' in week_data.columns else 0
        expander_title = f"Week Ending {week_end_str} - {first_time_count} new tenants, {additional_count} with additional journeys, {run_count} tenants with {total_week_runs} journey runs"

        with st.expander(expander_title):
            if not week_data.empty:
                # Add title for clarity
                st.subheader(f"Journey Activity for Week Ending {week_end_str}")

                # Show summary statistics for journey runs
                if 'JOURNEY_RUNS_IN_WEEK' in week_data.columns:
                    total_runs = int(week_data['JOURNEY_RUNS_IN_WEEK'].sum())
                    tenants_with_runs_count = (week_data['JOURNEY_RUNS_IN_WEEK'] > 0).sum()

                    if total_runs > 0:
                        st.info(f"{tenants_with_runs_count} tenants ran journeys this week, with {total_runs} total journey runs.")

                # Create the new column-based display format
                # Get sorted lists of tenants for each category
                first_journey_tenants = sorted(first_time_creators['TENANT_NAME'].unique())
                additional_journey_tenants = sorted(additional_creators['TENANT_NAME'].unique())

                # For running journeys, get tenant names with run counts in parentheses
                running_journey_tenants = []
                for tenant_name in sorted(tenants_with_runs['TENANT_NAME'].unique()):
                    run_count = int(tenants_with_runs[tenants_with_runs['TENANT_NAME'] == tenant_name]['JOURNEY_RUNS_IN_WEEK'].max())
                    running_journey_tenants.append(f"{tenant_name} ({run_count})")

                # Determine the maximum length of the three lists to create a properly sized DataFrame
                max_length = max(len(first_journey_tenants), len(additional_journey_tenants), len(running_journey_tenants))

                # Create lists of equal length by padding with empty strings
                first_journey_column = first_journey_tenants + [''] * (max_length - len(first_journey_tenants))
                additional_journey_column = additional_journey_tenants + [''] * (max_length - len(additional_journey_tenants))
                running_journey_column = running_journey_tenants + [''] * (max_length - len(running_journey_tenants))

                # Create the display DataFrame with the three columns
                display_df = pd.DataFrame({
                    'First Time Journey Tenants': first_journey_column,
                    'Additional Journey Tenants': additional_journey_column,
                    'Tenants RUNNING Journeys': running_journey_column
                })

                # Display the table
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # Add a download button for this week's data
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label=f"Download Week Ending {week_end_str} Data",
                    data=csv,
                    file_name=f"journey_tenants_week_ending_{week_end_str.replace(' ', '_')}.csv",
                    mime="text/csv",
                )
            else:
                st.info("No journey creators or runs this week.")


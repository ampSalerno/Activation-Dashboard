"""
Data processing functions for the Activation Dashboard app.
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils import parse_numeric_value, calculate_trend_arrow
import queries

# Try to import Snowpark first (for Snowflake environment), fall back to connector (for local)
try:
    from snowflake.snowpark.context import get_active_session
    USE_SNOWPARK = True
except ImportError:
    USE_SNOWPARK = False
    import snowflake.connector
    from config import SNOWFLAKE_CONFIG


def get_snowflake_connection():
    """
    Get a Snowflake connection for local testing.
    Uses the snowflake-connector-python library with externalbrowser authentication.

    Returns:
        Snowflake connection object or None if an error occurs
    """
    try:
        conn = snowflake.connector.connect(
            account=SNOWFLAKE_CONFIG['account'],
            user=SNOWFLAKE_CONFIG['user'],
            authenticator='externalbrowser',
            warehouse=SNOWFLAKE_CONFIG.get('warehouse'),
            database=SNOWFLAKE_CONFIG.get('database'),
            schema=SNOWFLAKE_CONFIG.get('schema'),
            role=SNOWFLAKE_CONFIG.get('role')
        )
        return conn
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        return None


def get_snowflake_session():
    """
    Get the active Snowflake session.

    Returns:
        Snowflake session object or None if an error occurs
    """
    if not USE_SNOWPARK:
        return None
    try:
        return get_active_session()
    except Exception as e:
        st.error(f"Failed to get active Snowflake session: {e}. Ensure this app is run within a Snowflake environment.")
        return None


def execute_query_with_connection(conn, query):
    """
    Execute a SQL query using an existing connection.

    Args:
        conn: Existing Snowflake connection
        query: SQL query to execute

    Returns:
        Pandas DataFrame with the query results
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)

        # Fetch results as pandas DataFrame
        try:
            df = cursor.fetch_pandas_all()
        except Exception:
            # Fallback for queries that don't support pandas
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if cursor.description else []
            df = pd.DataFrame(results, columns=columns)

        cursor.close()
        return df
    except Exception as e:
        st.error(f"Error executing SQL query: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def execute_query(query):
    """
    Execute a SQL query and return results as a pandas DataFrame.
    Automatically detects whether to use Snowpark or snowflake-connector.

    Args:
        query: SQL query to execute

    Returns:
        Pandas DataFrame with the query results
    """
    try:
        if USE_SNOWPARK:
            # Running in Snowflake environment
            session = get_snowflake_session()
            if not session:
                return pd.DataFrame()
            df = session.sql(query).to_pandas()
        else:
            # Running locally - create connection just for this query
            conn = get_snowflake_connection()
            if not conn:
                return pd.DataFrame()

            df = execute_query_with_connection(conn, query)
            conn.close()

        return df
    except Exception as e:
        st.error(f"Error executing SQL query: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_amps_data(_session, query):
    """
    Retrieve AMPS data from Snowflake.

    Args:
        _session: Snowflake session object (prefixed with underscore to tell Streamlit not to hash it)
        query: SQL query to execute

    Returns:
        Pandas DataFrame with the query results
    """
    # Backward compatible: use execute_query which handles both modes
    return execute_query(query)


@st.cache_data(ttl=600)
def get_data_from_snowflake(_session, query):
    """
    Retrieve data from Snowflake with a generic query.

    Args:
        _session: Snowflake session object (prefixed with underscore to tell Streamlit not to hash it)
        query: SQL query to execute

    Returns:
        Pandas DataFrame with the query results
    """
    # Backward compatible: use execute_query which handles both modes
    return execute_query(query)


def fetch_all_dashboard_data():
    """
    Fetch all data needed for the dashboard.

    Returns:
        Tuple of (df_amps, df_sql_result, df_journey_stats, df_new_journey_tenants, unique_journey_tenants) or None if there was an error
    """
    # For Snowpark, get session once and reuse; for local, create one connection
    if USE_SNOWPARK:
        session = get_snowflake_session()
        if not session:
            st.error("Failed to get Snowflake session")
            return None
        # Session will be reused by the cached functions
        conn = None
    else:
        # Running locally - create ONE connection for all queries
        conn = get_snowflake_connection()
        if not conn:
            st.error("Failed to connect to Snowflake")
            return None
        session = None

    try:
        if USE_SNOWPARK:
            df_amps = get_amps_data(session, queries.AMPS_QUERY)
        else:
            df_amps = execute_query_with_connection(conn, queries.AMPS_QUERY)

        if USE_SNOWPARK:
            df_sql_result = get_data_from_snowflake(session, queries.MAIN_DASHBOARD_QUERY)
        else:
            df_sql_result = execute_query_with_connection(conn, queries.MAIN_DASHBOARD_QUERY)

        if USE_SNOWPARK:
            df_journey_stats = get_data_from_snowflake(session, queries.JOURNEY_WEEKLY_STATS_QUERY)
        else:
            df_journey_stats = execute_query_with_connection(conn, queries.JOURNEY_WEEKLY_STATS_QUERY)

        if USE_SNOWPARK:
            df_new_journey_tenants = get_data_from_snowflake(session, queries.NEW_JOURNEY_TENANTS_QUERY)
        else:
            df_new_journey_tenants = execute_query_with_connection(conn, queries.NEW_JOURNEY_TENANTS_QUERY)

        if USE_SNOWPARK:
            df_unique_journey_tenants = get_data_from_snowflake(session, queries.UNIQUE_JOURNEY_TENANTS_QUERY)
        else:
            df_unique_journey_tenants = execute_query_with_connection(conn, queries.UNIQUE_JOURNEY_TENANTS_QUERY)

        if df_sql_result.empty:
            st.warning("No data retrieved for the main dashboard. Please check your SQL query and Snowflake connection.")
            return None

        # Extract the unique journey tenants count
        unique_journey_tenants = 0  # Default value
        if not df_unique_journey_tenants.empty:
            # Get the first value from the first row (should be the count)
            unique_journey_tenants = int(df_unique_journey_tenants.iloc[0, 0])
        else:
            st.warning("Could not retrieve unique journey tenants count.")

        return df_amps, df_sql_result, df_journey_stats, df_new_journey_tenants, unique_journey_tenants

    finally:
        # Close connection if we created one
        if conn is not None:
            conn.close()


def transform_dashboard_data(df_sql_result):
    """
    Transform the raw dashboard data into a format suitable for display.

    Args:
        df_sql_result: Raw DataFrame from Snowflake

    Returns:
        Tuple of (df_pivoted, df_pivoted_latest, dynamic_trend_indicators)
    """
    # Metric mapping for consistent naming
    metric_mapping = {
        'Campaign & Segment Sends': 'Campaign & Segment Sends', 'Total Sends': 'Total Sends',
        'All Tenants': 'All Tenants', '% Campaign & Segment': 'Campaign & Segment %', 'Rows Sent': 'Rows Sent',
        'Paid Media Tenants': 'Paid Media Tenants', 'Paid Media Sends': 'Paid Media Sends', 'Paid Media Rows': 'Paid Media Rows',
        'Paid Media %': 'Paid Media %', 'Journey Adoption': 'Journey Adoption', 'Journeys': 'Journeys',
        'Journey Clients': 'Journey Clients',
        'Source Connectors': 'Source Connectors', 'Destination Connectors': 'Destination Connectors',
        'CS Tenants': 'CS Tenants',
        'CS Tenants Percent': 'CS Tenants Percent', 'Campaign & Segment Rows Sent': 'Campaign & Segment Rows Sent',
        'Amps - Total': 'Amps - Total', 'Amps - Activation': 'Amps - Activation', 'Amps - Campaigns': 'Amps - Campaigns',
        'Amps - Journeys': 'Amps - Journeys', 'Amps - Orchestration': 'Amps - Orchestration',
        'Amps - Profile API': 'Amps - Profile API'
    }

    # Pivot the data for easier access
    df_pivoted = df_sql_result.pivot_table(
        index='Week Ending',
        columns='Metric',
        values='Value',
        aggfunc='first'
    ).rename(columns=metric_mapping).reset_index()

    df_pivoted['Week Ending'] = pd.to_datetime(df_pivoted['Week Ending'])
    df_pivoted = df_pivoted.sort_values(by='Week Ending', ascending=True)
    df_pivoted_latest = df_pivoted.sort_values(by='Week Ending', ascending=False)

    # List of numeric columns for trend calculations
    numeric_cols_for_trend = [
        'Campaign & Segment Sends', 'Rows Sent', 'Paid Media Tenants',
        'Paid Media Sends', 'Paid Media Rows', 'Journeys', 'Journey Clients', 'Journey Adoption',
        'Total Sends', 'All Tenants', 'Campaign & Segment %', 'Paid Media %', 'CS Tenants', 'CS Tenants Percent',
        'Campaign & Segment Rows Sent', 'Source Connectors', 'Destination Connectors',
        'Amps - Total', 'Amps - Activation', 'Amps - Campaigns', 'Amps - Journeys', 'Amps - Orchestration',
        'Amps - Profile API'
    ]

    # Convert values to numeric for calculations
    for col in numeric_cols_for_trend:
        if col in df_pivoted.columns:
            df_pivoted[f'{col}_NUM'] = df_pivoted[col].apply(parse_numeric_value)
        else:
            st.warning(f"Warning: Column '{col}' not found in pivoted data. It will be treated as missing.")

    # Calculate trend indicators for each metric
    dynamic_trend_indicators = {}
    for col_name in numeric_cols_for_trend:
        if f'{col_name}_NUM' in df_pivoted.columns:
            trends = []
            for i in range(len(df_pivoted)):
                current_val = df_pivoted[f'{col_name}_NUM'].iloc[i]
                if i > 0:
                    previous_val = df_pivoted[f'{col_name}_NUM'].iloc[i-1]
                    trends.append(calculate_trend_arrow(current_val, previous_val))
                else:
                    trends.append("→")
            dynamic_trend_indicators[col_name] = trends
        else:
            dynamic_trend_indicators[col_name] = ["→"] * len(df_pivoted)

    return df_pivoted, df_pivoted_latest, dynamic_trend_indicators


def aggregate_weekly_to_monthly(df_pivoted, dynamic_trend_indicators):
    """
    Aggregate weekly data to monthly data.

    Args:
        df_pivoted: DataFrame with weekly data
        dynamic_trend_indicators: Dictionary of trend indicators for weekly data

    Returns:
        Tuple of (df_monthly, df_monthly_latest, monthly_trend_indicators)
    """
    if df_pivoted.empty:
        return pd.DataFrame(), pd.DataFrame(), {}

    # Create a copy and add month column
    df_monthly_prep = df_pivoted.copy()
    df_monthly_prep['Month'] = df_monthly_prep['Week Ending'].dt.to_period('M')

    # Get numeric columns (those with _NUM suffix from transform)
    numeric_cols = [col for col in df_monthly_prep.columns if col.endswith('_NUM')]

    # Identify point-in-time metrics (these should use 'last' not 'sum')
    # These represent state at a point in time, not cumulative counts
    point_in_time_keywords = ['Connector', 'Tenants', 'Adoption', 'Clients']
    point_in_time_cols = [col for col in numeric_cols if any(keyword in col for keyword in point_in_time_keywords)]

    # Group by month and aggregate
    agg_dict = {}
    for col in df_monthly_prep.columns:
        if col in ['Week Ending', 'Month']:
            continue
        elif col in point_in_time_cols:
            # For point-in-time metrics, use the last value of the month
            agg_dict[col] = 'last'
        elif col in numeric_cols:
            # Sum cumulative metrics (like sends, journeys run, rows sent, etc.)
            agg_dict[col] = 'sum'
        else:
            # For all display values (including percentages), take the last value of the month
            # We can't average string percentages like "50%"
            agg_dict[col] = 'last'

    df_monthly = df_monthly_prep.groupby('Month').agg(agg_dict).reset_index()

    # Convert Month period back to timestamp (end of month)
    df_monthly['Month Ending'] = df_monthly['Month'].dt.to_timestamp('M')
    df_monthly = df_monthly.drop('Month', axis=1)
    df_monthly = df_monthly.sort_values(by='Month Ending', ascending=True)
    df_monthly_latest = df_monthly.sort_values(by='Month Ending', ascending=False)

    # Calculate monthly trend indicators
    monthly_trend_indicators = {}
    for col_name in numeric_cols:
        if col_name in df_monthly.columns:
            trends = []
            for i in range(len(df_monthly)):
                current_val = df_monthly[col_name].iloc[i]
                if i > 0:
                    previous_val = df_monthly[col_name].iloc[i-1]
                    trends.append(calculate_trend_arrow(current_val, previous_val))
                else:
                    trends.append("→")
            # Debug output for connectors
            metric_name = col_name.replace('_NUM', '')
            if 'Connector' in metric_name:
                import sys
                sys.stderr.write(f"DEBUG {metric_name}: values={df_monthly[col_name].tolist()}, trends={trends}\n")
                sys.stderr.flush()
            monthly_trend_indicators[metric_name] = trends
        else:
            monthly_trend_indicators[col_name.replace('_NUM', '')] = ["→"] * len(df_monthly)

    return df_monthly, df_monthly_latest, monthly_trend_indicators


@st.cache_data(ttl=600)
def process_journey_stats_data(df_journey_stats):
    """
    Process the journey stats data to get weekly journey stats.

    Args:
        df_journey_stats: DataFrame with journey stats data

    Returns:
        DataFrame with aggregated weekly journey stats
    """
    if df_journey_stats.empty:
        return pd.DataFrame()

    # Convert week to datetime
    df_journey_stats['WEEK'] = pd.to_datetime(df_journey_stats['WEEK'])

    # Group by week and count unique tenants
    weekly_stats = df_journey_stats.groupby('WEEK').agg({
        'TENANT_NAME': 'nunique',
        'RUNNING_TOTAL_AT_WEEK_END': 'sum'
    }).reset_index()

    weekly_stats.rename(columns={
        'TENANT_NAME': 'unique_tenants',
        'RUNNING_TOTAL_AT_WEEK_END': 'total_journeys'
    }, inplace=True)

    weekly_stats.sort_values('WEEK', ascending=False, inplace=True)

    return weekly_stats

@st.cache_data(ttl=600)
def process_new_journey_tenants(df_new_journey_tenants):
    """
    Process the new journey tenants data.

    Args:
        df_new_journey_tenants: DataFrame with new journey tenants data

    Returns:
        DataFrame with new journey tenants grouped by week
    """
    if df_new_journey_tenants.empty:
        return pd.DataFrame()

    # Print column names and data stats
    print("Available columns in data frame:", df_new_journey_tenants.columns.tolist())
    print(f"Data shape: {df_new_journey_tenants.shape}")

    # Print journey run statistics if available
    if 'JOURNEY_RUNS_IN_WEEK' in df_new_journey_tenants.columns:
        # First ensure the column is numeric
        df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'] = pd.to_numeric(df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'], errors='coerce').fillna(0)

        run_counts = df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK']
        print(f"Journey run counts: min={run_counts.min()}, max={run_counts.max()}, mean={run_counts.mean():.1f}")
        print(f"Tenants with runs > 0: {(run_counts > 0).sum()}")
        print(f"Total journey runs: {int(run_counts.sum())}")

        # Print some sample tenants with runs
        has_runs = df_new_journey_tenants[df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'] > 0]
        if not has_runs.empty:
            print("\nSample tenants with journey runs:")
            sample = has_runs.sort_values('JOURNEY_RUNS_IN_WEEK', ascending=False).head(5)
            for _, row in sample.iterrows():
                print(f"{row['TENANT_NAME']}: {int(row['JOURNEY_RUNS_IN_WEEK'])} runs")
        else:
            print("\nNO TENANTS WITH JOURNEY RUNS > 0 FOUND - THIS IS A POTENTIAL DATA ISSUE!")
            print(f"Raw JOURNEY_RUNS_IN_WEEK value counts: {df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'].value_counts().to_dict()}")

    # Convert date columns to datetime
    for col in ['FIRST_JOURNEY_WEEK', 'ACTIVITY_WEEK', 'FIRST_JOURNEY_DATE']:
        if col in df_new_journey_tenants.columns:
            df_new_journey_tenants[col] = pd.to_datetime(df_new_journey_tenants[col])

    # Create a column to indicate if this is additional journeys (true) or first journeys (false)
    df_new_journey_tenants['IS_ADDITIONAL'] = df_new_journey_tenants['IS_ADDITIONAL_JOURNEY']

    # Create standard HAS_RUNS column - ensure we're using numeric values for comparison
    if 'JOURNEY_RUNS_IN_WEEK' in df_new_journey_tenants.columns:
        df_new_journey_tenants['HAS_RUNS'] = df_new_journey_tenants['JOURNEY_RUNS_IN_WEEK'] > 0
    elif 'HAS_JOURNEY_RUNS' in df_new_journey_tenants.columns:
        df_new_journey_tenants['HAS_RUNS'] = df_new_journey_tenants['HAS_JOURNEY_RUNS']
    else:
        df_new_journey_tenants['HAS_RUNS'] = False

    # Sort by activity week (descending) and tenant name
    df_new_journey_tenants.sort_values(['ACTIVITY_WEEK', 'TENANT_NAME'], ascending=[False, True], inplace=True)

    return df_new_journey_tenants

def extract_raw_values(df_pivoted, numeric_cols_for_trend):
    """
    Extract raw values from the DataFrame for charting.

    Args:
        df_pivoted: The pivoted DataFrame (weekly or monthly)
        numeric_cols_for_trend: List of numeric columns to extract

    Returns:
        Tuple of (raw_data, display_values, formatted_dates)
    """
    raw_data, display_values, formatted_dates = {}, {}, []

    # Determine which date column to use
    date_col = 'Month Ending' if 'Month Ending' in df_pivoted.columns else 'Week Ending'

    for date in df_pivoted[date_col]:
        formatted_dates.append(date.strftime('%b %d, %Y'))

    for metric in numeric_cols_for_trend:
        values, disp_values = [], []
        for _, row in df_pivoted.iterrows():
            val_str = row.get(metric, '')
            disp_values.append(val_str)
            values.append(parse_numeric_value(val_str))
        raw_data[metric] = values
        display_values[metric] = disp_values

    return raw_data, display_values, formatted_dates
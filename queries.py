"""
This module contains SQL queries used in the Activation Dashboard Streamlit app.
Queries are loaded from external .sql files for better maintainability.
"""
from pathlib import Path


def load_sql_query(filename):
    """
    Load a SQL query from a file in the same directory.

    Args:
        filename: Name of the SQL file to load (e.g., 'amps_query.sql')

    Returns:
        String containing the SQL query
    """
    sql_file = Path(__file__).parent / filename

    with open(sql_file, 'r') as f:
        return f.read()


# Load all SQL queries from external files
AMPS_QUERY = load_sql_query('amps_query.sql')
MAIN_DASHBOARD_QUERY = load_sql_query('main_dashboard_query.sql')
UNIQUE_JOURNEY_TENANTS_QUERY = load_sql_query('unique_journey_tenants_query.sql')
JOURNEY_WEEKLY_STATS_QUERY = load_sql_query('journey_weekly_stats_query.sql')
NEW_JOURNEY_TENANTS_QUERY = load_sql_query('new_journey_tenants_query.sql')

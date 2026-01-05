# Activation Dashboard

A Streamlit-based dashboard for visualizing activation metrics from Snowflake.

## Features

- Real-time metrics visualization for Activation, Journey, Paid Media, and Connectors
- Historical trend analysis with interactive charts
- Journey adoption tracking and tenant details
- AMPS consumption monitoring
- Weekly metrics breakdown

## Setup for Local Testing

### Prerequisites

- Python 3.8 or higher
- Access to Snowflake with appropriate permissions
- Okta SSO authentication

### Installation

1. **Clone or navigate to the repository:**
   ```bash
   cd /Users/eric/__Activation-Dashboard
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Snowflake connection:**

   Edit `config.py` and update the following parameters:
   ```python
   SNOWFLAKE_CONFIG = {
       'account': 'your-account-identifier',
       'user': 'your.email@company.com',
       'warehouse': 'YOUR_WAREHOUSE',
       'database': 'YOUR_DATABASE',
       'role': 'YOUR_ROLE',
   }
   ```

### Running the Dashboard

1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Authenticate:**
   - A browser window will open for Okta authentication on first run
   - Complete the SSO authentication process
   - The token will be cached for subsequent runs

3. **Access the dashboard:**
   - The dashboard will automatically open in your browser
   - Default URL: http://localhost:8501

## Project Structure

```
.
├── app.py                              # Main Streamlit application
├── config.py                           # Snowflake connection configuration
├── data_processing.py                  # Data fetching and transformation logic
├── components.py                       # UI components and tiles
├── queries.py                          # SQL query loader
├── utils.py                            # Utility functions
├── styles.py                           # CSS styles and chart configurations
├── requirements.txt                    # Python dependencies
├── *.sql                              # SQL query files
└── README.md                          # This file
```

## SQL Queries

The dashboard uses the following SQL queries:

- `main_dashboard_query.sql` - Main metrics for all categories
- `amps_query.sql` - AMPS consumption data
- `journey_weekly_stats_query.sql` - Weekly journey statistics
- `new_journey_tenants_query.sql` - New journey tenant tracking
- `unique_journey_tenants_query.sql` - Unique journey tenant counts

## Development

### Running in Snowflake Environment

The application is designed to work in both local and Snowflake environments:

- **Local**: Uses `snowflake-connector-python` with externalbrowser authentication
- **Snowflake**: Automatically uses `snowflake-snowpark-python` when available

### Git Integration with Snowflake

To deploy your dashboard updates automatically from GitHub instead of manually uploading files:

📖 **See [SNOWFLAKE_GIT_SETUP.md](SNOWFLAKE_GIT_SETUP.md) for complete setup instructions**

Benefits of Git integration:
- Automatic deployment from GitHub
- Version control and change tracking
- Easy rollback to previous versions
- Team collaboration without manual file uploads

### Modifying Queries

To update the SQL queries, edit the corresponding `.sql` files. The queries are automatically loaded by `queries.py`.

### Customizing Styles

CSS styles and chart configurations can be modified in `styles.py`.

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:
1. Clear cached tokens: `rm -rf ~/.snowflake/`
2. Restart the application
3. Re-authenticate via the browser

### Connection Errors

- Verify your Snowflake account details in `config.py`
- Ensure you have access to the specified warehouse, database, and role
- Check your network connection and VPN if required

### Data Issues

- Verify the SQL queries return data when run directly in Snowflake
- Check that your role has appropriate permissions
- Review the Streamlit logs for specific error messages

## References

- [Snowflake CLI Setup](/Users/eric/Documents/snowflake-cli/README.md)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Snowflake Python Connector](https://docs.snowflake.com/en/user-guide/python-connector.html)

"""
CSS styles for the Activation Dashboard app.
"""

# Main stylesheet for the application
MAIN_STYLESHEET = """
<style>
/* Chart container styles for responsive sizing */
.chart-container {
    width: 80%;
    margin: 0 auto;
    display: flex;
    justify-content: center;
}

/* Existing styles for historical tiles */
.metric-table {
    width: 100%;
    border-collapse: collapse;
}
.metric-table tr:nth-child(odd) {
    background-color: #f9fafb;
}
.metric-table tr:nth-child(even) {
    background-color: #ffffff;
}
.metric-table tr:last-child {
    border-bottom: none;
}
.metric-table td {
    padding: 0.3rem 0;
    font-size: 0.75rem;
    vertical-align: middle;
    border: none;
}
.metric-label {
    width: 40%;
    color: #6b7280;
    font-weight: 500;
    padding-left: 0.5rem;
}
.metric-value {
    width: 60%;
    display: flex;
    align-items: center;
}
.value-main {
    min-width: 55%;
    font-weight: 600;
    color: #374151;
}
.trend-arrow {
    width: 15%;
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
}
.child-metric {
    width: 30%;
    font-size: 0.7rem;
    color: #4b5563;
    text-align: right;
}
.tile-container {
    background-color: #ffffff;
    padding: 0.8rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    margin-bottom: 10px;
    font-size: 0.9rem;
}
.tile-header {
    font-size: 1rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 0.3rem 0;
    padding-left: 0.5rem;
}
/* New and updated styles for the top featured tiles to match Slide 4 */
.metric-box {
    background-color: #ffffff; /* White background like the slide */
    padding: 1.5rem; /* Increased padding for more breathing room */
    border-radius: 0.75rem; /* More rounded corners */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Softer, more pronounced shadow */
    text-align: center;
    margin: 0 0.5rem 1.5rem 0.5rem; /* Add even margins on all sides */
    height: 100%; /* Ensure boxes in a row have equal height */
    display: flex;
    flex-direction: column;
    justify-content: space-between; /* Distribute content vertically */
}
.metric-name {
    font-size: 1.1rem; /* Slightly larger for main title in tile */
    color: #6b7280; /* Grayish color */
    font-weight: 600; /* Bolder */
    margin-bottom: 0.5rem; /* Space below the name */
    text-transform: uppercase; /* Uppercase like slide */
}
.metric-value-large {
    font-size: 2.5rem; /* Slightly reduced size for better fit */
    font-weight: 700; /* Bold */
    color: #1f2937; /* Darker text */
    display: flex;
    justify-content: flex-start; /* Left align for the new layout */
    align-items: center;
    margin-bottom: 0.5rem; /* Spacing below metric */
    line-height: 1.2; /* Slightly increased for better readability */
}
.metric-arrow {
    margin-right: 0.5rem; /* Space after arrow */
    font-size: 1.8rem; /* Slightly smaller arrow */
    display: inline-block; /* Ensure it displays properly */
}
/* Styles for the new activation tile design */
.metric-row {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 1rem;
    text-align: left;
}
.metric-label-new {
    font-size: 1rem;
    color: #4b5563;
    margin-bottom: 0.25rem;
    font-weight: 500;
}
.metric-value-wrapper {
    display: flex;
    align-items: center;
}
.metric-value-main {
    font-size: 1.8rem;
    font-weight: 600;
    color: #1f2937;
}
.metric-parenthetical {
    font-size: 1rem;
    color: #6b7280;
    margin-left: 0.5rem;
}
/* Styles for the connector stats grid */
.connector-stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    margin-top: 1rem;
}
.connector-stat-item {
    text-align: center;
    padding: 0.5rem;
    background-color: #f9fafb;
    border-radius: 0.375rem;
}
.connector-stat-label {
    font-size: 0.875rem;
    color: #6b7280;
    font-weight: 500;
    margin-bottom: 0.25rem;
}
.connector-stat-value {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
}
.connector-stat-arrow {
    display: inline-block;
    margin-right: 0.25rem;
    font-size: 0.875rem;
}
.metric-sub {
    font-size: 0.95rem; /* Slightly larger for sub-text */
    color: #4b5563; /* Medium gray */
    text-align: center;
    margin-top: 0.25rem; /* Space above sub-text */
    line-height: 1.3; /* A bit more line height for readability */
}
.tile-title {
    font-size: 1.8rem; /* Larger title for the week ending */
    font-weight: 700;
    color: #1f2937;
    text-align: center;
    margin-bottom: 1.5rem; /* More space below the week title */
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e5e7eb; /* Lighter border */
}
.main-title {
    font-size: 2.8rem; /* Larger main title */
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 0.8rem;
    text-align: center;
}
.sub-title {
    font-size: 1.4rem; /* Larger subtitle */
    color: #6b7280; /* More prominent gray */
    text-align: center;
    margin-bottom: 2.5rem;
}
/* Styles for connector table */
.connector-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin-top: 1rem;
}
.connector-table tr {
    background-color: #f9fafb;
}
.connector-table tr:nth-child(even) {
    background-color: #ffffff;
}
.connector-table td {
    padding: 0.5rem 0.3rem;
    font-size: 0.9rem;
    vertical-align: middle;
    text-align: left;
    border: none;
}
.connector-trend {
    width: 10%;
    text-align: center;
}
.connector-name {
    width: 50%;
    font-weight: 500;
    color: #4b5563;
    padding-left: 0.5rem;
}
.connector-value {
    width: 40%;
    text-align: right;
    font-weight: 600;
    color: #1f2937;
    padding-right: 0.5rem;
}
</style>
"""

def apply_styles(st):
    """
    Apply the stylesheet to the Streamlit app.

    Args:
        st: Streamlit module
    """
    st.markdown(MAIN_STYLESHEET, unsafe_allow_html=True)


# Chart color definitions
CHART_COLORS = {
    "activation": ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444"],
    "journey": ["#06b6d4", "#6366f1", "#10b981", "#f59e0b"],
    "paid_media": ["#f59e0b", "#ef4444", "#8b5cf6", "#10b981"],
    "connector": ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4"],
    "amps": ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4"]
}

# Chart definitions
CHART_DEFINITIONS = {
    "activation": {
        "metrics": ["Campaign & Segment Sends", "Campaign & Segment Rows Sent", "Total Sends", "CS Tenants", "Rows Sent"],
        "title": "Activation Metrics Trend",
        "colors": CHART_COLORS["activation"]
    },
    "journey": {
        "metrics": ["Journeys", "Journey Clients", "Journey Adoption"],
        "title": "Journey Metrics Trend",
        "colors": CHART_COLORS["journey"],
        "display_names": {"Journey Adoption": "# of Tenants Created a Journey", "Journeys": "Journey Runs", "Journey Clients": "Journey Client Tenants"}
    },
    "paid_media": {
        "metrics": ["Paid Media Tenants", "Paid Media Sends", "Paid Media Rows", "Paid Media %"],
        "title": "Paid Media Metrics Trend",
        "colors": CHART_COLORS["paid_media"]
    },
    "connector": {
        "metrics": ["Source Connectors", "Destination Connectors", "Bi-Directional Connectors"],
        "title": "Connector Metrics Trend",
        "colors": CHART_COLORS["connector"]
    },
    "amps": {
        "metrics": ["Amps - Total", "Amps - Activation", "Amps - Campaigns", "Amps - Journeys", "Amps - Orchestration", "Amps - Profile API"],
        "title": "Amps Consumption Trend",
        "colors": CHART_COLORS["amps"]
    }
}

# Metrics configurations
ACTIVATION_METRICS = [
    {"title": "Tenants with Campaign/Segment Sends", "value_col": "CS Tenants", "parenthetical_col": "CS Tenants Percent", "trend_col": "CS Tenants"},
    {"title": "Campaign & Segment Sends", "value_col": "Campaign & Segment Sends", "parenthetical_col": "Campaign & Segment %", "trend_col": "Campaign & Segment Sends"},
    {"title": "Campaign & Segment Rows Sent", "value_col": "Campaign & Segment Rows Sent", "parenthetical_col": "Rows Sent", "trend_col": "Campaign & Segment Rows Sent"},
    {"title": "Total Sends", "value_col": "Total Sends", "parenthetical_col": None, "trend_col": "Total Sends"},
    {"title": "Rows Sent", "value_col": "Rows Sent", "parenthetical_col": None, "trend_col": "Rows Sent"}
]

JOURNEY_METRICS = [
    {"title": "Journey Runs (This Week)", "value_col": "Journeys", "parenthetical_col": None, "trend_col": "Journeys"},
    {"title": "Tenants with Journey Run", "value_col": "Journey Clients", "parenthetical_col": None, "trend_col": "Journey Clients"},
    {"title": "# of Tenants Created a Journey (This Week)", "value_col": "Journey Adoption", "parenthetical_col": None, "trend_col": "Journey Adoption"}
]

PAID_MEDIA_METRICS = [
    {"title": "Paid Media Tenants", "value_col": "Paid Media Tenants", "parenthetical_col": "Paid Media %", "trend_col": "Paid Media Tenants"},
    {"title": "Paid Media Sends", "value_col": "Paid Media Sends", "parenthetical_col": None, "trend_col": "Paid Media Sends"},
    {"title": "Paid Media Rows", "value_col": "Paid Media Rows", "parenthetical_col": None, "trend_col": "Paid Media Rows"}
]

CONNECTOR_METRICS = [
    {"title": "Source Connectors", "value_col": "Source Connectors", "parenthetical_col": None, "trend_col": "Source Connectors"},
    {"title": "Destination Connectors", "value_col": "Destination Connectors", "parenthetical_col": None, "trend_col": "Destination Connectors"},
    {"title": "Bi-Directional Connectors", "value_col": "Bi-Directional Connectors", "parenthetical_col": None, "trend_col": "Bi-Directional Connectors"}
]

AMPS_METRICS = [
    {"title": "Total Amps", "value_col": "Amps - Total", "parenthetical_col": None, "trend_col": "Amps - Total"},
    {"title": "Activation Amps", "value_col": "Amps - Activation", "parenthetical_col": None, "trend_col": "Amps - Activation"},
    {"title": "Campaigns Amps", "value_col": "Amps - Campaigns", "parenthetical_col": None, "trend_col": "Amps - Campaigns"},
    {"title": "Journeys Amps", "value_col": "Amps - Journeys", "parenthetical_col": None, "trend_col": "Amps - Journeys"},
    {"title": "Orchestration Amps", "value_col": "Amps - Orchestration", "parenthetical_col": None, "trend_col": "Amps - Orchestration"},
    {"title": "Profile API Amps", "value_col": "Amps - Profile API", "parenthetical_col": None, "trend_col": "Amps - Profile API"}
]

# Monthly metric configurations (simplified per boss's requirements)
ACTIVATION_METRICS_MONTHLY = [
    {"title": "Tenants with Campaign/Segment Sends", "value_col": "CS Tenants", "parenthetical_col": "CS Tenants Percent", "trend_col": "CS Tenants"},
    {"title": "Campaign & Segment Sends", "value_col": "Campaign & Segment Sends", "parenthetical_col": None, "trend_col": "Campaign & Segment Sends"},
    {"title": "Campaign & Segment Rows Sent", "value_col": "Campaign & Segment Rows Sent", "parenthetical_col": None, "trend_col": "Campaign & Segment Rows Sent"}
]

# Journey monthly - same as weekly
JOURNEY_METRICS_MONTHLY = JOURNEY_METRICS

# Paid Media monthly - same as weekly
PAID_MEDIA_METRICS_MONTHLY = PAID_MEDIA_METRICS

# Connectors monthly - only Inbound (Source) & Outbound (Destination)
CONNECTOR_METRICS_MONTHLY = [
    {"title": "Source Connectors (Inbound)", "value_col": "Source Connectors", "parenthetical_col": None, "trend_col": "Source Connectors"},
    {"title": "Destination Connectors (Outbound)", "value_col": "Destination Connectors", "parenthetical_col": None, "trend_col": "Destination Connectors"}
]

# Amps monthly - same as weekly
AMPS_METRICS_MONTHLY = AMPS_METRICS
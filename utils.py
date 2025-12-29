"""
Utility functions for the Activation Dashboard app.
"""
import pandas as pd
import numpy as np


def parse_numeric_value(value_str):
    """
    Parse a string value that may contain formatted numbers with suffixes like k, M, B, T, or percentages.
    Returns a numeric value or np.nan if the value cannot be parsed.

    Args:
        value_str: String value to parse

    Returns:
        Parsed numeric value or np.nan
    """
    if pd.isna(value_str) or value_str is None or str(value_str).strip() == '':
        return np.nan
    s_value = str(value_str).strip().replace(',', '')
    if s_value.endswith('%'):
        try:
            return float(s_value[:-1])
        except ValueError:
            return np.nan
    suffix_multipliers = {
        'k': 1_000, 'K': 1_000, 'm': 1_000_000, 'M': 1_000_000,
        'b': 1_000_000_000, 'B': 1_000_000_000, 't': 1_000_000_000_000, 'T': 1_000_000_000_000
    }
    for suffix, multiplier in suffix_multipliers.items():
        if s_value.endswith(suffix):
            try:
                return float(s_value[:-len(suffix)]) * multiplier
            except ValueError:
                return np.nan
    try:
        value = float(s_value)
        if not np.isfinite(value):
            return np.nan
        return value
    except ValueError:
        return np.nan


def format_large_number(value):
    """
    Formats a number to have no more than 2 digits before a decimal,
    using 'k', 'M', 'B', 'T' postfixes.
    Handles values that are already formatted strings (e.g., '70k').

    Args:
        value: The value to format (can be a number or formatted string)

    Returns:
        Formatted string representation of the number
    """
    # Use the existing parser to convert strings like '70k' to a number
    num = parse_numeric_value(value)
    if pd.isna(num):
        return value  # Return original value if it's not a number (e.g., 'N/A')

    num = float(num)

    # Return numbers < 1000 as is, without decimals
    if abs(num) < 1000:
        return str(int(round(num)))

    # Handle thousands: 1,000 to 99,999 -> 1k to 99.9k
    if abs(num) < 100_000:
        return f"{num / 1000:.1f}k".replace(".0k", "k")

    # Handle millions: 100,000 to 99,999,999 -> 0.10M to 99.9M
    if abs(num) < 100_000_000:
        val = num / 1_000_000
        # Show more precision for numbers under 1 million
        if val < 1:
            return f"{val:.2f}M".replace(".00M", "M")
        return f"{val:.1f}M".replace(".0M", "M")

    # Handle billions: 100,000,000 to 99,999,999,999 -> 0.10B to 99.9B
    if abs(num) < 100_000_000_000:
        val = num / 1_000_000_000
        if val < 1:
            return f"{val:.2f}B".replace(".00B", "B")
        return f"{val:.1f}B".replace(".0B", "B")

    # Handle trillions
    val = num / 1_000_000_000_000
    if val < 1:
        return f"{val:.2f}T".replace(".00T", "T")
    return f"{val:.1f}T".replace(".0T", "T")


def calculate_trend_arrow(current_value, previous_value):
    """
    Calculates trend indicator arrow based on comparison of current and previous values.

    Args:
        current_value: The current metric value
        previous_value: The previous metric value for comparison

    Returns:
        String representing the trend: "▲" (up), "▼" (down), or "→" (unchanged)
    """
    if pd.isna(current_value) or pd.isna(previous_value):
        return "→"
    if current_value > previous_value:
        return "▲"
    elif current_value < previous_value:
        return "▼"
    else:
        return "→"


def get_arrow_html(indicator):
    """
    Returns HTML for a colored trend arrow.

    Args:
        indicator: Arrow indicator ("▲", "▼", or "→")

    Returns:
        HTML string with the styled arrow
    """
    if indicator == "▲":
        return '<span style="color:#10b981;">▲</span>'  # Green up arrow
    elif indicator == "▼":
        return '<span style="color:#ef4444;">▼</span>'  # Red down arrow
    elif indicator == "→":
        return '<span style="color:#6b7280;">→</span>'  # Gray right arrow
    return ""


def normalize_for_display(series):
    """
    Normalize a series of values for display in charts.
    Handles missing values using interpolation.

    Args:
        series: The series of values to normalize

    Returns:
        Normalized array of values between 0.1 and 0.9
    """
    series = np.array(series, dtype=float)
    valid_mask = np.isfinite(series)

    if not np.any(valid_mask):
        return np.full(len(series), 0.5)

    if not np.all(valid_mask):
        valid_indices = np.where(valid_mask)[0]
        invalid_indices = np.where(~valid_mask)[0]

        if len(valid_indices) >= 2:
            # Use numpy's interp instead of scipy
            series[invalid_indices] = np.interp(
                invalid_indices,
                valid_indices,
                series[valid_mask]
            )
        else:
            series[invalid_indices] = series[valid_indices[0]]

    if np.max(series) == np.min(series):
        return np.full_like(series, 0.5)

    min_val, max_val = np.min(series), np.max(series)
    data_range = max_val - min_val
    normalized = (series - min_val) / data_range

    # Scale to range 0.1 to 0.9 to avoid extreme edges
    return (normalized * 0.8) + 0.1
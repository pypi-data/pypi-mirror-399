"""Results table component for displaying VIN decode results"""

import streamlit as st
from typing import Any, Dict

# pandas not needed - using HTML table
from src.formatting.fields import FIELD_LABELS, FIELD_DESCRIPTIONS


def display_results_table(filtered_data: Dict[str, Any]) -> None:
    """
    Display VIN decode results in a clean table format with tooltips

    Args:
        filtered_data: Dictionary of field names to values (non-null only)
    """
    if not filtered_data:
        st.warning("No data to display")
        return

    # Build display data with clean labels and tooltips
    display_rows = []
    for field_name, value in filtered_data.items():
        label = FIELD_LABELS.get(field_name, field_name.replace("_", " ").title())
        description = FIELD_DESCRIPTIONS.get(field_name, "")

        # Create field name with tooltip using HTML title attribute
        if description:
            field_with_tooltip = f'<span title="{description}">{label}</span>'
        else:
            field_with_tooltip = label

        display_rows.append({"Field": field_with_tooltip, "Value": str(value)})

    # Create DataFrame
    # Display as HTML table to support tooltips
    st.markdown(
        """
    <style>
    .results-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    .results-table th {
        background-color: rgba(128, 128, 128, 0.2);
        color: inherit;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid rgba(128, 128, 128, 0.3);
    }
    .results-table td {
        padding: 10px 12px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        color: inherit;
    }
    .results-table tr:hover td {
        background-color: rgba(128, 128, 128, 0.1);
    }
    .results-table span[title] {
        cursor: help;
        border-bottom: 1px dotted currentColor;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Generate HTML table
    table_html = '<table class="results-table">'
    table_html += "<tr><th>Field</th><th>Value</th></tr>"

    for row in display_rows:
        table_html += f"<tr><td>{row['Field']}</td><td>{row['Value']}</td></tr>"

    table_html += "</table>"

    st.markdown(table_html, unsafe_allow_html=True)


__all__ = ["display_results_table"]

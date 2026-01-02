"""pyVIN - Vehicle Identification Number Decoder"""

import streamlit as st

st.set_page_config(page_title="Home - pyVIN", page_icon="🚗", layout="wide")

# Header
st.title("🚗 pyVIN")
st.subheader("Vehicle Identification Number Decoder")

# About Section
st.markdown("---")
st.header("About pyVIN")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    **pyVIN** is a Python-based Vehicle Identification Number (VIN) decoder that provides comprehensive
    vehicle information using the NHTSA vPIC (Vehicle Product Information Catalog) API.

    ### Features
    - 🔍 **Decode any 17-character VIN** instantly
    - 📊 **Comprehensive vehicle data** including make, model, year, specifications, and safety features
    - 🏭 **Manufacturing details** such as plant location and manufacturer information
    - ⚡ **Clean, filterable results** showing only available information
    - 📱 **Responsive interface** built with Streamlit

    ### What is a VIN?
    A Vehicle Identification Number (VIN) is a unique 17-character code assigned to every motor vehicle
    when manufactured. The VIN provides critical information about the vehicle including:
    - Manufacturer and country of origin
    - Vehicle specifications and features
    - Model year and production details
    - Safety and equipment information

    ### How to Use
    Navigate to the **VIN Decoder** page from the sidebar to start decoding VINs.
    """)

with col2:
    st.info("""
    **Quick Start**

    1. Click **VIN Decoder** in the sidebar
    2. Enter a 17-character VIN
    3. Click **Decode VIN**
    4. View detailed results

    **Example VIN:**
    `5UXWX7C50BA123456`
    """)


st.markdown("---")

# Footer
st.caption("© 2025 NovelGit LLC | Data provided by NHTSA vPIC API")
st.caption(
    "This tool is for informational purposes only. Always verify vehicle information through official sources."
)

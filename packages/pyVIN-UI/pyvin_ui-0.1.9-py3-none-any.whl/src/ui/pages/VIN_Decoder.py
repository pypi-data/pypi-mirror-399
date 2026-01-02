"""VIN Decoder page for pyVIN application"""

import streamlit as st
from src.api.client import decode_vin_values_extended
from src.formatting.response import filter_non_null
from src.ui.components.results_table import display_results_table
from src.exceptions import VINDecoderError

st.set_page_config(page_title="VIN Decoder - pyVIN", layout="wide")

st.title("🚗 VIN Decoder")
st.markdown(
    "Enter a 17-character Vehicle Identification Number to decode vehicle information from the NHTSA database."
)

st.info(
    "💡 **Tip:** VIN must be exactly 17 characters. Use `*` as a wildcard for unknown positions. Example: `5UXWX7C*5*B*A******`"
)

# VIN Input
vin_input = st.text_input(
    "Vehicle Identification Number",
    placeholder="Enter 17-character VIN (use * for unknowns)...",
    help="Example: 5UXWX7C50BA123456 or 5UXWX7C*5*B*A****** for partial VIN",
).strip()
# 5UXWX7C*5*B*A******
# Decode button
if st.button("Decode VIN", type="primary", use_container_width=False):
    if vin_input:
        if len(vin_input) != 17:
            st.error("VIN must be exactly 17 characters")
        else:
            try:
                with st.spinner("Decoding VIN..."):
                    result = decode_vin_values_extended(vin_input)
                    filtered = filter_non_null(result)

                # Show warnings if present (error codes 0-99)
                if result.error_text and result.error_code and result.error_code != "0":
                    warning_msg = f"⚠️ **Warnings:** {result.error_text}"
                    if result.suggested_vin:
                        warning_msg += (
                            f"\n\n**Suggested VIN:** `{result.suggested_vin}`"
                        )
                    if result.possible_values:
                        warning_msg += (
                            f"\n\n**Possible Values:** {result.possible_values}"
                        )
                    st.warning(warning_msg)
                else:
                    st.success(f"✅ Successfully decoded VIN: {result.vin}")

                # Display results using the custom table component
                display_results_table(filtered)

            except VINDecoderError as e:
                st.error(f"❌ Decoding Error: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected Error: {e}")
    else:
        st.warning("⚠️ Please enter a VIN")

# Footer with helpful info
st.divider()
st.caption("Data provided by the NHTSA vPIC API")

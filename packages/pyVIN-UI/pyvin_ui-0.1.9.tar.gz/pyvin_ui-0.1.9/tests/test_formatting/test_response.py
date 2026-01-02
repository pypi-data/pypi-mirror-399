"""Tests for response formatting module"""

from hypothesis import given, strategies as st
from src.formatting.response import filter_non_null
from src.api.models import VINDecodeResult


class TestFilterNonNull:
    """Tests for filter_non_null function"""

    def test_filters_none_values(self, sample_vin_result_with_nulls):
        """Test that None values are filtered out"""
        filtered = filter_non_null(sample_vin_result_with_nulls)

        # None values should be filtered
        assert "manufacturer" not in filtered
        assert "body_class" not in filtered

        # Non-None values should be present
        assert "vin" in filtered
        assert "make" in filtered
        assert "model" in filtered
        assert filtered["vin"] == "5UXWX7C50BA123456"

    def test_filters_empty_strings(self):
        """Test that empty strings are filtered out"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            make="BMW",
            model="",  # Empty string should become None and be filtered
            trim="   ",  # Whitespace should become None and be filtered
        )

        filtered = filter_non_null(result)

        assert "model" not in filtered
        assert "trim" not in filtered
        assert "vin" in filtered
        assert "make" in filtered

    def test_returns_field_names_not_aliases(self, sample_vin_result):
        """Test that filtered dict uses field names, not API aliases"""
        filtered = filter_non_null(sample_vin_result)

        # Should have field names (lowercase with underscores)
        assert "vin" in filtered
        assert "make" in filtered
        assert "model_year" in filtered
        assert "displacement_liters" in filtered

        # Should NOT have API aliases
        assert "VIN" not in filtered
        assert "Make" not in filtered
        assert "ModelYear" not in filtered
        assert "DisplacementL" not in filtered

    def test_all_none_values(self):
        """Test with result that has all None values"""
        result = VINDecodeResult()
        filtered = filter_non_null(result)

        # Should be empty since all values are None
        assert len(filtered) == 0

    def test_preserves_all_valid_values(self, sample_vin_result):
        """Test that all non-null values are preserved"""
        filtered = filter_non_null(sample_vin_result)

        # All these fields should be present
        assert filtered["vin"] == "5UXWX7C50BA123456"
        assert filtered["make"] == "BMW"
        assert filtered["model"] == "X3"
        assert filtered["model_year"] == "2011"
        assert filtered["doors"] == "4"
        assert filtered["engine_cylinders"] == "6"

    def test_returns_dict(self, sample_vin_result):
        """Test that function returns a dictionary"""
        filtered = filter_non_null(sample_vin_result)
        assert isinstance(filtered, dict)

    def test_mixed_none_and_values(self):
        """Test with mix of None and valid values"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            make="BMW",
            model=None,
            model_year="2011",
            manufacturer=None,
            doors="4",
            trim=None,
        )

        filtered = filter_non_null(result)

        assert len(filtered) == 4  # vin, make, model_year, doors
        assert "vin" in filtered
        assert "make" in filtered
        assert "model_year" in filtered
        assert "doors" in filtered
        assert "model" not in filtered
        assert "manufacturer" not in filtered
        assert "trim" not in filtered

    def test_zero_values_not_filtered(self):
        """Test that '0' string values are NOT filtered"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            error_code="0",  # '0' should not be filtered
            doors="0",  # '0' should not be filtered
        )

        filtered = filter_non_null(result)

        assert "error_code" in filtered
        assert filtered["error_code"] == "0"
        assert "doors" in filtered
        assert filtered["doors"] == "0"

    def test_special_characters_preserved(self):
        """Test that special characters in values are preserved"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            manufacturer="BMW MANUFACTURER CORPORATION / USA",
            body_class="Sport Utility Vehicle (SUV)/Multi-Purpose Vehicle (MPV)",
        )

        filtered = filter_non_null(result)

        assert "/" in filtered["manufacturer"]
        assert "(" in filtered["body_class"]
        assert ")" in filtered["body_class"]

    @given(
        st.text(min_size=1, max_size=50),
        st.text(min_size=1, max_size=50),
        st.text(min_size=1, max_size=50),
    )
    def test_fuzzing_with_various_strings(self, vin, make, model):
        """Fuzz test with various string values"""
        result = VINDecodeResult(vin=vin, make=make, model=model)
        filtered = filter_non_null(result)

        # Fields should be in filtered only if they're not whitespace-only
        # (empty_str_to_none validator converts whitespace to None)
        if vin.strip():
            assert "vin" in filtered
            assert filtered["vin"] == vin
        else:
            assert "vin" not in filtered

        if make.strip():
            assert "make" in filtered
            assert filtered["make"] == make
        else:
            assert "make" not in filtered

        if model.strip():
            assert "model" in filtered
            assert filtered["model"] == model
        else:
            assert "model" not in filtered

    def test_filtering_preserves_data_integrity(self, sample_vin_result):
        """Test that filtering doesn't modify original data"""
        original_vin = sample_vin_result.vin
        original_make = sample_vin_result.make

        filtered = filter_non_null(sample_vin_result)

        # Original object should be unchanged
        assert sample_vin_result.vin == original_vin
        assert sample_vin_result.make == original_make

        # Filtered dict should have correct values
        assert filtered["vin"] == original_vin
        assert filtered["make"] == original_make

    def test_numeric_strings_preserved(self):
        """Test that numeric strings are preserved"""
        result = VINDecodeResult(
            vin="12345678901234567",
            model_year="2024",
            doors="2",
            engine_cylinders="8",
            displacement_liters="5.0",
        )

        filtered = filter_non_null(result)

        assert filtered["model_year"] == "2024"
        assert filtered["doors"] == "2"
        assert filtered["engine_cylinders"] == "8"
        assert filtered["displacement_liters"] == "5.0"

    def test_whitespace_only_filtered(self):
        """Test that whitespace-only strings are filtered"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            make="   ",  # Whitespace only
            model="\t\n",  # Tabs and newlines
            trim="     ",  # Spaces
        )

        filtered = filter_non_null(result)

        assert "make" not in filtered
        assert "model" not in filtered
        assert "trim" not in filtered
        assert "vin" in filtered

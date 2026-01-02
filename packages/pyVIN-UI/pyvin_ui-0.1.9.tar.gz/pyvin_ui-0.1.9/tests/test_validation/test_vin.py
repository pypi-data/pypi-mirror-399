"""Tests for VIN validation module"""

import pytest
from hypothesis import given, strategies as st
from src.validation.vin import validate_and_normalize_vin, VIN_PATTERN
from src.exceptions import InvalidVINError


class TestValidateAndNormalizeVIN:
    """Tests for validate_and_normalize_vin function"""

    def test_valid_vin(self, valid_vin):
        """Test validation of valid VIN"""
        result = validate_and_normalize_vin(valid_vin)
        assert result == valid_vin
        assert len(result) == 17

    def test_valid_vin_lowercase(self, valid_vin_lowercase):
        """Test that lowercase VIN is normalized to uppercase"""
        result = validate_and_normalize_vin(valid_vin_lowercase)
        assert result == valid_vin_lowercase.upper()
        assert result.isupper()

    def test_valid_vin_with_whitespace(self, valid_vin):
        """Test that VIN with leading/trailing whitespace is normalized"""
        vin_with_whitespace = f"  {valid_vin}  "
        result = validate_and_normalize_vin(vin_with_whitespace)
        assert result == valid_vin
        assert result == result.strip()

    def test_empty_vin(self):
        """Test that empty VIN raises error"""
        with pytest.raises(InvalidVINError, match="VIN cannot be empty"):
            validate_and_normalize_vin("")

    def test_none_vin(self):
        """Test that None VIN raises error"""
        with pytest.raises(InvalidVINError, match="VIN cannot be empty"):
            validate_and_normalize_vin(None)

    def test_vin_too_short(self, invalid_vin_short):
        """Test that VIN shorter than 17 characters raises error"""
        with pytest.raises(InvalidVINError, match="VIN must be exactly 17 characters"):
            validate_and_normalize_vin(invalid_vin_short)

    def test_vin_too_long(self, invalid_vin_long):
        """Test that VIN longer than 17 characters raises error"""
        with pytest.raises(InvalidVINError, match="VIN must be exactly 17 characters"):
            validate_and_normalize_vin(invalid_vin_long)

    def test_vin_with_invalid_character_i(self, invalid_vin_with_i):
        """Test that VIN with 'I' raises error"""
        with pytest.raises(InvalidVINError, match="Invalid VIN format"):
            validate_and_normalize_vin(invalid_vin_with_i)

    def test_vin_with_invalid_character_o(self, invalid_vin_with_o):
        """Test that VIN with 'O' raises error"""
        with pytest.raises(InvalidVINError, match="Invalid VIN format"):
            validate_and_normalize_vin(invalid_vin_with_o)

    def test_vin_with_invalid_character_q(self, invalid_vin_with_q):
        """Test that VIN with 'Q' raises error"""
        with pytest.raises(InvalidVINError, match="Invalid VIN format"):
            validate_and_normalize_vin(invalid_vin_with_q)

    def test_vin_with_special_characters(self):
        """Test that VIN with special characters raises error"""
        invalid_vins = [
            "5UXWX7C50BA12345!",  # Exclamation mark
            "5UXWX7C50BA12345@",  # At symbol
            "5UXWX7C50BA12345#",  # Hash
            "5UXWX7C50BA12345$",  # Dollar sign
            "5UXWX7C50BA-123456",  # Dash
            "5UXWX7C50BA_123456",  # Underscore
        ]
        for vin in invalid_vins:
            with pytest.raises(InvalidVINError):
                validate_and_normalize_vin(vin)

    def test_vin_with_lowercase_i_o_q(self):
        """Test that lowercase i, o, q are also invalid"""
        invalid_vins = [
            "5UXWX7C50Bi123456",  # lowercase i
            "5UXWX7C50Bo123456",  # lowercase o
            "5UXWX7C50Bq123456",  # lowercase q
        ]
        for vin in invalid_vins:
            with pytest.raises(InvalidVINError, match="Invalid VIN format"):
                validate_and_normalize_vin(vin)

    def test_vin_with_wildcard(self):
        """Test that VIN with * wildcard is valid (for API queries)"""
        vin_with_wildcard = "5UXWX7C50BA******"
        result = validate_and_normalize_vin(vin_with_wildcard)
        assert result == vin_with_wildcard

    def test_vin_all_wildcards(self):
        """Test VIN with all wildcards"""
        vin_all_wildcards = "*****************"
        result = validate_and_normalize_vin(vin_all_wildcards)
        assert result == vin_all_wildcards

    @given(
        st.text(
            alphabet=st.sampled_from(
                "ABCDEFGHJKLMNPRSTUVWXYZ0123456789*"  # No I, O, Q
            ),
            min_size=17,
            max_size=17,
        )
    )
    def test_valid_vin_fuzzing(self, vin):
        """Fuzz test with valid VIN characters"""
        result = validate_and_normalize_vin(vin)
        assert len(result) == 17
        # VIN is valid if it matches the pattern (includes digits, uppercase, wildcards)
        assert VIN_PATTERN.match(result)

    @given(
        st.one_of(
            st.text(min_size=0, max_size=16),  # Too short
            st.text(min_size=18, max_size=100),  # Too long
        )
    )
    def test_invalid_length_fuzzing(self, vin):
        """Fuzz test with invalid VIN lengths"""
        # After stripping, could be empty or wrong length
        normalized = vin.upper().strip() if vin else ""

        if not normalized:
            with pytest.raises(InvalidVINError, match="VIN cannot be empty"):
                validate_and_normalize_vin(vin)
        else:
            with pytest.raises(
                InvalidVINError, match="VIN must be exactly 17 characters"
            ):
                validate_and_normalize_vin(vin)

    @given(
        st.text(
            alphabet=st.sampled_from("IOQioq!@#$%^&()-_=+[]{}|;:'\",.<>?/\\"),
            min_size=1,
            max_size=1,
        )
    )
    def test_invalid_characters_fuzzing(self, invalid_char):
        """Fuzz test with invalid characters"""
        vin = f"5UXWX7C50BA12345{invalid_char}"
        with pytest.raises(InvalidVINError, match="Invalid VIN format"):
            validate_and_normalize_vin(vin)


class TestVINPattern:
    """Tests for VIN_PATTERN regex"""

    def test_pattern_matches_valid_vin(self, valid_vin):
        """Test that pattern matches valid VIN"""
        assert VIN_PATTERN.match(valid_vin)

    def test_pattern_rejects_lowercase(self, valid_vin_lowercase):
        """Test that pattern rejects lowercase letters"""
        assert not VIN_PATTERN.match(valid_vin_lowercase)

    def test_pattern_allows_wildcard(self):
        """Test that pattern allows * wildcard"""
        assert VIN_PATTERN.match("5UXWX7C50BA******")

    def test_pattern_rejects_invalid_chars(self):
        """Test that pattern rejects I, O, Q"""
        assert not VIN_PATTERN.match("5UXWX7C50BI123456")
        assert not VIN_PATTERN.match("5UXWX7C50BO123456")
        assert not VIN_PATTERN.match("5UXWX7C50BQ123456")

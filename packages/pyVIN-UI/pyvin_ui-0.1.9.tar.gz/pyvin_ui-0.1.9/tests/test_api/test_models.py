"""Tests for API models module"""

from hypothesis import given, strategies as st
from src.api.models import VINDecodeResult


class TestVINDecodeResult:
    """Tests for VINDecodeResult Pydantic model"""

    def test_create_with_all_fields(self):
        """Test creating model with all fields"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            make="BMW",
            model="X3",
            model_year="2011",
            manufacturer="BMW MANUFACTURER",
            body_class="SUV",
            doors="4",
            engine_cylinders="6",
            displacement_liters="3.0",
            fuel_type="Gasoline",
        )

        assert result.vin == "5UXWX7C50BA123456"
        assert result.make == "BMW"
        assert result.model == "X3"
        assert result.model_year == "2011"

    def test_create_with_minimal_fields(self):
        """Test creating model with only required fields (none are required)"""
        result = VINDecodeResult()
        assert result.vin is None
        assert result.make is None

    def test_create_with_aliases(self):
        """Test creating model using API field names (aliases)"""
        result = VINDecodeResult(
            VIN="5UXWX7C50BA123456",
            Make="BMW",
            Model="X3",
            ModelYear="2011",
        )

        assert result.vin == "5UXWX7C50BA123456"
        assert result.make == "BMW"
        assert result.model == "X3"
        assert result.model_year == "2011"

    def test_empty_string_to_none_validator(self):
        """Test that empty strings are converted to None"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            make="BMW",
            model="",  # Empty string
            trim="   ",  # Whitespace only
            doors="4",
        )

        assert result.model is None
        assert result.trim is None
        assert result.make == "BMW"

    def test_model_dump_with_alias(self):
        """Test model_dump returns aliases when by_alias=True"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            make="BMW",
            model="X3",
        )

        dumped = result.model_dump(by_alias=True)
        assert "VIN" in dumped
        assert "Make" in dumped
        assert "Model" in dumped

    def test_model_dump_without_alias(self):
        """Test model_dump returns field names when by_alias=False"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            make="BMW",
            model="X3",
        )

        dumped = result.model_dump(by_alias=False)
        assert "vin" in dumped
        assert "make" in dumped
        assert "model" in dumped

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed and preserved"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            make="BMW",
            extra_field="extra_value",
            another_field="another_value",
        )

        # Extra fields should be stored
        dumped = result.model_dump()
        assert "extra_field" in dumped
        assert "another_field" in dumped

    def test_populate_by_name(self):
        """Test that both alias and field name work"""
        # Using alias
        result1 = VINDecodeResult(VIN="5UXWX7C50BA123456")
        # Using field name
        result2 = VINDecodeResult(vin="5UXWX7C50BA123456")

        assert result1.vin == result2.vin

    def test_all_fields_optional(self):
        """Test that all fields are optional"""
        result = VINDecodeResult()

        # Check all main fields are None by default
        assert result.vin is None
        assert result.make is None
        assert result.model is None
        assert result.model_year is None
        assert result.manufacturer is None

    def test_field_types_are_strings(self):
        """Test that all fields accept string values"""
        result = VINDecodeResult(
            vin="123",
            make="456",
            model_year="2011",
            doors="4",
            engine_cylinders="6",
        )

        assert isinstance(result.vin, str)
        assert isinstance(result.make, str)
        assert isinstance(result.model_year, str)

    def test_safety_features(self):
        """Test safety feature fields"""
        result = VINDecodeResult(
            abs="Standard",
            esc="Standard",
            airbag_locations_front="Driver and Passenger",
            airbag_locations_curtain="All Rows",
        )

        assert result.abs == "Standard"
        assert result.esc == "Standard"
        assert result.airbag_locations_front == "Driver and Passenger"

    def test_manufacturing_info(self):
        """Test manufacturing information fields"""
        result = VINDecodeResult(
            plant_city="Spartanburg",
            plant_country="UNITED STATES (USA)",
            plant_state="South Carolina",
            plant_company="BMW Manufacturing",
        )

        assert result.plant_city == "Spartanburg"
        assert result.plant_country == "UNITED STATES (USA)"
        assert result.plant_state == "South Carolina"

    def test_error_fields(self):
        """Test error handling fields"""
        result = VINDecodeResult(
            error_code="0",
            error_text="VIN decoded clean",
            additional_error_text="",
        )

        assert result.error_code == "0"
        assert result.error_text == "VIN decoded clean"
        assert result.additional_error_text is None  # Empty string converted

    def test_drivetrain_fields(self):
        """Test drivetrain related fields"""
        result = VINDecodeResult(
            engine_model="N52 B30",
            engine_cylinders="6",
            displacement_liters="3.0",
            displacement_cc="2996",
            displacement_ci="182.8",
            fuel_type="Gasoline",
            transmission_style="Automatic",
            drive_type="AWD",
        )

        assert result.engine_model == "N52 B30"
        assert result.engine_cylinders == "6"
        assert result.displacement_liters == "3.0"
        assert result.fuel_type == "Gasoline"

    @given(
        st.text(min_size=0, max_size=100),
        st.text(min_size=0, max_size=100),
        st.text(min_size=0, max_size=100),
    )
    def test_fuzzing_string_fields(self, vin, make, model):
        """Fuzz test with random string values"""
        # Empty strings should become None
        expected_vin = None if not vin.strip() else vin
        expected_make = None if not make.strip() else make
        expected_model = None if not model.strip() else model

        result = VINDecodeResult(vin=vin, make=make, model=model)

        assert result.vin == expected_vin
        assert result.make == expected_make
        assert result.model == expected_model

    def test_serialization_roundtrip(self, sample_vin_result):
        """Test that model can be serialized and deserialized"""
        # Serialize
        data = sample_vin_result.model_dump()

        # Deserialize
        result = VINDecodeResult(**data)

        assert result.vin == sample_vin_result.vin
        assert result.make == sample_vin_result.make
        assert result.model == sample_vin_result.model

    def test_json_serialization(self, sample_vin_result):
        """Test JSON serialization"""
        json_str = sample_vin_result.model_dump_json()
        assert isinstance(json_str, str)
        assert "5UXWX7C50BA123456" in json_str
        assert "BMW" in json_str

    def test_none_values_preserved(self):
        """Test that None values are preserved"""
        result = VINDecodeResult(
            vin="5UXWX7C50BA123456",
            make="BMW",
            model=None,
            trim=None,
        )

        assert result.model is None
        assert result.trim is None
        assert result.vin == "5UXWX7C50BA123456"

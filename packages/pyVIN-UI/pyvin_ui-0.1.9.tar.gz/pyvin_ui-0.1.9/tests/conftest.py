"""Pytest configuration and shared fixtures"""

import pytest
from src.api.models import VINDecodeResult


@pytest.fixture
def valid_vin():
    """Valid VIN for testing"""
    return "5UXWX7C50BA123456"


@pytest.fixture
def valid_vin_lowercase():
    """Valid VIN in lowercase"""
    return "5uxwx7c50ba123456"


@pytest.fixture
def invalid_vin_short():
    """Invalid VIN - too short"""
    return "5UXWX7C50BA"


@pytest.fixture
def invalid_vin_long():
    """Invalid VIN - too long"""
    return "5UXWX7C50BA1234567890"


@pytest.fixture
def invalid_vin_with_i():
    """Invalid VIN - contains I"""
    return "5UXWX7C50BI123456"


@pytest.fixture
def invalid_vin_with_o():
    """Invalid VIN - contains O"""
    return "5UXWX7C50BO123456"


@pytest.fixture
def invalid_vin_with_q():
    """Invalid VIN - contains Q"""
    return "5UXWX7C50BQ123456"


@pytest.fixture
def sample_api_response():
    """Sample NHTSA API response data"""
    return {
        "Count": 1,
        "Message": "Results returned successfully ...",
        "SearchCriteria": "VIN:5UXWX7C50BA",
        "Results": [
            {
                "VIN": "5UXWX7C50BA123456",
                "Make": "BMW",
                "Model": "X3",
                "ModelYear": "2011",
                "Manufacturer": "BMW MANUFACTURER CORPORATION",
                "BodyClass": "Sport Utility Vehicle (SUV)/Multi-Purpose Vehicle (MPV)",
                "VehicleType": "MULTIPURPOSE PASSENGER VEHICLE (MPV)",
                "Doors": "4",
                "EngineModel": "N52 B30",
                "EngineCylinders": "6",
                "DisplacementL": "3.0",
                "DisplacementCC": "2996",
                "DisplacementCI": "182.8",
                "FuelTypePrimary": "Gasoline",
                "TransmissionStyle": "Automatic",
                "DriveType": "AWD/4-Wheel Drive/4x4",
                "ABS": "Standard",
                "ESC": "Standard",
                "PlantCity": "Spartanburg",
                "PlantCountry": "UNITED STATES (USA)",
                "PlantState": "South Carolina",
                "ErrorCode": "0",
                "ErrorText": "0 - VIN decoded clean. Check Digit (9th position) is correct",
                "AdditionalErrorText": "",
                "Trim": "",  # Empty string should be filtered
                "MakeID": "",  # Empty string should be filtered
            }
        ],
    }


@pytest.fixture
def sample_vin_result():
    """Sample VINDecodeResult object"""
    return VINDecodeResult(
        vin="5UXWX7C50BA123456",
        make="BMW",
        model="X3",
        model_year="2011",
        manufacturer="BMW MANUFACTURER CORPORATION",
        body_class="Sport Utility Vehicle (SUV)/Multi-Purpose Vehicle (MPV)",
        vehicle_type="MULTIPURPOSE PASSENGER VEHICLE (MPV)",
        doors="4",
        engine_model="N52 B30",
        engine_cylinders="6",
        displacement_liters="3.0",
        fuel_type="Gasoline",
        transmission_style="Automatic",
        drive_type="AWD/4-Wheel Drive/4x4",
        abs="Standard",
        esc="Standard",
        plant_city="Spartanburg",
        plant_country="UNITED STATES (USA)",
        plant_state="South Carolina",
    )


@pytest.fixture
def sample_vin_result_with_nulls():
    """Sample VINDecodeResult with some null fields"""
    return VINDecodeResult(
        vin="5UXWX7C50BA123456",
        make="BMW",
        model="X3",
        model_year="2011",
        manufacturer=None,  # Null field
        body_class=None,  # Null field
        doors="4",
        engine_cylinders="6",
    )

"""Pydantic models for NHTSA VIN decode API responses."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class VINDecodeResult(BaseModel):
    """Pydantic model for NHTSA DecodeVinValuesExtended response"""

    # vehicle identity fields
    vin: Optional[str] = Field(
        None, alias="VIN", description="Vehicle Identification Number"
    )
    make: Optional[str] = Field(None, alias="Make", description="Vehicle make")
    model: Optional[str] = Field(None, alias="Model", description="Vehicle model")
    model_year: Optional[str] = Field(
        None, alias="ModelYear", description="Vehicle model year"
    )
    manufacturer: Optional[str] = Field(
        None, alias="Manufacturer", description="Vehicle manufacturer"
    )
    make_id: Optional[str] = Field(None, alias="MakeID", description="Vehicle make ID")
    model_id: Optional[str] = Field(
        None, alias="ModelID", description="Vehicle model ID"
    )
    manufacturer_id: Optional[str] = Field(
        None, alias="ManufacturerID", description="Vehicle manufacturer ID"
    )

    # Vehicle Specs
    body_class: Optional[str] = Field(
        None, alias="BodyClass", description="Vehicle body class"
    )
    vehicle_type: Optional[str] = Field(
        None, alias="VehicleType", description="Vehicle type"
    )
    doors: Optional[str] = Field(None, alias="Doors", description="Number of doors")
    trim: Optional[str] = Field(None, alias="Trim", description="Vehicle trim")
    trim_alt: Optional[str] = Field(None, alias="Trim2", description="Vehicle trim alt")
    axles: Optional[str] = Field(None, alias="Axles", description="Number of axles")
    axle_configuration: Optional[str] = Field(
        None, alias="AxleConfiguration", description="Axle configuration"
    )
    body_cab_type: Optional[str] = Field(
        None, alias="BodyCabType", description="Body cab type"
    )
    bed_type: Optional[str] = Field(None, alias="BedType", description="Bed type")
    bed_length_in: Optional[str] = Field(
        None, alias="BedLengthIn", description="Bed length in inches"
    )
    bus_type: Optional[str] = Field(None, alias="BusType", description="Bus type")
    bus_floor_config: Optional[str] = Field(
        None, alias="BusFloorConfigType", description="Bus floor configuration"
    )
    bus_length: Optional[str] = Field(
        None, alias="BusLength", description="Bus length in inches"
    )
    custom_motorcycle_type: Optional[str] = Field(
        None, alias="CustomMotorcycleType", description="Custom motorcycle type"
    )

    # Drivetrain
    engine_model: Optional[str] = Field(
        None, alias="EngineModel", description="Engine model"
    )
    engine_cylinders: Optional[str] = Field(
        None, alias="EngineCylinders", description="Number of engine cylinders"
    )
    displacement_liters: Optional[str] = Field(
        None, alias="DisplacementL", description="Engine displacement in liters"
    )
    displacement_cc: Optional[str] = Field(
        None,
        alias="DisplacementCC",
        description="Engine displacement in cubic centimeters",
    )
    displacement_ci: Optional[str] = Field(
        None, alias="DisplacementCI", description="Engine displacement in cubic inches"
    )
    fuel_type: Optional[str] = Field(
        None, alias="FuelTypePrimary", description="Primary fuel type"
    )
    transmission_style: Optional[str] = Field(
        None, alias="TransmissionStyle", description="Transmission style"
    )
    drive_type: Optional[str] = Field(None, alias="DriveType", description="Drive type")

    # Safety
    abs: Optional[str] = Field(
        None, alias="ABS", description="Anti-lock braking system (ABS) presence"
    )
    esc: Optional[str] = Field(
        None, alias="ESC", description="Electronic stability control (ESC) presence"
    )
    airbag_locations_front: Optional[str] = Field(
        None, alias="AirBagLocFront", description="Airbag locations in the front"
    )
    airbag_locations_curtain: Optional[str] = Field(
        None, alias="AirBagLocCurtain", description="Curtain Airbag locations"
    )
    airbag_locations_knee: Optional[str] = Field(
        None, alias="AirBagLocKnee", description="Knee Airbag locations"
    )
    airbag_locations_seat: Optional[str] = Field(
        None, alias="AirBagLocSeatCushion", description="Seat Cushion Airbag locations"
    )
    airbag_locations_side: Optional[str] = Field(
        None, alias="AirBagLocSide", description="Side Airbag locations"
    )

    # Manufacturing
    plant_city: Optional[str] = Field(
        None, alias="PlantCity", description="City where vehicle was manufactured"
    )
    plant_country: Optional[str] = Field(
        None, alias="PlantCountry", description="Country where vehicle was manufactured"
    )
    plant_state: Optional[str] = Field(
        None, alias="PlantState", description="State where vehicle was manufactured"
    )
    plant_company: Optional[str] = Field(
        None, alias="PlantCompanyName", description="Company that manufactured"
    )

    # Error handling and suggestions
    error_code: Optional[str] = Field(
        None, alias="ErrorCode", description="Error code from NHTSA API"
    )
    error_text: Optional[str] = Field(
        None, alias="ErrorText", description="Error text from NHTSA API"
    )
    additional_error_text: Optional[str] = Field(
        None,
        alias="AdditionalErrorText",
        description="Additional Error text from NHTSA API",
    )
    suggested_vin: Optional[str] = Field(
        None, alias="SuggestedVIN", description="Suggested VIN from NHTSA API"
    )
    possible_values: Optional[str] = Field(
        None, alias="PossibleValues", description="Possible values for VIN positions"
    )

    class Config:
        populate_by_name = True  # Allow both alias and field name
        extra = "allow"  # Keep extra fields we didn't explicitly define

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


__all__ = ["VINDecodeResult"]

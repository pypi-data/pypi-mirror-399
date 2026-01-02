"""Tests for field mapping module"""

from hypothesis import given, strategies as st
from src.formatting.fields import FIELD_LABELS, FIELD_DESCRIPTIONS


class TestFieldLabels:
    """Tests for FIELD_LABELS mapping"""

    def test_field_labels_is_dict(self):
        """Test that FIELD_LABELS is a dictionary"""
        assert isinstance(FIELD_LABELS, dict)

    def test_field_labels_not_empty(self):
        """Test that FIELD_LABELS has entries"""
        assert len(FIELD_LABELS) > 0

    def test_basic_identity_fields_exist(self):
        """Test that basic identity fields are mapped"""
        required_fields = ["vin", "make", "model", "model_year", "manufacturer"]
        for field in required_fields:
            assert field in FIELD_LABELS

    def test_labels_are_human_readable(self):
        """Test that labels are properly formatted"""
        # Check some key fields have proper labels
        assert FIELD_LABELS["vin"] == "VIN"
        assert FIELD_LABELS["make"] == "Make"
        assert FIELD_LABELS["model"] == "Model"
        assert FIELD_LABELS["model_year"] == "Model Year"

    def test_no_empty_labels(self):
        """Test that no labels are empty strings"""
        for label in FIELD_LABELS.values():
            assert label
            assert label.strip() != ""

    def test_labels_are_title_case_or_uppercase(self):
        """Test that labels use proper capitalization"""
        for label in FIELD_LABELS.values():
            # Should be title case or all uppercase (like VIN, ABS, ESC)
            assert label[0].isupper() or label.isupper()

    def test_drivetrain_fields_mapped(self):
        """Test that drivetrain fields are mapped"""
        drivetrain_fields = [
            "engine_model",
            "engine_cylinders",
            "displacement_liters",
            "fuel_type",
            "transmission_style",
            "drive_type",
        ]
        for field in drivetrain_fields:
            assert field in FIELD_LABELS
            assert FIELD_LABELS[field]

    def test_safety_fields_mapped(self):
        """Test that safety fields are mapped"""
        safety_fields = [
            "abs",
            "esc",
            "airbag_locations_front",
            "airbag_locations_curtain",
        ]
        for field in safety_fields:
            assert field in FIELD_LABELS
            assert FIELD_LABELS[field]

    def test_manufacturing_fields_mapped(self):
        """Test that manufacturing fields are mapped"""
        manufacturing_fields = [
            "plant_city",
            "plant_country",
            "plant_state",
            "plant_company",
        ]
        for field in manufacturing_fields:
            assert field in FIELD_LABELS
            assert FIELD_LABELS[field]

    def test_acronyms_are_uppercase(self):
        """Test that known acronyms are all uppercase"""
        acronyms = ["VIN", "ABS", "ESC"]
        for acronym in acronyms:
            assert acronym in FIELD_LABELS.values()

    def test_units_in_labels(self):
        """Test that units are included in labels where appropriate"""
        # Check that displacement fields have unit indicators
        assert (
            "L" in FIELD_LABELS["displacement_liters"]
            or "Liter" in FIELD_LABELS["displacement_liters"]
        )
        assert (
            "cc" in FIELD_LABELS["displacement_cc"]
            or "Cubic" in FIELD_LABELS["displacement_cc"]
        )
        assert (
            "in" in FIELD_LABELS["bed_length_in"]
            or "inch" in FIELD_LABELS["bed_length_in"].lower()
        )


class TestFieldDescriptions:
    """Tests for FIELD_DESCRIPTIONS mapping"""

    def test_field_descriptions_is_dict(self):
        """Test that FIELD_DESCRIPTIONS is a dictionary"""
        assert isinstance(FIELD_DESCRIPTIONS, dict)

    def test_field_descriptions_not_empty(self):
        """Test that FIELD_DESCRIPTIONS has entries"""
        assert len(FIELD_DESCRIPTIONS) > 0

    def test_descriptions_match_labels_keys(self):
        """Test that all fields in FIELD_LABELS have descriptions"""
        for field in FIELD_LABELS.keys():
            assert field in FIELD_DESCRIPTIONS, f"Field {field} missing description"

    def test_descriptions_are_strings(self):
        """Test that all descriptions are strings"""
        for desc in FIELD_DESCRIPTIONS.values():
            assert isinstance(desc, str)

    def test_descriptions_are_not_empty(self):
        """Test that descriptions are not empty"""
        for field, desc in FIELD_DESCRIPTIONS.items():
            assert desc, f"Description for {field} is empty"
            assert desc.strip() != "", f"Description for {field} is whitespace"

    def test_basic_descriptions_exist(self):
        """Test that basic fields have proper descriptions"""
        assert "Vehicle Identification Number" in FIELD_DESCRIPTIONS["vin"]
        assert "make" in FIELD_DESCRIPTIONS["make"].lower()
        assert "model" in FIELD_DESCRIPTIONS["model"].lower()
        assert "year" in FIELD_DESCRIPTIONS["model_year"].lower()

    def test_descriptions_are_descriptive(self):
        """Test that descriptions are sufficiently descriptive"""
        for desc in FIELD_DESCRIPTIONS.values():
            # Descriptions should be at least 8 characters
            assert len(desc) >= 8

    def test_drivetrain_descriptions_exist(self):
        """Test that drivetrain fields have descriptions"""
        drivetrain_fields = [
            "engine_model",
            "engine_cylinders",
            "displacement_liters",
            "fuel_type",
        ]
        for field in drivetrain_fields:
            assert field in FIELD_DESCRIPTIONS
            assert FIELD_DESCRIPTIONS[field]
            assert (
                "engine" in FIELD_DESCRIPTIONS[field].lower()
                or "fuel" in FIELD_DESCRIPTIONS[field].lower()
            )

    def test_safety_descriptions_exist(self):
        """Test that safety fields have descriptions"""
        safety_fields = ["abs", "esc", "airbag_locations_front"]
        for field in safety_fields:
            assert field in FIELD_DESCRIPTIONS
            assert FIELD_DESCRIPTIONS[field]


class TestFieldMappingConsistency:
    """Tests for consistency between labels and descriptions"""

    def test_same_keys_in_both_dicts(self):
        """Test that FIELD_LABELS and FIELD_DESCRIPTIONS have same keys"""
        label_keys = set(FIELD_LABELS.keys())
        desc_keys = set(FIELD_DESCRIPTIONS.keys())

        assert label_keys == desc_keys, (
            f"Mismatched keys: {label_keys.symmetric_difference(desc_keys)}"
        )

    def test_all_pydantic_model_fields_covered(self):
        """Test that common VINDecodeResult fields are mapped"""
        # These are the main fields from VINDecodeResult
        expected_fields = [
            "vin",
            "make",
            "model",
            "model_year",
            "manufacturer",
            "body_class",
            "vehicle_type",
            "doors",
            "engine_model",
            "engine_cylinders",
            "displacement_liters",
            "fuel_type",
            "transmission_style",
            "drive_type",
            "abs",
            "esc",
            "plant_city",
            "plant_country",
            "error_code",
            "error_text",
        ]

        for field in expected_fields:
            assert field in FIELD_LABELS, f"Field {field} not in FIELD_LABELS"
            assert field in FIELD_DESCRIPTIONS, (
                f"Field {field} not in FIELD_DESCRIPTIONS"
            )

    def test_no_duplicate_labels(self):
        """Test that no two fields map to the same label"""
        labels = list(FIELD_LABELS.values())
        unique_labels = set(labels)

        # Some fields might legitimately have the same label, but check for suspicious duplicates
        assert len(unique_labels) > len(labels) * 0.9, "Too many duplicate labels"

    @given(st.sampled_from(list(FIELD_LABELS.keys())))
    def test_fuzzing_field_access(self, field):
        """Fuzz test accessing random fields"""
        # Should not raise any errors
        label = FIELD_LABELS[field]
        description = FIELD_DESCRIPTIONS[field]

        assert isinstance(label, str)
        assert isinstance(description, str)
        assert label
        assert description


class TestFieldLabelFormatting:
    """Tests for label formatting consistency"""

    def test_labels_dont_have_trailing_spaces(self):
        """Test that labels don't have trailing spaces"""
        for field, label in FIELD_LABELS.items():
            assert label == label.strip(), f"Label for {field} has extra whitespace"

    def test_labels_dont_have_underscores(self):
        """Test that labels use spaces not underscores"""
        for field, label in FIELD_LABELS.items():
            # Some exceptions for technical terms
            if field not in ["vin"]:  # VIN is an acronym
                assert "_" not in label, f"Label for {field} contains underscore"

    def test_descriptions_are_sentences(self):
        """Test that descriptions are proper sentences or phrases"""
        for desc in FIELD_DESCRIPTIONS.values():
            # Should start with capital letter
            assert desc[0].isupper(), f"Description doesn't start with capital: {desc}"

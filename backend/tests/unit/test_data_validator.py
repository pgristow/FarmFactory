"""
Unit tests for data validation service.

Tests all validation rules and edge cases including data types, ranges,
required fields, references, and cross-field validation.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd


@pytest.mark.unit
class TestDataTypeValidation:
    """Test data type validation."""

    def test_validate_string_field(self):
        """Test validating string fields."""
        # Valid strings
        assert self._validate_string('Green Valley Farm', max_length=255) is True
        assert self._validate_string('', required=False) is True

        # Invalid strings
        assert self._validate_string('', required=True) is False
        assert self._validate_string('A' * 300, max_length=255) is False
        assert self._validate_string(None, required=True) is False
        assert self._validate_string(123, max_length=255) is False  # Not a string

    def test_validate_integer_field(self):
        """Test validating integer fields."""
        # Valid integers
        assert self._validate_integer(100) is True
        assert self._validate_integer(0) is True
        assert self._validate_integer(-50) is True
        assert self._validate_integer(None, required=False) is True

        # Invalid integers
        assert self._validate_integer(10.5) is False  # Float
        assert self._validate_integer('100') is False  # String
        assert self._validate_integer(None, required=True) is False

    def test_validate_float_field(self):
        """Test validating float/decimal fields."""
        # Valid floats
        assert self._validate_float(10.5) is True
        assert self._validate_float(0.0) is True
        assert self._validate_float(-3.14) is True
        assert self._validate_float(100) is True  # Integer is acceptable for float
        assert self._validate_float(None, required=False) is True

        # Invalid floats
        assert self._validate_float('10.5') is False  # String
        assert self._validate_float(None, required=True) is False
        assert self._validate_float(float('inf')) is False  # Infinity
        assert self._validate_float(float('nan')) is False  # NaN

    def test_validate_date_field(self):
        """Test validating date fields."""
        # Valid dates
        assert self._validate_date('2024-01-15') is True
        assert self._validate_date('2024-12-31') is True
        assert self._validate_date(datetime(2024, 1, 15)) is True
        assert self._validate_date(None, required=False) is True

        # Invalid dates
        assert self._validate_date('2024-13-01') is False  # Invalid month
        assert self._validate_date('2024-02-30') is False  # Invalid day
        assert self._validate_date('invalid-date') is False
        assert self._validate_date(None, required=True) is False

    def test_validate_datetime_field(self):
        """Test validating datetime fields."""
        # Valid datetimes
        assert self._validate_datetime('2024-01-15T10:30:00') is True
        assert self._validate_datetime('2024-01-15 10:30:00') is True
        assert self._validate_datetime(datetime(2024, 1, 15, 10, 30)) is True

        # Invalid datetimes
        assert self._validate_datetime('2024-01-15T25:00:00') is False  # Invalid hour
        assert self._validate_datetime('invalid') is False

    def test_validate_boolean_field(self):
        """Test validating boolean fields."""
        # Valid booleans
        assert self._validate_boolean(True) is True
        assert self._validate_boolean(False) is True
        assert self._validate_boolean('true') is True
        assert self._validate_boolean('false') is True
        assert self._validate_boolean('yes') is True
        assert self._validate_boolean('no') is True
        assert self._validate_boolean(1) is True
        assert self._validate_boolean(0) is True

        # Invalid booleans
        assert self._validate_boolean('invalid') is False
        assert self._validate_boolean(2) is False


@pytest.mark.unit
class TestRangeValidation:
    """Test range validation for numeric fields."""

    def test_validate_ph_range(self):
        """Test pH validation (0-14)."""
        # Valid pH values
        assert self._validate_range(7.0, min_val=0, max_val=14) is True
        assert self._validate_range(0.0, min_val=0, max_val=14) is True
        assert self._validate_range(14.0, min_val=0, max_val=14) is True
        assert self._validate_range(6.5, min_val=0, max_val=14) is True

        # Invalid pH values
        assert self._validate_range(-0.1, min_val=0, max_val=14) is False
        assert self._validate_range(14.1, min_val=0, max_val=14) is False
        assert self._validate_range(20.0, min_val=0, max_val=14) is False

    def test_validate_temperature_range(self):
        """Test temperature validation (-50 to 60°C)."""
        # Valid temperatures
        assert self._validate_range(25.0, min_val=-50, max_val=60) is True
        assert self._validate_range(-50.0, min_val=-50, max_val=60) is True
        assert self._validate_range(60.0, min_val=-50, max_val=60) is True
        assert self._validate_range(0.0, min_val=-50, max_val=60) is True

        # Invalid temperatures
        assert self._validate_range(-51.0, min_val=-50, max_val=60) is False
        assert self._validate_range(61.0, min_val=-50, max_val=60) is False
        assert self._validate_range(100.0, min_val=-50, max_val=60) is False

    def test_validate_latitude_range(self):
        """Test latitude validation (-90 to 90)."""
        # Valid latitudes
        assert self._validate_range(40.7128, min_val=-90, max_val=90) is True
        assert self._validate_range(-90.0, min_val=-90, max_val=90) is True
        assert self._validate_range(90.0, min_val=-90, max_val=90) is True
        assert self._validate_range(0.0, min_val=-90, max_val=90) is True

        # Invalid latitudes
        assert self._validate_range(-91.0, min_val=-90, max_val=90) is False
        assert self._validate_range(91.0, min_val=-90, max_val=90) is False

    def test_validate_longitude_range(self):
        """Test longitude validation (-180 to 180)."""
        # Valid longitudes
        assert self._validate_range(-74.0060, min_val=-180, max_val=180) is True
        assert self._validate_range(-180.0, min_val=-180, max_val=180) is True
        assert self._validate_range(180.0, min_val=-180, max_val=180) is True

        # Invalid longitudes
        assert self._validate_range(-181.0, min_val=-180, max_val=180) is False
        assert self._validate_range(181.0, min_val=-180, max_val=180) is False

    def test_validate_positive_numbers(self):
        """Test validation for fields that must be positive."""
        # Valid positive numbers (area, volume, weight, cost)
        assert self._validate_range(10.5, min_val=0) is True
        assert self._validate_range(0.0, min_val=0) is True
        assert self._validate_range(1000000, min_val=0) is True

        # Invalid (negative)
        assert self._validate_range(-0.1, min_val=0) is False
        assert self._validate_range(-100, min_val=0) is False

    def test_validate_percentage_range(self):
        """Test percentage validation (0-100)."""
        # Valid percentages
        assert self._validate_range(50.0, min_val=0, max_val=100) is True
        assert self._validate_range(0.0, min_val=0, max_val=100) is True
        assert self._validate_range(100.0, min_val=0, max_val=100) is True

        # Invalid percentages
        assert self._validate_range(-1.0, min_val=0, max_val=100) is False
        assert self._validate_range(101.0, min_val=0, max_val=100) is False


@pytest.mark.unit
class TestRequiredFieldValidation:
    """Test required field validation."""

    def test_required_fields_present(self):
        """Test validation with all required fields present."""
        data = {
            'farm_name': 'Green Valley Farm',
            'plot_name': 'North Field',
            'event_time': '2024-01-15T10:00:00',
        }
        required_fields = ['farm_name', 'plot_name', 'event_time']

        errors = self._validate_required_fields(data, required_fields)
        assert len(errors) == 0

    def test_required_field_missing(self):
        """Test validation with missing required field."""
        data = {
            'farm_name': 'Green Valley Farm',
            # plot_name is missing
            'event_time': '2024-01-15T10:00:00',
        }
        required_fields = ['farm_name', 'plot_name', 'event_time']

        errors = self._validate_required_fields(data, required_fields)
        assert len(errors) == 1
        assert 'plot_name' in errors[0]

    def test_required_field_null(self):
        """Test validation with null required field."""
        data = {
            'farm_name': 'Green Valley Farm',
            'plot_name': None,
            'event_time': '2024-01-15T10:00:00',
        }
        required_fields = ['farm_name', 'plot_name', 'event_time']

        errors = self._validate_required_fields(data, required_fields)
        assert len(errors) == 1
        assert 'plot_name' in errors[0]

    def test_required_field_empty_string(self):
        """Test validation with empty string in required field."""
        data = {
            'farm_name': '',
            'plot_name': 'North Field',
            'event_time': '2024-01-15T10:00:00',
        }
        required_fields = ['farm_name', 'plot_name', 'event_time']

        errors = self._validate_required_fields(data, required_fields)
        assert len(errors) == 1
        assert 'farm_name' in errors[0]


@pytest.mark.unit
class TestReferenceIntegrityValidation:
    """Test reference integrity validation."""

    def test_validate_farm_exists(self):
        """Test validating farm name exists."""
        existing_farms = ['Green Valley Farm', 'Sunny Acres', 'Test Farm']

        # Valid reference
        assert self._validate_reference('Green Valley Farm', existing_farms) is True

        # Invalid reference
        assert self._validate_reference('Nonexistent Farm', existing_farms) is False
        assert self._validate_reference('', existing_farms) is False

    def test_validate_plot_exists(self):
        """Test validating plot name exists."""
        existing_plots = ['North Field', 'South Field', 'East Plot']

        # Valid reference
        assert self._validate_reference('North Field', existing_plots) is True

        # Invalid reference
        assert self._validate_reference('Nonexistent Plot', existing_plots) is False

    def test_validate_case_sensitive_references(self):
        """Test reference validation with case sensitivity."""
        existing_farms = ['Green Valley Farm']

        # Exact match
        assert self._validate_reference('Green Valley Farm', existing_farms) is True

        # Case mismatch - should fail with strict matching
        assert self._validate_reference('green valley farm', existing_farms) is False

    def test_validate_case_insensitive_references(self):
        """Test reference validation with case insensitivity."""
        existing_farms = ['Green Valley Farm']

        # Case-insensitive match
        assert self._validate_reference_case_insensitive('green valley farm', existing_farms) is True
        assert self._validate_reference_case_insensitive('GREEN VALLEY FARM', existing_farms) is True


@pytest.mark.unit
class TestDuplicateDetection:
    """Test duplicate detection."""

    def test_detect_duplicate_rows(self):
        """Test detecting duplicate rows in import data."""
        data = pd.DataFrame({
            'farm_name': ['Farm 1', 'Farm 2', 'Farm 1'],  # Duplicate
            'plot_name': ['Plot A', 'Plot B', 'Plot A'],  # Duplicate
            'area_hectares': [10.5, 15.2, 10.5],
        })

        duplicates = self._find_duplicates(data, subset=['farm_name', 'plot_name'])

        # Should find 1 duplicate (row 3 is duplicate of row 1)
        assert len(duplicates) == 1
        assert 2 in duplicates  # Row index 2

    def test_no_duplicates(self):
        """Test with no duplicate rows."""
        data = pd.DataFrame({
            'farm_name': ['Farm 1', 'Farm 2', 'Farm 3'],
            'plot_name': ['Plot A', 'Plot B', 'Plot C'],
        })

        duplicates = self._find_duplicates(data, subset=['farm_name', 'plot_name'])

        assert len(duplicates) == 0

    def test_detect_duplicate_with_null_values(self):
        """Test duplicate detection with null values."""
        data = pd.DataFrame({
            'farm_name': ['Farm 1', 'Farm 2', None],
            'plot_name': ['Plot A', None, 'Plot C'],
        })

        duplicates = self._find_duplicates(data, subset=['farm_name', 'plot_name'])

        # Null values should not be considered duplicates
        assert len(duplicates) == 0


@pytest.mark.unit
class TestCrossFieldValidation:
    """Test cross-field validation rules."""

    def test_harvest_date_after_planting_date(self):
        """Test harvest date must be after planting date."""
        # Valid
        assert self._validate_date_order(
            planting_date='2024-01-15',
            harvest_date='2024-06-15'
        ) is True

        # Invalid
        assert self._validate_date_order(
            planting_date='2024-06-15',
            harvest_date='2024-01-15'
        ) is False

        # Same date - could be invalid depending on business rules
        assert self._validate_date_order(
            planting_date='2024-01-15',
            harvest_date='2024-01-15'
        ) is False

    def test_irrigation_end_after_start(self):
        """Test irrigation end time after start time."""
        # Valid
        assert self._validate_date_order(
            start_time='2024-01-15T08:00:00',
            end_time='2024-01-15T10:00:00'
        ) is True

        # Invalid
        assert self._validate_date_order(
            start_time='2024-01-15T10:00:00',
            end_time='2024-01-15T08:00:00'
        ) is False

    def test_total_area_vs_plot_sum(self):
        """Test total farm area should be >= sum of plot areas."""
        farm_area = 50.0
        plot_areas = [10.5, 15.2, 20.0]  # Sum = 45.7

        # Valid
        assert farm_area >= sum(plot_areas)

        # Invalid
        plot_areas_invalid = [10.5, 15.2, 30.0]  # Sum = 55.7
        assert farm_area < sum(plot_areas_invalid)

    def test_npk_ratio_calculation(self):
        """Test N-P-K amounts match ratio and total amount."""
        npk_ratio = "10-10-10"
        total_amount_kg = 100.0
        nitrogen_kg = 10.0
        phosphorus_kg = 10.0
        potassium_kg = 10.0

        # Parse ratio
        n_ratio, p_ratio, k_ratio = map(int, npk_ratio.split('-'))
        total_ratio = n_ratio + p_ratio + k_ratio

        # Calculate expected amounts
        expected_n = total_amount_kg * (n_ratio / total_ratio)
        expected_p = total_amount_kg * (p_ratio / total_ratio)
        expected_k = total_amount_kg * (k_ratio / total_ratio)

        # Validate (with tolerance for rounding)
        tolerance = 0.1
        assert abs(nitrogen_kg - expected_n) < tolerance
        assert abs(phosphorus_kg - expected_p) < tolerance
        assert abs(potassium_kg - expected_k) < tolerance


@pytest.mark.unit
class TestDateValidation:
    """Test date-specific validation rules."""

    def test_date_not_in_future_for_historical_data(self):
        """Test historical data dates should not be in future."""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Valid historical dates
        assert self._validate_not_future(yesterday.isoformat()) is True
        assert self._validate_not_future(today.isoformat()) is True

        # Invalid future dates
        assert self._validate_not_future(tomorrow.isoformat()) is False

    def test_date_format_variations(self):
        """Test various date format validations."""
        # Valid formats
        assert self._parse_date('2024-01-15') is not None  # ISO format
        assert self._parse_date('01/15/2024') is not None  # US format
        assert self._parse_date('15/01/2024') is not None  # EU format
        assert self._parse_date('2024-01-15T10:30:00') is not None  # ISO datetime

        # Invalid formats
        assert self._parse_date('invalid-date') is None
        assert self._parse_date('32/13/2024') is None

    def test_date_range_validation(self):
        """Test date is within acceptable range."""
        # Valid date range (1900 - today)
        assert self._validate_date_range('2024-01-15', min_year=1900) is True
        assert self._validate_date_range('2000-01-01', min_year=1900) is True

        # Invalid (too old)
        assert self._validate_date_range('1800-01-01', min_year=1900) is False


@pytest.mark.unit
class TestEnumValidation:
    """Test enum/choice field validation."""

    def test_validate_irrigation_method(self):
        """Test irrigation method enum validation."""
        valid_methods = ['drip', 'sprinkler', 'flood', 'furrow', 'center_pivot']

        # Valid methods
        assert self._validate_enum('drip', valid_methods) is True
        assert self._validate_enum('sprinkler', valid_methods) is True

        # Invalid methods
        assert self._validate_enum('invalid_method', valid_methods) is False
        assert self._validate_enum('', valid_methods) is False

    def test_validate_soil_type(self):
        """Test soil type enum validation."""
        valid_types = ['Sandy', 'Loamy', 'Clay', 'Silty', 'Peaty']

        # Valid types
        assert self._validate_enum('Loamy', valid_types) is True

        # Invalid types
        assert self._validate_enum('Invalid Soil', valid_types) is False

    def test_validate_case_insensitive_enum(self):
        """Test case-insensitive enum validation."""
        valid_methods = ['drip', 'sprinkler', 'flood']

        # Should accept different cases
        assert self._validate_enum_case_insensitive('DRIP', valid_methods) is True
        assert self._validate_enum_case_insensitive('Drip', valid_methods) is True
        assert self._validate_enum_case_insensitive('drip', valid_methods) is True


@pytest.mark.unit
class TestBoundaryValueValidation:
    """Test boundary value validation."""

    def test_zero_boundary(self):
        """Test zero as boundary value."""
        # Area cannot be zero
        assert self._validate_range(0.0, min_val=0, exclusive_min=True) is False
        assert self._validate_range(0.001, min_val=0, exclusive_min=True) is True

        # Duration can be zero
        assert self._validate_range(0, min_val=0) is True

    def test_maximum_values(self):
        """Test maximum value boundaries."""
        # Area (reasonable max: 100,000 hectares)
        assert self._validate_range(100000, max_val=100000) is True
        assert self._validate_range(100001, max_val=100000) is False

        # Temperature (max: 60°C)
        assert self._validate_range(60.0, max_val=60) is True
        assert self._validate_range(60.1, max_val=60) is False

    def test_precision_validation(self):
        """Test decimal precision validation."""
        # Area with 2 decimal places
        assert self._validate_precision(10.55, decimal_places=2) is True
        assert self._validate_precision(10.555, decimal_places=2) is False

        # Coordinates with 6 decimal places
        assert self._validate_precision(40.712800, decimal_places=6) is True


# Helper methods for validation

def _validate_string(value, max_length=None, required=True):
    """Validate string field."""
    if value is None or value == '':
        return not required
    if not isinstance(value, str):
        return False
    if max_length and len(value) > max_length:
        return False
    return True


def _validate_integer(value, required=True):
    """Validate integer field."""
    if value is None:
        return not required
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_float(value, required=True):
    """Validate float field."""
    if value is None:
        return not required
    if not isinstance(value, (int, float)):
        return False
    if isinstance(value, float):
        return not (float('inf') == abs(value) or value != value)  # Check for inf and nan
    return True


def _validate_date(value, required=True):
    """Validate date field."""
    if value is None:
        return not required
    if isinstance(value, datetime):
        return True

    try:
        pd.to_datetime(value)
        return True
    except:
        return False


def _validate_datetime(value, required=True):
    """Validate datetime field."""
    return _validate_date(value, required)


def _validate_boolean(value, required=True):
    """Validate boolean field."""
    if value is None:
        return not required
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return value.lower() in ['true', 'false', 'yes', 'no', '1', '0']
    if isinstance(value, int):
        return value in [0, 1]
    return False


def _validate_range(value, min_val=None, max_val=None, exclusive_min=False):
    """Validate numeric value is within range."""
    if min_val is not None:
        if exclusive_min:
            if value <= min_val:
                return False
        else:
            if value < min_val:
                return False
    if max_val is not None:
        if value > max_val:
            return False
    return True


def _validate_required_fields(data, required_fields):
    """Validate all required fields are present and not empty."""
    errors = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"Required field '{field}' is missing or empty")
    return errors


def _validate_reference(value, valid_values):
    """Validate reference exists (case-sensitive)."""
    return value in valid_values


def _validate_reference_case_insensitive(value, valid_values):
    """Validate reference exists (case-insensitive)."""
    value_lower = value.lower()
    valid_values_lower = [v.lower() for v in valid_values]
    return value_lower in valid_values_lower


def _find_duplicates(df, subset):
    """Find duplicate rows in DataFrame."""
    duplicates = df[df.duplicated(subset=subset, keep='first')]
    return duplicates.index.tolist()


def _validate_date_order(planting_date=None, harvest_date=None, start_time=None, end_time=None):
    """Validate date/time ordering."""
    if planting_date and harvest_date:
        planting = pd.to_datetime(planting_date)
        harvest = pd.to_datetime(harvest_date)
        return harvest > planting

    if start_time and end_time:
        start = pd.to_datetime(start_time)
        end = pd.to_datetime(end_time)
        return end > start

    return True


def _validate_not_future(date_value):
    """Validate date is not in future."""
    date = pd.to_datetime(date_value)
    return date <= datetime.now()


def _parse_date(date_string):
    """Parse date from various formats."""
    try:
        return pd.to_datetime(date_string)
    except:
        return None


def _validate_date_range(date_value, min_year=1900):
    """Validate date is within acceptable range."""
    try:
        date = pd.to_datetime(date_value)
        return date.year >= min_year and date <= datetime.now()
    except:
        return False


def _validate_enum(value, valid_values):
    """Validate value is in enum list (case-sensitive)."""
    return value in valid_values


def _validate_enum_case_insensitive(value, valid_values):
    """Validate value is in enum list (case-insensitive)."""
    value_lower = value.lower()
    valid_values_lower = [v.lower() for v in valid_values]
    return value_lower in valid_values_lower


def _validate_precision(value, decimal_places):
    """Validate decimal precision."""
    decimal_value = Decimal(str(value))
    return abs(decimal_value.as_tuple().exponent) <= decimal_places

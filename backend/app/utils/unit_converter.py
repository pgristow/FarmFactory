"""
Unit conversion utilities for FarmFactory data import system.

Provides conversions for common agricultural measurements:
- Area (acres <-> hectares <-> square meters)
- Volume (gallons <-> liters)
- Weight/Mass (pounds <-> kilograms)
- Temperature (Fahrenheit <-> Celsius)
- Length (feet <-> meters, inches <-> centimeters)
- Pressure (PSI <-> Bar)
- Flow rate (GPM <-> LPM)
"""

from typing import Optional, Union
from enum import Enum


class AreaUnit(Enum):
    """Area measurement units."""
    ACRES = "acres"
    HECTARES = "hectares"
    SQUARE_METERS = "square_meters"
    SQUARE_FEET = "square_feet"


class VolumeUnit(Enum):
    """Volume measurement units."""
    GALLONS = "gallons"
    LITERS = "liters"
    CUBIC_METERS = "cubic_meters"


class WeightUnit(Enum):
    """Weight/Mass measurement units."""
    POUNDS = "pounds"
    KILOGRAMS = "kilograms"
    GRAMS = "grams"
    TONS = "tons"
    METRIC_TONS = "metric_tons"


class TemperatureUnit(Enum):
    """Temperature measurement units."""
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"
    KELVIN = "kelvin"


class LengthUnit(Enum):
    """Length measurement units."""
    FEET = "feet"
    METERS = "meters"
    INCHES = "inches"
    CENTIMETERS = "centimeters"
    KILOMETERS = "kilometers"
    MILES = "miles"


class PressureUnit(Enum):
    """Pressure measurement units."""
    PSI = "psi"
    BAR = "bar"
    PASCAL = "pascal"
    KILOPASCAL = "kilopascal"


# Conversion factors
# Area conversions (to hectares)
ACRES_TO_HECTARES = 0.404686
HECTARES_TO_ACRES = 2.47105
SQ_METERS_TO_HECTARES = 0.0001
HECTARES_TO_SQ_METERS = 10000

# Volume conversions (to liters)
GALLONS_TO_LITERS = 3.78541
LITERS_TO_GALLONS = 0.264172
CUBIC_METERS_TO_LITERS = 1000

# Weight conversions (to kilograms)
POUNDS_TO_KG = 0.453592
KG_TO_POUNDS = 2.20462
GRAMS_TO_KG = 0.001
TONS_TO_KG = 907.185  # US ton
METRIC_TONS_TO_KG = 1000

# Length conversions (to meters)
FEET_TO_METERS = 0.3048
METERS_TO_FEET = 3.28084
INCHES_TO_CM = 2.54
CM_TO_INCHES = 0.393701
INCHES_TO_METERS = 0.0254
KILOMETERS_TO_METERS = 1000
MILES_TO_METERS = 1609.34

# Pressure conversions (to bar)
PSI_TO_BAR = 0.0689476
BAR_TO_PSI = 14.5038
PASCAL_TO_BAR = 0.00001
KILOPASCAL_TO_BAR = 0.01


class UnitConverter:
    """Unit conversion utility class."""

    # Area conversions
    @staticmethod
    def acres_to_hectares(acres: float) -> float:
        """Convert acres to hectares."""
        return acres * ACRES_TO_HECTARES

    @staticmethod
    def hectares_to_acres(hectares: float) -> float:
        """Convert hectares to acres."""
        return hectares * HECTARES_TO_ACRES

    @staticmethod
    def square_meters_to_hectares(sq_meters: float) -> float:
        """Convert square meters to hectares."""
        return sq_meters * SQ_METERS_TO_HECTARES

    @staticmethod
    def hectares_to_square_meters(hectares: float) -> float:
        """Convert hectares to square meters."""
        return hectares * HECTARES_TO_SQ_METERS

    # Volume conversions
    @staticmethod
    def gallons_to_liters(gallons: float) -> float:
        """Convert US gallons to liters."""
        return gallons * GALLONS_TO_LITERS

    @staticmethod
    def liters_to_gallons(liters: float) -> float:
        """Convert liters to US gallons."""
        return liters * LITERS_TO_GALLONS

    @staticmethod
    def cubic_meters_to_liters(cubic_meters: float) -> float:
        """Convert cubic meters to liters."""
        return cubic_meters * CUBIC_METERS_TO_LITERS

    @staticmethod
    def liters_to_cubic_meters(liters: float) -> float:
        """Convert liters to cubic meters."""
        return liters / CUBIC_METERS_TO_LITERS

    # Weight conversions
    @staticmethod
    def pounds_to_kg(pounds: float) -> float:
        """Convert pounds to kilograms."""
        return pounds * POUNDS_TO_KG

    @staticmethod
    def kg_to_pounds(kg: float) -> float:
        """Convert kilograms to pounds."""
        return kg * KG_TO_POUNDS

    @staticmethod
    def grams_to_kg(grams: float) -> float:
        """Convert grams to kilograms."""
        return grams * GRAMS_TO_KG

    @staticmethod
    def kg_to_grams(kg: float) -> float:
        """Convert kilograms to grams."""
        return kg / GRAMS_TO_KG

    @staticmethod
    def tons_to_kg(tons: float) -> float:
        """Convert US tons to kilograms."""
        return tons * TONS_TO_KG

    @staticmethod
    def metric_tons_to_kg(metric_tons: float) -> float:
        """Convert metric tons to kilograms."""
        return metric_tons * METRIC_TONS_TO_KG

    # Temperature conversions
    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """Convert Fahrenheit to Celsius."""
        return (fahrenheit - 32) * 5.0 / 9.0

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9.0 / 5.0) + 32

    @staticmethod
    def celsius_to_kelvin(celsius: float) -> float:
        """Convert Celsius to Kelvin."""
        return celsius + 273.15

    @staticmethod
    def kelvin_to_celsius(kelvin: float) -> float:
        """Convert Kelvin to Celsius."""
        return kelvin - 273.15

    # Length conversions
    @staticmethod
    def feet_to_meters(feet: float) -> float:
        """Convert feet to meters."""
        return feet * FEET_TO_METERS

    @staticmethod
    def meters_to_feet(meters: float) -> float:
        """Convert meters to feet."""
        return meters * METERS_TO_FEET

    @staticmethod
    def inches_to_cm(inches: float) -> float:
        """Convert inches to centimeters."""
        return inches * INCHES_TO_CM

    @staticmethod
    def cm_to_inches(cm: float) -> float:
        """Convert centimeters to inches."""
        return cm * CM_TO_INCHES

    @staticmethod
    def inches_to_meters(inches: float) -> float:
        """Convert inches to meters."""
        return inches * INCHES_TO_METERS

    @staticmethod
    def meters_to_inches(meters: float) -> float:
        """Convert meters to inches."""
        return meters / INCHES_TO_METERS

    @staticmethod
    def kilometers_to_meters(kilometers: float) -> float:
        """Convert kilometers to meters."""
        return kilometers * KILOMETERS_TO_METERS

    @staticmethod
    def miles_to_meters(miles: float) -> float:
        """Convert miles to meters."""
        return miles * MILES_TO_METERS

    # Pressure conversions
    @staticmethod
    def psi_to_bar(psi: float) -> float:
        """Convert PSI to bar."""
        return psi * PSI_TO_BAR

    @staticmethod
    def bar_to_psi(bar: float) -> float:
        """Convert bar to PSI."""
        return bar * BAR_TO_PSI

    @staticmethod
    def pascal_to_bar(pascal: float) -> float:
        """Convert Pascal to bar."""
        return pascal * PASCAL_TO_BAR

    @staticmethod
    def kilopascal_to_bar(kilopascal: float) -> float:
        """Convert kilopascal to bar."""
        return kilopascal * KILOPASCAL_TO_BAR

    # Flow rate conversions (GPM <-> LPM)
    @staticmethod
    def gpm_to_lpm(gpm: float) -> float:
        """Convert gallons per minute to liters per minute."""
        return gpm * GALLONS_TO_LITERS

    @staticmethod
    def lpm_to_gpm(lpm: float) -> float:
        """Convert liters per minute to gallons per minute."""
        return lpm * LITERS_TO_GALLONS

    # Time conversions
    @staticmethod
    def hours_to_minutes(hours: float) -> float:
        """Convert hours to minutes."""
        return hours * 60

    @staticmethod
    def minutes_to_hours(minutes: float) -> float:
        """Convert minutes to hours."""
        return minutes / 60


def detect_and_convert_unit(
    column_name: str,
    value: float
) -> tuple[Optional[str], Optional[float]]:
    """
    Auto-detect unit from column name and convert to standard unit.

    Args:
        column_name: Name of the column (e.g., "area_acres", "temp_fahrenheit")
        value: Value to convert

    Returns:
        Tuple of (target_field_name, converted_value) or (None, None) if no conversion needed
    """
    column_lower = column_name.lower()
    converter = UnitConverter()

    # Area conversions to hectares
    if 'acre' in column_lower and 'hectare' not in column_lower:
        return column_name.replace('acres', 'hectares').replace('acre', 'hectares'), converter.acres_to_hectares(value)

    # Volume conversions to liters
    if 'gallon' in column_lower and 'liter' not in column_lower:
        return column_name.replace('gallons', 'liters').replace('gallon', 'liters'), converter.gallons_to_liters(value)

    # Weight conversions to kg
    if any(unit in column_lower for unit in ['pound', 'lbs', 'lb']) and 'kg' not in column_lower:
        new_name = column_name.replace('pounds', 'kg').replace('lbs', 'kg').replace('lb', 'kg')
        return new_name, converter.pounds_to_kg(value)

    # Temperature conversions to Celsius
    if 'fahrenheit' in column_lower or 'temp_f' in column_lower:
        new_name = column_name.replace('fahrenheit', 'celsius').replace('temp_f', 'temp_c')
        return new_name, converter.fahrenheit_to_celsius(value)

    # Length conversions to meters
    if any(unit in column_lower for unit in ['feet', 'foot', 'ft']) and 'meter' not in column_lower:
        new_name = column_name.replace('feet', 'meters').replace('foot', 'meters').replace('ft', 'meters')
        return new_name, converter.feet_to_meters(value)

    # Length conversions cm (from inches)
    if 'inch' in column_lower and 'cm' not in column_lower:
        new_name = column_name.replace('inches', 'cm').replace('inch', 'cm')
        return new_name, converter.inches_to_cm(value)

    # Pressure conversions to bar
    if 'psi' in column_lower and 'bar' not in column_lower:
        new_name = column_name.replace('psi', 'bar')
        return new_name, converter.psi_to_bar(value)

    # Flow rate conversions to LPM
    if 'gpm' in column_lower and 'lpm' not in column_lower:
        new_name = column_name.replace('gpm', 'lpm')
        return new_name, converter.gpm_to_lpm(value)

    return None, None


def convert_value(
    value: Union[float, int],
    from_unit: str,
    to_unit: str
) -> Optional[float]:
    """
    Convert a value from one unit to another.

    Args:
        value: Value to convert
        from_unit: Source unit (e.g., 'acres', 'fahrenheit')
        to_unit: Target unit (e.g., 'hectares', 'celsius')

    Returns:
        Converted value or None if conversion not supported
    """
    converter = UnitConverter()
    conversion_map = {
        # Area
        ('acres', 'hectares'): converter.acres_to_hectares,
        ('hectares', 'acres'): converter.hectares_to_acres,
        ('square_meters', 'hectares'): converter.square_meters_to_hectares,
        ('hectares', 'square_meters'): converter.hectares_to_square_meters,

        # Volume
        ('gallons', 'liters'): converter.gallons_to_liters,
        ('liters', 'gallons'): converter.liters_to_gallons,
        ('cubic_meters', 'liters'): converter.cubic_meters_to_liters,
        ('liters', 'cubic_meters'): converter.liters_to_cubic_meters,

        # Weight
        ('pounds', 'kg'): converter.pounds_to_kg,
        ('pounds', 'kilograms'): converter.pounds_to_kg,
        ('kg', 'pounds'): converter.kg_to_pounds,
        ('kilograms', 'pounds'): converter.kg_to_pounds,
        ('lbs', 'kg'): converter.pounds_to_kg,
        ('grams', 'kg'): converter.grams_to_kg,
        ('tons', 'kg'): converter.tons_to_kg,

        # Temperature
        ('fahrenheit', 'celsius'): converter.fahrenheit_to_celsius,
        ('celsius', 'fahrenheit'): converter.celsius_to_fahrenheit,
        ('celsius', 'kelvin'): converter.celsius_to_kelvin,
        ('kelvin', 'celsius'): converter.kelvin_to_celsius,

        # Length
        ('feet', 'meters'): converter.feet_to_meters,
        ('meters', 'feet'): converter.meters_to_feet,
        ('inches', 'cm'): converter.inches_to_cm,
        ('inches', 'centimeters'): converter.inches_to_cm,
        ('cm', 'inches'): converter.cm_to_inches,
        ('centimeters', 'inches'): converter.cm_to_inches,

        # Pressure
        ('psi', 'bar'): converter.psi_to_bar,
        ('bar', 'psi'): converter.bar_to_psi,

        # Flow rate
        ('gpm', 'lpm'): converter.gpm_to_lpm,
        ('lpm', 'gpm'): converter.lpm_to_gpm,

        # Time
        ('hours', 'minutes'): converter.hours_to_minutes,
        ('minutes', 'hours'): converter.minutes_to_hours,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversion_map:
        return conversion_map[key](float(value))

    return None


def get_standard_unit(measurement_type: str) -> Optional[str]:
    """
    Get the standard unit for a measurement type.

    Args:
        measurement_type: Type of measurement (e.g., 'area', 'volume', 'weight')

    Returns:
        Standard unit name or None
    """
    standard_units = {
        'area': 'hectares',
        'volume': 'liters',
        'weight': 'kilograms',
        'mass': 'kilograms',
        'temperature': 'celsius',
        'length': 'meters',
        'distance': 'meters',
        'pressure': 'bar',
        'flow_rate': 'liters_per_minute',
        'time': 'minutes'
    }

    return standard_units.get(measurement_type.lower())


# Convenience functions for common conversions
def acres_to_hectares(acres: float) -> float:
    """Convert acres to hectares."""
    return UnitConverter.acres_to_hectares(acres)


def gallons_to_liters(gallons: float) -> float:
    """Convert gallons to liters."""
    return UnitConverter.gallons_to_liters(gallons)


def pounds_to_kg(pounds: float) -> float:
    """Convert pounds to kilograms."""
    return UnitConverter.pounds_to_kg(pounds)


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return UnitConverter.fahrenheit_to_celsius(fahrenheit)


def feet_to_meters(feet: float) -> float:
    """Convert feet to meters."""
    return UnitConverter.feet_to_meters(feet)


def inches_to_cm(inches: float) -> float:
    """Convert inches to centimeters."""
    return UnitConverter.inches_to_cm(inches)

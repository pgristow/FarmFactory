"""
Data validation utility for FarmFactory data import system.

Provides comprehensive data validation based on configurable rules,
including type checking, range validation, cross-field validation,
and duplicate detection.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class ValidationLevel(Enum):
    """Validation error severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationError:
    """Represents a single validation error."""

    def __init__(
        self,
        row_number: int,
        column_name: str,
        error_type: str,
        error_message: str,
        level: ValidationLevel = ValidationLevel.ERROR,
        value: Any = None
    ):
        self.row_number = row_number
        self.column_name = column_name
        self.error_type = error_type
        self.error_message = error_message
        self.level = level
        self.value = value

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'row_number': self.row_number,
            'column_name': self.column_name,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'level': self.level.value,
            'value': str(self.value) if self.value is not None else None
        }


class DataValidator:
    """Comprehensive data validator for import system."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the data validator.

        Args:
            config_path: Path to validation_rules.json config file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "import_config" / "validation_rules.json"

        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def validate_field(
        self,
        field_name: str,
        value: Any,
        data_type: str,
        row_number: int
    ) -> List[ValidationError]:
        """
        Validate a single field value.

        Args:
            field_name: Name of the field
            value: Value to validate
            data_type: Data type (e.g., 'farms_and_plots')
            row_number: Row number in CSV (for error reporting)

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if data_type not in self.config:
            return errors

        field_rules = self.config[data_type].get(field_name)
        if not field_rules:
            return errors

        # Check if value is null/empty
        is_null = value is None or value == '' or (isinstance(value, str) and value.strip() == '')

        # Required field validation
        if field_rules.get('required', False) and is_null:
            errors.append(ValidationError(
                row_number=row_number,
                column_name=field_name,
                error_type='required',
                error_message=field_rules['error_messages'].get('required', 'Field is required'),
                value=value
            ))
            return errors  # Don't check other rules if required field is missing

        # Allow null if field allows it
        if is_null and field_rules.get('allow_null', False):
            return errors

        # Type validation
        field_type = field_rules.get('type')
        converted_value, type_error = self._validate_type(
            value, field_type, field_rules, row_number, field_name
        )

        if type_error:
            errors.append(type_error)
            return errors  # Don't check other rules if type is wrong

        # Range validation for numeric types
        if field_type in ['float', 'integer']:
            range_error = self._validate_range(
                converted_value, field_rules, row_number, field_name
            )
            if range_error:
                errors.append(range_error)

        # String length validation
        if field_type == 'string':
            length_errors = self._validate_string_length(
                converted_value, field_rules, row_number, field_name
            )
            errors.extend(length_errors)

        # Pattern validation
        if 'pattern' in field_rules and field_rules['pattern']:
            pattern_error = self._validate_pattern(
                converted_value, field_rules, row_number, field_name
            )
            if pattern_error:
                errors.append(pattern_error)

        # Enum validation
        if 'enum' in field_rules:
            enum_error = self._validate_enum(
                converted_value, field_rules, row_number, field_name
            )
            if enum_error:
                errors.append(enum_error)

        # Date/datetime specific validation
        if field_type in ['date', 'datetime']:
            date_errors = self._validate_date_constraints(
                converted_value, field_rules, row_number, field_name
            )
            errors.extend(date_errors)

        return errors

    def _validate_type(
        self,
        value: Any,
        field_type: str,
        field_rules: Dict,
        row_number: int,
        field_name: str
    ) -> Tuple[Any, Optional[ValidationError]]:
        """Validate and convert field type."""
        if field_type == 'string':
            return str(value), None

        elif field_type == 'integer':
            try:
                return int(float(value)), None
            except (ValueError, TypeError):
                return None, ValidationError(
                    row_number=row_number,
                    column_name=field_name,
                    error_type='type',
                    error_message=field_rules['error_messages'].get('type', 'Must be a whole number'),
                    value=value
                )

        elif field_type == 'float':
            try:
                return float(value), None
            except (ValueError, TypeError):
                return None, ValidationError(
                    row_number=row_number,
                    column_name=field_name,
                    error_type='type',
                    error_message=field_rules['error_messages'].get('type', 'Must be a number'),
                    value=value
                )

        elif field_type == 'date':
            date_obj = self._parse_date(value, field_rules.get('formats', ['%Y-%m-%d']))
            if date_obj is None:
                return None, ValidationError(
                    row_number=row_number,
                    column_name=field_name,
                    error_type='format',
                    error_message=field_rules['error_messages'].get('format', 'Invalid date format'),
                    value=value
                )
            return date_obj, None

        elif field_type == 'datetime':
            datetime_obj = self._parse_date(
                value,
                field_rules.get('formats', ['%Y-%m-%d %H:%M:%S']),
                is_datetime=True
            )
            if datetime_obj is None:
                return None, ValidationError(
                    row_number=row_number,
                    column_name=field_name,
                    error_type='format',
                    error_message=field_rules['error_messages'].get('format', 'Invalid datetime format'),
                    value=value
                )
            return datetime_obj, None

        return value, None

    def _parse_date(self, value: Any, formats: List[str], is_datetime: bool = False) -> Optional[datetime]:
        """Parse date/datetime from string."""
        if isinstance(value, datetime):
            return value

        value_str = str(value).strip()

        for fmt in formats:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue

        return None

    def _validate_range(
        self,
        value: float,
        field_rules: Dict,
        row_number: int,
        field_name: str
    ) -> Optional[ValidationError]:
        """Validate numeric range."""
        min_value = field_rules.get('min_value')
        max_value = field_rules.get('max_value')

        if min_value is not None and value < min_value:
            return ValidationError(
                row_number=row_number,
                column_name=field_name,
                error_type='range',
                error_message=field_rules['error_messages'].get('range', f'Value must be at least {min_value}'),
                value=value
            )

        if max_value is not None and value > max_value:
            return ValidationError(
                row_number=row_number,
                column_name=field_name,
                error_type='range',
                error_message=field_rules['error_messages'].get('range', f'Value cannot exceed {max_value}'),
                value=value
            )

        # Check typical range for warnings
        if field_rules.get('warning_outside_typical', False):
            typical_range = field_rules.get('typical_range')
            if typical_range and (value < typical_range[0] or value > typical_range[1]):
                return ValidationError(
                    row_number=row_number,
                    column_name=field_name,
                    error_type='warning',
                    error_message=field_rules['error_messages'].get('warning', 'Value outside typical range'),
                    level=ValidationLevel.WARNING,
                    value=value
                )

        return None

    def _validate_string_length(
        self,
        value: str,
        field_rules: Dict,
        row_number: int,
        field_name: str
    ) -> List[ValidationError]:
        """Validate string length constraints."""
        errors = []

        min_length = field_rules.get('min_length')
        max_length = field_rules.get('max_length')

        if min_length is not None and len(value) < min_length:
            errors.append(ValidationError(
                row_number=row_number,
                column_name=field_name,
                error_type='min_length',
                error_message=field_rules['error_messages'].get('min_length', f'Must be at least {min_length} characters'),
                value=value
            ))

        if max_length is not None and len(value) > max_length:
            errors.append(ValidationError(
                row_number=row_number,
                column_name=field_name,
                error_type='max_length',
                error_message=field_rules['error_messages'].get('max_length', f'Cannot exceed {max_length} characters'),
                value=value
            ))

        return errors

    def _validate_pattern(
        self,
        value: str,
        field_rules: Dict,
        row_number: int,
        field_name: str
    ) -> Optional[ValidationError]:
        """Validate against regex pattern."""
        pattern = field_rules.get('pattern')
        if not pattern:
            return None

        if not re.match(pattern, str(value)):
            return ValidationError(
                row_number=row_number,
                column_name=field_name,
                error_type='pattern',
                error_message=field_rules['error_messages'].get('pattern', 'Value does not match required pattern'),
                value=value
            )

        return None

    def _validate_enum(
        self,
        value: str,
        field_rules: Dict,
        row_number: int,
        field_name: str
    ) -> Optional[ValidationError]:
        """Validate against enum values."""
        enum_values = field_rules.get('enum', [])
        case_insensitive = field_rules.get('case_insensitive', False)

        value_str = str(value)

        if case_insensitive:
            enum_values_lower = [v.lower() for v in enum_values]
            if value_str.lower() not in enum_values_lower:
                return ValidationError(
                    row_number=row_number,
                    column_name=field_name,
                    error_type='enum',
                    error_message=field_rules['error_messages'].get('enum', f'Must be one of: {", ".join(enum_values)}'),
                    value=value
                )
        else:
            if value_str not in enum_values:
                return ValidationError(
                    row_number=row_number,
                    column_name=field_name,
                    error_type='enum',
                    error_message=field_rules['error_messages'].get('enum', f'Must be one of: {", ".join(enum_values)}'),
                    value=value
                )

        return None

    def _validate_date_constraints(
        self,
        value: datetime,
        field_rules: Dict,
        row_number: int,
        field_name: str
    ) -> List[ValidationError]:
        """Validate date-specific constraints."""
        errors = []
        now = datetime.now()

        # Future date validation
        if not field_rules.get('allow_future', True) and value > now:
            errors.append(ValidationError(
                row_number=row_number,
                column_name=field_name,
                error_type='future',
                error_message=field_rules['error_messages'].get('future', 'Date cannot be in the future'),
                value=value
            ))

        # Maximum future days
        max_future_days = field_rules.get('max_future_days')
        if max_future_days is not None:
            max_future_date = now + timedelta(days=max_future_days)
            if value > max_future_date:
                errors.append(ValidationError(
                    row_number=row_number,
                    column_name=field_name,
                    error_type='too_future',
                    error_message=field_rules['error_messages'].get('too_future', f'Date cannot be more than {max_future_days} days in the future'),
                    value=value
                ))

        # Maximum past years
        max_past_years = field_rules.get('max_past_years')
        if max_past_years is not None:
            min_date = now - timedelta(days=max_past_years * 365)
            if value < min_date:
                errors.append(ValidationError(
                    row_number=row_number,
                    column_name=field_name,
                    error_type='too_old',
                    error_message=field_rules['error_messages'].get('too_old', f'Date cannot be more than {max_past_years} years in the past'),
                    value=value
                ))

        return errors

    def validate_row(
        self,
        row_data: Dict[str, Any],
        data_type: str,
        row_number: int
    ) -> List[ValidationError]:
        """
        Validate an entire row of data.

        Args:
            row_data: Dictionary of field_name: value
            data_type: Data type (e.g., 'farms_and_plots')
            row_number: Row number in CSV

        Returns:
            List of validation errors
        """
        errors = []

        # Validate each field
        for field_name, value in row_data.items():
            field_errors = self.validate_field(field_name, value, data_type, row_number)
            errors.extend(field_errors)

        return errors

    def validate_dataset(
        self,
        data: List[Dict[str, Any]],
        data_type: str,
        start_row: int = 1
    ) -> Tuple[List[ValidationError], Dict[str, int]]:
        """
        Validate entire dataset.

        Args:
            data: List of row dictionaries
            data_type: Data type (e.g., 'farms_and_plots')
            start_row: Starting row number for error reporting

        Returns:
            Tuple of (errors_list, statistics_dict)
        """
        all_errors = []
        stats = {
            'total_rows': len(data),
            'valid_rows': 0,
            'rows_with_errors': 0,
            'rows_with_warnings': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'error_types': {}
        }

        for idx, row_data in enumerate(data):
            row_number = start_row + idx
            errors = self.validate_row(row_data, data_type, row_number)

            if errors:
                has_error = any(e.level == ValidationLevel.ERROR for e in errors)
                has_warning = any(e.level == ValidationLevel.WARNING for e in errors)

                if has_error:
                    stats['rows_with_errors'] += 1
                elif has_warning:
                    stats['rows_with_warnings'] += 1

                for error in errors:
                    if error.level == ValidationLevel.ERROR:
                        stats['total_errors'] += 1
                    elif error.level == ValidationLevel.WARNING:
                        stats['total_warnings'] += 1

                    # Track error types
                    error_type = error.error_type
                    stats['error_types'][error_type] = stats['error_types'].get(error_type, 0) + 1

                all_errors.extend(errors)
            else:
                stats['valid_rows'] += 1

        return all_errors, stats

    def check_duplicates(
        self,
        data: List[Dict[str, Any]],
        data_type: str,
        start_row: int = 1
    ) -> List[ValidationError]:
        """
        Check for duplicate entries based on unique field combinations.

        Args:
            data: List of row dictionaries
            data_type: Data type
            start_row: Starting row number

        Returns:
            List of duplicate validation errors
        """
        duplicate_config = self.config.get('duplicate_detection', {}).get(data_type, {})

        if not duplicate_config.get('enabled', False):
            return []

        unique_fields = duplicate_config.get('unique_fields', [])
        if not unique_fields:
            return []

        seen_combinations = {}
        errors = []

        for idx, row_data in enumerate(data):
            row_number = start_row + idx

            # Build key from unique fields
            key_parts = []
            for field in unique_fields:
                value = row_data.get(field, '')
                key_parts.append(str(value).lower().strip())

            key = '|'.join(key_parts)

            if key in seen_combinations:
                errors.append(ValidationError(
                    row_number=row_number,
                    column_name=', '.join(unique_fields),
                    error_type='duplicate',
                    error_message=duplicate_config.get('error_message', 'Duplicate entry detected'),
                    value=key
                ))
            else:
                seen_combinations[key] = row_number

        return errors


def validate_import_data(
    data: List[Dict[str, Any]],
    data_type: str,
    check_duplicates: bool = True
) -> Dict:
    """
    Convenience function to validate import data.

    Args:
        data: List of row dictionaries
        data_type: Data type (e.g., 'farms_and_plots')
        check_duplicates: Whether to check for duplicates

    Returns:
        Validation results dictionary with errors and statistics
    """
    validator = DataValidator()

    # Validate all rows
    errors, stats = validator.validate_dataset(data, data_type)

    # Check duplicates
    if check_duplicates:
        duplicate_errors = validator.check_duplicates(data, data_type)
        errors.extend(duplicate_errors)
        stats['duplicate_errors'] = len(duplicate_errors)

    return {
        'valid': len(errors) == 0 or all(e.level != ValidationLevel.ERROR for e in errors),
        'errors': [e.to_dict() for e in errors if e.level == ValidationLevel.ERROR],
        'warnings': [e.to_dict() for e in errors if e.level == ValidationLevel.WARNING],
        'statistics': stats
    }

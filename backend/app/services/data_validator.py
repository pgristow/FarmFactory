"""
Data validation service for import data.

Provides comprehensive validation including type checking, range validation,
required fields, and reference integrity.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
import re
import logging

from app.models.farm import Farm
from app.models.plot import Plot

logger = logging.getLogger(__name__)


class ValidationError:
    """Represents a validation error for a specific row and column"""

    def __init__(
        self,
        row_number: int,
        column_name: Optional[str],
        error_type: str,
        error_message: str,
        value: Any = None
    ):
        self.row_number = row_number
        self.column_name = column_name
        self.error_type = error_type
        self.error_message = error_message
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'row_number': self.row_number,
            'column_name': self.column_name,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'value': str(self.value) if self.value is not None else None
        }


class DataValidator:
    """
    Comprehensive data validation service.

    Features:
    - Type validation (date, number, string, boolean)
    - Range validation
    - Required field validation
    - Reference validation (farm/plot existence)
    - Duplicate detection
    - Custom validation rules per data type
    """

    # Validation rules for each data type
    VALIDATION_RULES = {
        'farms_plots': {
            'required_fields': ['farm_name', 'plot_name'],
            'numeric_fields': {
                'latitude': {'min': -90, 'max': 90},
                'longitude': {'min': -180, 'max': 180},
                'total_area_hectares': {'min': 0, 'max': 1000000},
                'plot_area_hectares': {'min': 0, 'max': 100000},
            },
            'string_fields': {
                'farm_name': {'max_length': 255},
                'plot_name': {'max_length': 255},
                'farm_address': {'max_length': 500},
            },
            'date_fields': [],
        },
        'irrigation': {
            'required_fields': ['farm_name', 'plot_name', 'irrigation_date', 'amount_liters'],
            'numeric_fields': {
                'amount_liters': {'min': 0, 'max': 1000000},
                'duration_minutes': {'min': 0, 'max': 1440},  # Max 24 hours
                'flow_rate': {'min': 0, 'max': 10000},
            },
            'string_fields': {
                'method': {'max_length': 100},
                'water_source': {'max_length': 255},
                'notes': {'max_length': 1000},
            },
            'date_fields': ['irrigation_date'],
        },
        'nutrients': {
            'required_fields': ['farm_name', 'plot_name', 'application_date', 'nutrient_type'],
            'numeric_fields': {
                'amount_kg': {'min': 0, 'max': 100000},
                'concentration': {'min': 0, 'max': 100},
                'n_content': {'min': 0, 'max': 100},
                'p_content': {'min': 0, 'max': 100},
                'k_content': {'min': 0, 'max': 100},
            },
            'string_fields': {
                'nutrient_type': {'max_length': 255},
                'method': {'max_length': 100},
                'notes': {'max_length': 1000},
            },
            'date_fields': ['application_date'],
        },
        'phenology': {
            'required_fields': ['farm_name', 'plot_name', 'observation_date', 'growth_stage'],
            'numeric_fields': {
                'plant_height_cm': {'min': 0, 'max': 1000},
                'leaf_count': {'min': 0, 'max': 10000},
                'flowering_percentage': {'min': 0, 'max': 100},
            },
            'string_fields': {
                'growth_stage': {'max_length': 100},
                'notes': {'max_length': 1000},
            },
            'date_fields': ['observation_date'],
        },
        'financial': {
            'required_fields': ['farm_name', 'plot_name', 'transaction_date', 'amount'],
            'numeric_fields': {
                'amount': {'min': 0, 'max': 10000000},
                'quantity': {'min': 0, 'max': 1000000},
                'price_per_unit': {'min': 0, 'max': 100000},
            },
            'string_fields': {
                'transaction_type': {'max_length': 100},
                'description': {'max_length': 1000},
                'unit': {'max_length': 50},
            },
            'date_fields': ['transaction_date'],
        },
    }

    def __init__(self, db: Session):
        """Initialize validator with database session"""
        self.db = db
        self._farm_cache = None
        self._plot_cache = None

    def validate_dataframe(
        self,
        df: pd.DataFrame,
        data_type: str,
        column_mapping: Dict[str, str],
        max_errors: int = 100
    ) -> Tuple[bool, List[ValidationError], Dict[str, int]]:
        """
        Validate a DataFrame according to rules for the data type.

        Args:
            df: Pandas DataFrame with source column names
            data_type: Type of data being imported
            column_mapping: Mapping from source columns to target columns
            max_errors: Maximum number of errors to collect

        Returns:
            Tuple of (is_valid, errors_list, error_summary)
        """
        if data_type not in self.VALIDATION_RULES:
            raise ValueError(f"Unknown data type: {data_type}")

        errors: List[ValidationError] = []
        rules = self.VALIDATION_RULES[data_type]

        # Reverse mapping for validation (target -> source)
        target_to_source = {v: k for k, v in column_mapping.items()}

        # Load reference data once
        self._load_reference_data()

        # Validate each row
        for idx, row in df.iterrows():
            row_number = idx + 2  # +2 for header row and 0-indexing

            if len(errors) >= max_errors:
                logger.warning(f"Reached max errors limit ({max_errors})")
                break

            # Validate required fields
            for target_field in rules['required_fields']:
                source_field = target_to_source.get(target_field)
                if source_field is None or source_field not in df.columns:
                    # Field not mapped - this should be caught earlier
                    continue

                value = row[source_field]
                if pd.isna(value) or (isinstance(value, str) and not value.strip()):
                    errors.append(ValidationError(
                        row_number=row_number,
                        column_name=source_field,
                        error_type='required_field',
                        error_message=f"Required field '{source_field}' is empty",
                        value=value
                    ))

            # Validate numeric fields
            for target_field, constraints in rules['numeric_fields'].items():
                source_field = target_to_source.get(target_field)
                if source_field is None or source_field not in df.columns:
                    continue

                value = row[source_field]
                if pd.isna(value):
                    continue  # Optional field

                # Type validation
                try:
                    numeric_value = float(value)
                except (ValueError, TypeError):
                    errors.append(ValidationError(
                        row_number=row_number,
                        column_name=source_field,
                        error_type='type_error',
                        error_message=f"Value '{value}' is not a valid number",
                        value=value
                    ))
                    continue

                # Range validation
                if 'min' in constraints and numeric_value < constraints['min']:
                    errors.append(ValidationError(
                        row_number=row_number,
                        column_name=source_field,
                        error_type='range_error',
                        error_message=f"Value {numeric_value} is below minimum {constraints['min']}",
                        value=numeric_value
                    ))

                if 'max' in constraints and numeric_value > constraints['max']:
                    errors.append(ValidationError(
                        row_number=row_number,
                        column_name=source_field,
                        error_type='range_error',
                        error_message=f"Value {numeric_value} exceeds maximum {constraints['max']}",
                        value=numeric_value
                    ))

            # Validate string fields
            for target_field, constraints in rules['string_fields'].items():
                source_field = target_to_source.get(target_field)
                if source_field is None or source_field not in df.columns:
                    continue

                value = row[source_field]
                if pd.isna(value):
                    continue  # Optional field

                str_value = str(value)

                # Length validation
                if 'max_length' in constraints and len(str_value) > constraints['max_length']:
                    errors.append(ValidationError(
                        row_number=row_number,
                        column_name=source_field,
                        error_type='validation_error',
                        error_message=f"Text exceeds maximum length of {constraints['max_length']} characters",
                        value=str_value[:50] + '...'
                    ))

            # Validate date fields
            for target_field in rules['date_fields']:
                source_field = target_to_source.get(target_field)
                if source_field is None or source_field not in df.columns:
                    continue

                value = row[source_field]
                if pd.isna(value):
                    continue  # Optional field

                # Date validation
                date_error = self._validate_date(value, source_field, row_number)
                if date_error:
                    errors.append(date_error)

            # Validate farm/plot references
            if data_type != 'farms_plots':  # Don't validate for farms_plots import itself
                farm_error = self._validate_farm_reference(
                    row, target_to_source, row_number
                )
                if farm_error:
                    errors.append(farm_error)

                plot_error = self._validate_plot_reference(
                    row, target_to_source, row_number
                )
                if plot_error:
                    errors.append(plot_error)

        # Check for duplicates
        duplicate_errors = self._check_duplicates(df, data_type, target_to_source)
        errors.extend(duplicate_errors[:max_errors - len(errors)])

        # Generate error summary
        error_summary = {}
        for error in errors:
            error_summary[error.error_type] = error_summary.get(error.error_type, 0) + 1

        is_valid = len(errors) == 0

        logger.info(
            f"Validation complete: {len(errors)} errors found, "
            f"valid={is_valid}"
        )

        return is_valid, errors, error_summary

    def _validate_date(
        self,
        value: Any,
        column_name: str,
        row_number: int
    ) -> Optional[ValidationError]:
        """Validate a date value"""
        try:
            # Try parsing as datetime
            if isinstance(value, pd.Timestamp):
                date_value = value.to_pydatetime()
            elif isinstance(value, datetime):
                date_value = value
            else:
                # Try parsing string
                date_value = pd.to_datetime(value)

            # Check if date is in future (for historical data)
            if date_value > datetime.now():
                return ValidationError(
                    row_number=row_number,
                    column_name=column_name,
                    error_type='validation_error',
                    error_message=f"Date {date_value.date()} is in the future",
                    value=value
                )

            return None

        except (ValueError, TypeError):
            return ValidationError(
                row_number=row_number,
                column_name=column_name,
                error_type='type_error',
                error_message=f"Invalid date format: '{value}'",
                value=value
            )

    def _load_reference_data(self):
        """Load farm and plot reference data for validation"""
        if self._farm_cache is None:
            farms = self.db.query(Farm).all()
            self._farm_cache = {farm.name.lower().strip(): farm.id for farm in farms}

        if self._plot_cache is None:
            plots = self.db.query(Plot).all()
            self._plot_cache = {
                (plot.farm.name.lower().strip(), plot.name.lower().strip()): plot.id
                for plot in plots
            }

    def _validate_farm_reference(
        self,
        row: pd.Series,
        target_to_source: Dict[str, str],
        row_number: int
    ) -> Optional[ValidationError]:
        """Validate that farm exists in database"""
        source_field = target_to_source.get('farm_name')
        if source_field is None:
            return None

        farm_name = row.get(source_field)
        if pd.isna(farm_name):
            return None

        farm_name_norm = str(farm_name).lower().strip()
        if farm_name_norm not in self._farm_cache:
            return ValidationError(
                row_number=row_number,
                column_name=source_field,
                error_type='reference_error',
                error_message=f"Farm '{farm_name}' not found in database",
                value=farm_name
            )

        return None

    def _validate_plot_reference(
        self,
        row: pd.Series,
        target_to_source: Dict[str, str],
        row_number: int
    ) -> Optional[ValidationError]:
        """Validate that plot exists for the farm"""
        farm_source = target_to_source.get('farm_name')
        plot_source = target_to_source.get('plot_name')

        if farm_source is None or plot_source is None:
            return None

        farm_name = row.get(farm_source)
        plot_name = row.get(plot_source)

        if pd.isna(farm_name) or pd.isna(plot_name):
            return None

        key = (str(farm_name).lower().strip(), str(plot_name).lower().strip())
        if key not in self._plot_cache:
            return ValidationError(
                row_number=row_number,
                column_name=plot_source,
                error_type='reference_error',
                error_message=f"Plot '{plot_name}' not found for farm '{farm_name}'",
                value=plot_name
            )

        return None

    def _check_duplicates(
        self,
        df: pd.DataFrame,
        data_type: str,
        target_to_source: Dict[str, str]
    ) -> List[ValidationError]:
        """Check for duplicate rows"""
        errors = []

        # Define key columns for duplicate detection by data type
        key_columns_map = {
            'farms_plots': ['farm_name', 'plot_name'],
            'irrigation': ['farm_name', 'plot_name', 'irrigation_date'],
            'nutrients': ['farm_name', 'plot_name', 'application_date', 'nutrient_type'],
            'phenology': ['farm_name', 'plot_name', 'observation_date'],
            'financial': ['farm_name', 'plot_name', 'transaction_date', 'transaction_type'],
        }

        key_columns = key_columns_map.get(data_type, [])
        if not key_columns:
            return errors

        # Map to source columns
        source_key_columns = []
        for target_col in key_columns:
            source_col = target_to_source.get(target_col)
            if source_col and source_col in df.columns:
                source_key_columns.append(source_col)

        if not source_key_columns:
            return errors

        # Find duplicates
        duplicates = df[df.duplicated(subset=source_key_columns, keep=False)]

        if not duplicates.empty:
            # Group by duplicate key
            for key, group in duplicates.groupby(source_key_columns):
                row_numbers = [idx + 2 for idx in group.index]
                for row_num in row_numbers[1:]:  # Skip first occurrence
                    errors.append(ValidationError(
                        row_number=row_num,
                        column_name=', '.join(source_key_columns),
                        error_type='duplicate_error',
                        error_message=f"Duplicate row found (matches row {row_numbers[0]})",
                        value=str(key)
                    ))

        return errors

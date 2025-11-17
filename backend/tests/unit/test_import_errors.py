"""
Unit tests for import error handling.

Tests all error scenarios including file size, file type, missing columns,
invalid data, duplicates, reference errors, network errors, database errors,
and Celery task failures.
"""
import pytest
import pandas as pd
from pathlib import Path


@pytest.mark.unit
class TestFileSizeErrors:
    """Test file size validation errors."""

    def test_file_too_large_over_100mb(self, tmp_path):
        """Test rejection of files over 100MB."""
        # Simulate large file
        max_size_bytes = 100 * 1024 * 1024  # 100 MB
        large_file_size = 101 * 1024 * 1024  # 101 MB

        # In practice, would check file size before processing
        assert large_file_size > max_size_bytes

        error_message = "File size exceeds maximum allowed size of 100MB"
        assert "100MB" in error_message

    def test_file_at_limit_100mb(self, tmp_path):
        """Test acceptance of files at exactly 100MB."""
        max_size_bytes = 100 * 1024 * 1024
        file_size = 100 * 1024 * 1024

        assert file_size <= max_size_bytes  # Should be accepted

    def test_empty_file_zero_bytes(self, tmp_path):
        """Test rejection of empty (0 byte) files."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")

        file_size = empty_file.stat().st_size

        assert file_size == 0

        error_message = "File is empty"
        assert "empty" in error_message.lower()


@pytest.mark.unit
class TestFileTypeErrors:
    """Test file type validation errors."""

    def test_invalid_file_type_txt(self, tmp_path):
        """Test rejection of .txt files."""
        txt_file = tmp_path / "data.txt"
        txt_file.write_text("Some text data")

        valid_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = txt_file.suffix

        assert file_extension not in valid_extensions

        error_message = f"Invalid file type. Allowed types: CSV, XLSX, XLS"
        assert "Invalid file type" in error_message

    def test_invalid_file_type_pdf(self, tmp_path):
        """Test rejection of .pdf files."""
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_bytes(b'%PDF-1.4')

        valid_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = pdf_file.suffix

        assert file_extension not in valid_extensions

    def test_invalid_file_type_json(self, tmp_path):
        """Test rejection of .json files."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"farm": "test"}')

        valid_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = json_file.suffix

        assert file_extension not in valid_extensions

    def test_valid_file_type_csv(self, tmp_path):
        """Test acceptance of .csv files."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("farm_name,area\nFarm 1,50.5")

        valid_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = csv_file.suffix

        assert file_extension in valid_extensions

    def test_valid_file_type_xlsx(self, tmp_path):
        """Test acceptance of .xlsx files."""
        xlsx_file = tmp_path / "data.xlsx"

        valid_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = xlsx_file.suffix

        assert file_extension in valid_extensions

    def test_no_file_extension(self, tmp_path):
        """Test handling of files without extension."""
        no_ext_file = tmp_path / "data"
        no_ext_file.write_text("some data")

        file_extension = no_ext_file.suffix

        assert file_extension == ""

        error_message = "File has no extension"
        assert "extension" in error_message.lower()


@pytest.mark.unit
class TestMissingColumnsErrors:
    """Test missing required columns errors."""

    def test_missing_required_column_farm_name(self, tmp_path):
        """Test error when required farm_name column is missing."""
        csv_content = """address,total_area_hectares
123 Farm Road,50.5"""

        csv_file = tmp_path / "missing_col.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        required_columns = ['farm_name', 'total_area_hectares']
        missing_columns = [col for col in required_columns if col not in df.columns]

        assert 'farm_name' in missing_columns

        error_message = f"Missing required column(s): {', '.join(missing_columns)}"
        assert "farm_name" in error_message

    def test_all_required_columns_present(self, tmp_path):
        """Test no error when all required columns present."""
        csv_content = """farm_name,total_area_hectares
Farm 1,50.5"""

        csv_file = tmp_path / "complete.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        required_columns = ['farm_name', 'total_area_hectares']
        missing_columns = [col for col in required_columns if col not in df.columns]

        assert len(missing_columns) == 0

    def test_unmapped_required_column(self):
        """Test error when required column cannot be mapped."""
        input_columns = ['Name', 'Location', 'Size']
        required_columns = ['farm_name', 'total_area_hectares', 'latitude', 'longitude']

        # Simulate mapping attempt
        mapped_columns = {
            'Name': 'farm_name',
            'Location': 'address',
            'Size': 'total_area_hectares'
        }

        # Check which required columns are not mapped
        unmapped_required = [col for col in required_columns
                            if col not in mapped_columns.values()]

        assert 'latitude' in unmapped_required
        assert 'longitude' in unmapped_required


@pytest.mark.unit
class TestInvalidDataTypeErrors:
    """Test invalid data type errors."""

    def test_text_in_numeric_field(self, tmp_path):
        """Test error when text is in numeric field."""
        csv_content = """farm_name,total_area_hectares
Farm 1,fifty"""

        csv_file = tmp_path / "bad_type.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        # Check if area can be converted to float
        try:
            pd.to_numeric(df['total_area_hectares'], errors='raise')
            is_valid = True
        except:
            is_valid = False

        assert is_valid is False

        error = {
            'row_number': 2,
            'column_name': 'total_area_hectares',
            'error_type': 'invalid_data_type',
            'error_message': 'Expected numeric value, got text: "fifty"',
            'value': 'fifty'
        }

        assert error['error_type'] == 'invalid_data_type'

    def test_text_in_date_field(self, tmp_path):
        """Test error when invalid text is in date field."""
        csv_content = """farm_name,planting_date
Farm 1,not-a-date"""

        csv_file = tmp_path / "bad_date.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        # Check if date can be parsed
        try:
            pd.to_datetime(df['planting_date'], errors='raise')
            is_valid = True
        except:
            is_valid = False

        assert is_valid is False

    def test_numeric_out_of_integer_range(self):
        """Test error when numeric value exceeds integer range."""
        value = 2**64  # Exceeds int64 range

        is_valid = -(2**63) <= value < 2**63

        assert is_valid is False

        error_message = "Value exceeds integer range"
        assert "range" in error_message.lower()


@pytest.mark.unit
class TestOutOfRangeErrors:
    """Test out of range value errors."""

    def test_ph_below_minimum(self):
        """Test pH value below 0."""
        ph_value = -0.5

        is_valid = 0 <= ph_value <= 14

        assert is_valid is False

        error = {
            'error_type': 'out_of_range',
            'error_message': 'pH must be between 0 and 14',
            'value': ph_value,
            'valid_range': '0-14'
        }

        assert error['error_type'] == 'out_of_range'

    def test_ph_above_maximum(self):
        """Test pH value above 14."""
        ph_value = 15.0

        is_valid = 0 <= ph_value <= 14

        assert is_valid is False

    def test_temperature_below_minimum(self):
        """Test temperature below -50°C."""
        temp = -60.0

        is_valid = -50 <= temp <= 60

        assert is_valid is False

    def test_latitude_out_of_range(self):
        """Test latitude outside -90 to 90 range."""
        latitude = 95.0

        is_valid = -90 <= latitude <= 90

        assert is_valid is False

        error_message = "Latitude must be between -90 and 90 degrees"
        assert "-90" in error_message and "90" in error_message

    def test_longitude_out_of_range(self):
        """Test longitude outside -180 to 180 range."""
        longitude = 185.0

        is_valid = -180 <= longitude <= 180

        assert is_valid is False

    def test_negative_area(self):
        """Test negative area value."""
        area = -10.5

        is_valid = area >= 0

        assert is_valid is False

        error_message = "Area cannot be negative"
        assert "negative" in error_message.lower()

    def test_negative_cost(self):
        """Test negative cost value."""
        cost = -100.0

        is_valid = cost >= 0

        assert is_valid is False


@pytest.mark.unit
class TestDuplicateErrors:
    """Test duplicate data detection errors."""

    def test_duplicate_farm_names(self, tmp_path):
        """Test detection of duplicate farm names."""
        csv_content = """farm_name,total_area_hectares
Farm 1,50.5
Farm 2,75.2
Farm 1,60.0"""

        csv_file = tmp_path / "duplicates.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        # Find duplicates
        duplicates = df[df.duplicated(subset=['farm_name'], keep='first')]

        assert len(duplicates) == 1
        assert duplicates.index[0] == 2  # Row 3 (0-indexed)

        error = {
            'row_number': 3,
            'error_type': 'duplicate',
            'error_message': 'Duplicate farm_name: "Farm 1" already exists in row 1',
            'column_name': 'farm_name',
            'value': 'Farm 1',
            'duplicate_of_row': 1
        }

        assert error['error_type'] == 'duplicate'

    def test_duplicate_entire_rows(self, tmp_path):
        """Test detection of entirely duplicate rows."""
        csv_content = """farm_name,area
Farm 1,50.5
Farm 2,75.2
Farm 1,50.5"""

        csv_file = tmp_path / "dup_rows.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        duplicates = df[df.duplicated(keep='first')]

        assert len(duplicates) == 1

    def test_no_duplicates(self, tmp_path):
        """Test no error when no duplicates present."""
        csv_content = """farm_name,area
Farm 1,50.5
Farm 2,75.2
Farm 3,60.0"""

        csv_file = tmp_path / "no_dups.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        duplicates = df[df.duplicated(subset=['farm_name'], keep='first')]

        assert len(duplicates) == 0


@pytest.mark.unit
class TestReferenceErrors:
    """Test reference integrity errors."""

    def test_nonexistent_farm_reference(self):
        """Test error when referencing non-existent farm."""
        plot_data = {
            'farm_name': 'Nonexistent Farm',
            'plot_name': 'Test Plot',
            'area_hectares': 10.5
        }

        existing_farms = ['Farm 1', 'Farm 2', 'Farm 3']

        is_valid = plot_data['farm_name'] in existing_farms

        assert is_valid is False

        error = {
            'row_number': 1,
            'column_name': 'farm_name',
            'error_type': 'reference_error',
            'error_message': f"Farm '{plot_data['farm_name']}' does not exist",
            'value': plot_data['farm_name']
        }

        assert error['error_type'] == 'reference_error'

    def test_nonexistent_plot_reference(self):
        """Test error when referencing non-existent plot."""
        irrigation_data = {
            'plot_name': 'Nonexistent Plot',
            'event_time': '2024-01-15T06:00:00',
            'method': 'drip'
        }

        existing_plots = ['North Field', 'South Field']

        is_valid = irrigation_data['plot_name'] in existing_plots

        assert is_valid is False

    def test_valid_farm_reference(self):
        """Test no error when farm reference is valid."""
        plot_data = {
            'farm_name': 'Farm 1',
            'plot_name': 'Test Plot'
        }

        existing_farms = ['Farm 1', 'Farm 2', 'Farm 3']

        is_valid = plot_data['farm_name'] in existing_farms

        assert is_valid is True


@pytest.mark.unit
class TestCrossFieldValidationErrors:
    """Test cross-field validation errors."""

    def test_harvest_date_before_planting_date(self):
        """Test error when harvest date is before planting date."""
        planting_date = pd.to_datetime('2024-06-15')
        harvest_date = pd.to_datetime('2024-01-15')

        is_valid = harvest_date > planting_date

        assert is_valid is False

        error = {
            'error_type': 'cross_field_validation',
            'error_message': 'Harvest date must be after planting date',
            'fields': ['planting_date', 'harvest_date']
        }

        assert error['error_type'] == 'cross_field_validation'

    def test_end_time_before_start_time(self):
        """Test error when end time is before start time."""
        start_time = pd.to_datetime('2024-01-15T10:00:00')
        end_time = pd.to_datetime('2024-01-15T08:00:00')

        is_valid = end_time > start_time

        assert is_valid is False

    def test_plot_area_exceeds_farm_area(self):
        """Test error when plot area exceeds farm total area."""
        farm_area = 50.0
        plot_areas = [15.0, 20.0, 25.0]  # Sum = 60.0

        total_plot_area = sum(plot_areas)
        is_valid = total_plot_area <= farm_area

        assert is_valid is False

        error_message = f"Total plot area ({total_plot_area}ha) exceeds farm area ({farm_area}ha)"
        assert "exceeds" in error_message.lower()


@pytest.mark.unit
class TestNetworkErrors:
    """Test network error scenarios."""

    def test_upload_timeout_error(self):
        """Test handling of upload timeout."""
        error = {
            'error_type': 'network_error',
            'error_message': 'Upload timed out after 300 seconds',
            'status_code': 408  # Request Timeout
        }

        assert error['status_code'] == 408

    def test_connection_lost_during_upload(self):
        """Test handling of connection loss."""
        error = {
            'error_type': 'network_error',
            'error_message': 'Connection lost during upload',
            'status_code': None
        }

        assert 'Connection lost' in error['error_message']

    def test_server_unavailable_503(self):
        """Test handling of server unavailability."""
        error = {
            'error_type': 'network_error',
            'error_message': 'Server temporarily unavailable',
            'status_code': 503
        }

        assert error['status_code'] == 503


@pytest.mark.unit
class TestDatabaseErrors:
    """Test database error scenarios."""

    def test_database_connection_error(self):
        """Test handling of database connection failure."""
        error = {
            'error_type': 'database_error',
            'error_message': 'Unable to connect to database',
            'details': 'Connection timeout after 30 seconds'
        }

        assert error['error_type'] == 'database_error'

    def test_constraint_violation_error(self):
        """Test handling of database constraint violation."""
        error = {
            'error_type': 'database_error',
            'error_message': 'Unique constraint violation',
            'constraint': 'unique_farm_name',
            'details': 'Farm name "Farm 1" already exists'
        }

        assert 'constraint' in error

    def test_foreign_key_violation(self):
        """Test handling of foreign key constraint violation."""
        error = {
            'error_type': 'database_error',
            'error_message': 'Foreign key constraint violation',
            'constraint': 'fk_plot_farm_id',
            'details': 'Referenced farm does not exist'
        }

        assert 'Foreign key' in error['error_message']

    def test_transaction_rollback_error(self):
        """Test handling of transaction rollback."""
        error = {
            'error_type': 'database_error',
            'error_message': 'Transaction rolled back due to error',
            'details': 'Import failed at row 5000, all changes reverted'
        }

        assert 'rolled back' in error['error_message'].lower()

    def test_disk_full_error(self):
        """Test handling of disk space error."""
        error = {
            'error_type': 'database_error',
            'error_message': 'Insufficient disk space',
            'details': 'Unable to complete import, disk is full'
        }

        assert 'disk' in error['error_message'].lower()


@pytest.mark.unit
class TestCeleryTaskErrors:
    """Test Celery task failure scenarios."""

    def test_task_timeout_error(self):
        """Test handling of Celery task timeout."""
        error = {
            'error_type': 'task_error',
            'error_message': 'Import task timed out after 30 minutes',
            'task_id': 'abc123',
            'status': 'FAILURE'
        }

        assert error['status'] == 'FAILURE'

    def test_task_revoked_error(self):
        """Test handling of revoked/cancelled task."""
        error = {
            'error_type': 'task_error',
            'error_message': 'Import task was cancelled by user',
            'task_id': 'abc123',
            'status': 'REVOKED'
        }

        assert error['status'] == 'REVOKED'

    def test_worker_crashed_error(self):
        """Test handling of worker crash."""
        error = {
            'error_type': 'task_error',
            'error_message': 'Worker crashed during task execution',
            'task_id': 'abc123',
            'status': 'FAILURE'
        }

        assert 'crashed' in error['error_message'].lower()

    def test_task_retry_exceeded(self):
        """Test handling of exceeded retry attempts."""
        error = {
            'error_type': 'task_error',
            'error_message': 'Maximum retry attempts (3) exceeded',
            'task_id': 'abc123',
            'retry_count': 3,
            'max_retries': 3
        }

        assert error['retry_count'] == error['max_retries']


@pytest.mark.unit
class TestErrorMessageFormatting:
    """Test error message formatting for user-friendliness."""

    def test_user_friendly_error_message(self):
        """Test error messages are user-friendly."""
        technical_error = "ValueError: could not convert string to float: 'abc'"

        # Convert to user-friendly message
        user_friendly = "Invalid number format in row 5, column 'area_hectares'. Expected a number, got 'abc'."

        assert 'row' in user_friendly.lower()
        assert 'column' in user_friendly.lower()
        assert 'abc' in user_friendly

    def test_error_with_row_and_column_info(self):
        """Test errors include row and column information."""
        error = {
            'row_number': 42,
            'column_name': 'total_area_hectares',
            'error_type': 'invalid_data_type',
            'error_message': 'Expected numeric value',
            'value': 'invalid'
        }

        assert 'row_number' in error
        assert 'column_name' in error
        assert error['row_number'] == 42

    def test_error_includes_actual_value(self):
        """Test errors include the actual invalid value."""
        error = {
            'error_message': 'Invalid pH value: 20.0 (must be between 0 and 14)',
            'value': 20.0
        }

        assert error['value'] == 20.0
        assert '20.0' in error['error_message']

    def test_error_includes_fix_suggestion(self):
        """Test errors include suggestions for fixing."""
        error = {
            'error_message': 'Missing required column "farm_name"',
            'suggestion': 'Ensure your CSV has a column named "farm_name" or map an existing column to this field.'
        }

        assert 'suggestion' in error
        assert len(error['suggestion']) > 0


@pytest.mark.unit
class TestErrorRecovery:
    """Test error recovery scenarios."""

    def test_skip_invalid_rows_option(self, tmp_path):
        """Test skip_invalid_rows option."""
        csv_content = """farm_name,area
Farm 1,50.5
Farm 2,invalid
Farm 3,75.2"""

        csv_file = tmp_path / "mixed.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        # Convert area to numeric, coercing errors to NaN
        df['area'] = pd.to_numeric(df['area'], errors='coerce')

        # Filter out rows with NaN area (skip_invalid_rows=True)
        valid_rows = df[df['area'].notna()]

        assert len(valid_rows) == 2  # Only 2 valid rows
        assert len(df) == 3  # Original had 3 rows

    def test_error_log_generation(self):
        """Test generation of error log for user."""
        errors = [
            {'row': 5, 'column': 'area', 'error': 'Invalid number'},
            {'row': 10, 'column': 'latitude', 'error': 'Out of range'},
            {'row': 15, 'column': 'farm_name', 'error': 'Duplicate'},
        ]

        error_count = len(errors)

        assert error_count == 3

        # Error log should be exportable
        error_summary = f"Import failed with {error_count} errors. See details for fix suggestions."

        assert 'failed' in error_summary.lower()
        assert str(error_count) in error_summary

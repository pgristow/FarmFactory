"""
Excel parser service for importing Excel files.

Supports both .xlsx and .xls formats with automatic sheet detection.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ExcelParseError(Exception):
    """Exception raised when Excel parsing fails"""
    pass


class ExcelParser:
    """
    Excel parser for .xlsx and .xls files.

    Features:
    - Support .xlsx (Excel 2007+) and .xls (Excel 97-2003) formats
    - Auto-detect header row
    - Handle multiple sheets (use first by default)
    - Detect data types
    - Provide data preview
    """

    SUPPORTED_EXTENSIONS = ['.xlsx', '.xls']

    @staticmethod
    def get_sheet_names(file_path: str) -> List[str]:
        """
        Get list of sheet names in an Excel file.

        Args:
            file_path: Path to the Excel file

        Returns:
            List of sheet names

        Raises:
            ExcelParseError: If file cannot be read
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            raise ExcelParseError(f"Failed to read Excel file: {str(e)}")

    @staticmethod
    def parse_excel(
        file_path: str,
        sheet_name: Optional[str] = None,
        preview_rows: int = 10
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parse Excel file.

        Args:
            file_path: Path to the Excel file
            sheet_name: Name of sheet to parse (uses first sheet if None)
            preview_rows: Number of rows to include in preview

        Returns:
            Tuple of (full DataFrame, metadata dict)

        Raises:
            ExcelParseError: If parsing fails
        """
        if not Path(file_path).exists():
            raise ExcelParseError(f"File not found: {file_path}")

        file_extension = Path(file_path).suffix.lower()
        if file_extension not in ExcelParser.SUPPORTED_EXTENSIONS:
            raise ExcelParseError(
                f"Unsupported file extension: {file_extension}. "
                f"Supported: {', '.join(ExcelParser.SUPPORTED_EXTENSIONS)}"
            )

        try:
            # Get available sheets
            excel_file = pd.ExcelFile(file_path)
            available_sheets = excel_file.sheet_names

            # Determine which sheet to use
            if sheet_name is None:
                sheet_name = available_sheets[0]
                logger.info(f"Using first sheet: '{sheet_name}'")
            elif sheet_name not in available_sheets:
                raise ExcelParseError(
                    f"Sheet '{sheet_name}' not found. "
                    f"Available sheets: {', '.join(available_sheets)}"
                )

            # Parse the sheet
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                keep_default_na=True,
            )

            # Validate that we got data
            if df.empty:
                raise ExcelParseError(f"Sheet '{sheet_name}' is empty")

            if len(df.columns) == 0:
                raise ExcelParseError(f"No columns found in sheet '{sheet_name}'")

            # Clean column names (strip whitespace, handle unnamed columns)
            df.columns = [
                str(col).strip() if not str(col).startswith('Unnamed:') else f'Column_{i}'
                for i, col in enumerate(df.columns)
            ]

            # Remove completely empty rows
            df = df.dropna(how='all')

            # Detect data types
            data_types = ExcelParser._detect_data_types(df)

            # Create metadata
            metadata = {
                'sheet_name': sheet_name,
                'available_sheets': available_sheets,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': df.columns.tolist(),
                'data_types': data_types,
                'has_header': True,
                'file_size': Path(file_path).stat().st_size,
                'file_extension': file_extension,
            }

            logger.info(
                f"Successfully parsed Excel: {len(df)} rows, "
                f"{len(df.columns)} columns from sheet '{sheet_name}'"
            )

            return df, metadata

        except pd.errors.ParserError as e:
            raise ExcelParseError(f"Failed to parse Excel: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing Excel: {e}", exc_info=True)
            raise ExcelParseError(f"Failed to parse Excel: {str(e)}")

    @staticmethod
    def get_preview(df: pd.DataFrame, num_rows: int = 10) -> List[Dict[str, Any]]:
        """
        Get preview of DataFrame as list of dictionaries.

        Args:
            df: Pandas DataFrame
            num_rows: Number of rows to include

        Returns:
            List of row dictionaries
        """
        preview_df = df.head(num_rows)

        # Convert to list of dicts, handling NaN values
        preview_data = []
        for _, row in preview_df.iterrows():
            row_dict = {}
            for col in df.columns:
                value = row[col]
                # Convert pandas NA/NaN to None
                if pd.isna(value):
                    row_dict[col] = None
                # Convert timestamps to string for JSON serialization
                elif hasattr(value, 'isoformat'):
                    row_dict[col] = value.isoformat()
                else:
                    row_dict[col] = value
            preview_data.append(row_dict)

        return preview_data

    @staticmethod
    def _detect_data_types(df: pd.DataFrame) -> Dict[str, str]:
        """
        Detect data types for each column.

        Args:
            df: Pandas DataFrame

        Returns:
            Dictionary mapping column names to detected types
        """
        data_types = {}

        for col in df.columns:
            dtype = df[col].dtype

            # Pandas infers types better from Excel than CSV
            if dtype == 'object':
                # Sample non-null values to determine type
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    sample = non_null.iloc[0]

                    # Check if it's a date
                    if hasattr(sample, 'date'):
                        data_types[col] = 'date'
                        continue

                    # Try to parse as numeric
                    try:
                        pd.to_numeric(non_null, errors='raise')
                        data_types[col] = 'numeric'
                        continue
                    except (ValueError, TypeError):
                        pass

                # Default to string
                data_types[col] = 'string'

            elif dtype in ['int64', 'int32', 'float64', 'float32']:
                data_types[col] = 'numeric'

            elif dtype in ['datetime64', 'datetime64[ns]']:
                data_types[col] = 'date'

            elif dtype == 'bool':
                data_types[col] = 'boolean'

            else:
                data_types[col] = 'string'

        return data_types

    @staticmethod
    def validate_excel_structure(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a file is a valid Excel file without fully parsing it.

        Args:
            file_path: Path to the Excel file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not Path(file_path).exists():
                return False, "File does not exist"

            file_extension = Path(file_path).suffix.lower()
            if file_extension not in ExcelParser.SUPPORTED_EXTENSIONS:
                return False, f"Invalid file extension: {file_extension}"

            file_size = Path(file_path).stat().st_size
            if file_size == 0:
                return False, "File is empty"

            if file_size > 100 * 1024 * 1024:  # 100MB
                return False, "File is too large (max 100MB)"

            # Try to open the file and read sheet names
            excel_file = pd.ExcelFile(file_path)
            if not excel_file.sheet_names:
                return False, "No sheets found in Excel file"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def detect_header_row(file_path: str, sheet_name: Optional[str] = None) -> int:
        """
        Attempt to detect which row contains the header.

        Args:
            file_path: Path to the Excel file
            sheet_name: Name of sheet to analyze

        Returns:
            Row index of detected header (0-indexed)
        """
        try:
            # Read first 10 rows without assuming header
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=10)

            # Look for row with most string values and fewest empty cells
            best_row = 0
            best_score = 0

            for idx in range(min(5, len(df))):  # Check first 5 rows
                row = df.iloc[idx]
                # Count non-empty string values
                string_count = sum(1 for val in row if isinstance(val, str) and val.strip())
                # Count non-empty values
                non_empty_count = sum(1 for val in row if pd.notna(val))

                # Score based on string count and non-empty ratio
                score = string_count * 2 + non_empty_count

                if score > best_score:
                    best_score = score
                    best_row = idx

            logger.info(f"Detected header row at index {best_row}")
            return best_row

        except Exception as e:
            logger.warning(f"Error detecting header row: {e}. Using default (0)")
            return 0

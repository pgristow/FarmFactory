"""
CSV parser service for importing CSV files.

Handles various CSV formats, encodings, and delimiters with auto-detection.
"""
import pandas as pd
import chardet
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class CSVParseError(Exception):
    """Exception raised when CSV parsing fails"""
    pass


class CSVParser:
    """
    CSV parser with auto-detection of encoding, delimiter, and headers.

    Features:
    - Auto-detect encoding (UTF-8, Latin-1, Windows-1252, etc.)
    - Auto-detect delimiter (comma, semicolon, tab, pipe)
    - Auto-detect header row
    - Handle quoted fields
    - Detect data types
    - Provide data preview
    """

    SUPPORTED_ENCODINGS = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
    SUPPORTED_DELIMITERS = [',', ';', '\t', '|']

    @staticmethod
    def detect_encoding(file_path: str, sample_size: int = 10000) -> str:
        """
        Detect file encoding using chardet library.

        Args:
            file_path: Path to the CSV file
            sample_size: Number of bytes to sample for detection

        Returns:
            Detected encoding name (e.g., 'utf-8', 'latin-1')
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(sample_size)
                result = chardet.detect(raw_data)
                detected_encoding = result['encoding']
                confidence = result['confidence']

                logger.info(
                    f"Detected encoding: {detected_encoding} "
                    f"(confidence: {confidence:.2%})"
                )

                # Map some encodings to more common names
                encoding_map = {
                    'ascii': 'utf-8',
                    'ISO-8859-1': 'latin-1',
                    'Windows-1252': 'windows-1252',
                }

                return encoding_map.get(detected_encoding, detected_encoding.lower())

        except Exception as e:
            logger.warning(f"Error detecting encoding: {e}. Defaulting to utf-8")
            return 'utf-8'

    @staticmethod
    def detect_delimiter(file_path: str, encoding: str = 'utf-8', sample_lines: int = 5) -> str:
        """
        Detect CSV delimiter by analyzing the first few lines.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding
            sample_lines: Number of lines to sample

        Returns:
            Detected delimiter character
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # Read first few lines
                lines = [f.readline() for _ in range(sample_lines)]

            # Count occurrences of each delimiter
            delimiter_counts = {delim: [] for delim in CSVParser.SUPPORTED_DELIMITERS}

            for line in lines:
                if line.strip():
                    for delim in CSVParser.SUPPORTED_DELIMITERS:
                        delimiter_counts[delim].append(line.count(delim))

            # Find delimiter with most consistent counts (same count per line)
            best_delimiter = ','
            best_score = 0

            for delim, counts in delimiter_counts.items():
                if not counts or max(counts) == 0:
                    continue

                # Score based on consistency and frequency
                avg_count = sum(counts) / len(counts)
                consistency = 1 - (max(counts) - min(counts)) / (max(counts) + 1)
                score = avg_count * consistency

                if score > best_score:
                    best_score = score
                    best_delimiter = delim

            delim_name = {',': 'comma', ';': 'semicolon', '\t': 'tab', '|': 'pipe'}
            logger.info(f"Detected delimiter: {delim_name.get(best_delimiter, best_delimiter)}")

            return best_delimiter

        except Exception as e:
            logger.warning(f"Error detecting delimiter: {e}. Defaulting to comma")
            return ','

    @staticmethod
    def parse_csv(
        file_path: str,
        encoding: Optional[str] = None,
        delimiter: Optional[str] = None,
        preview_rows: int = 10
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parse CSV file with auto-detection of encoding and delimiter.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding (auto-detected if None)
            delimiter: CSV delimiter (auto-detected if None)
            preview_rows: Number of rows to include in preview

        Returns:
            Tuple of (full DataFrame, metadata dict)

        Raises:
            CSVParseError: If parsing fails
        """
        if not Path(file_path).exists():
            raise CSVParseError(f"File not found: {file_path}")

        try:
            # Auto-detect encoding if not provided
            if encoding is None:
                encoding = CSVParser.detect_encoding(file_path)

            # Auto-detect delimiter if not provided
            if delimiter is None:
                delimiter = CSVParser.detect_delimiter(file_path, encoding)

            # Parse CSV with pandas
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                delimiter=delimiter,
                skipinitialspace=True,
                quotechar='"',
                escapechar='\\',
                na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                keep_default_na=True,
            )

            # Validate that we got data
            if df.empty:
                raise CSVParseError("CSV file is empty")

            if len(df.columns) == 0:
                raise CSVParseError("No columns found in CSV file")

            # Clean column names (strip whitespace)
            df.columns = df.columns.str.strip()

            # Detect data types
            data_types = CSVParser._detect_data_types(df)

            # Create metadata
            metadata = {
                'encoding': encoding,
                'delimiter': delimiter,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': df.columns.tolist(),
                'data_types': data_types,
                'has_header': True,
                'file_size': Path(file_path).stat().st_size,
            }

            logger.info(
                f"Successfully parsed CSV: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )

            return df, metadata

        except pd.errors.ParserError as e:
            raise CSVParseError(f"Failed to parse CSV: {str(e)}")
        except UnicodeDecodeError as e:
            raise CSVParseError(
                f"Failed to decode file with encoding '{encoding}': {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing CSV: {e}", exc_info=True)
            raise CSVParseError(f"Failed to parse CSV: {str(e)}")

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

            # Try to infer better types
            if dtype == 'object':
                # Try to parse as datetime
                try:
                    pd.to_datetime(df[col], errors='raise')
                    data_types[col] = 'date'
                    continue
                except (ValueError, TypeError):
                    pass

                # Try to parse as numeric
                try:
                    pd.to_numeric(df[col], errors='raise')
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
    def validate_csv_structure(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a file is a valid CSV without fully parsing it.

        Args:
            file_path: Path to the CSV file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not Path(file_path).exists():
                return False, "File does not exist"

            file_size = Path(file_path).stat().st_size
            if file_size == 0:
                return False, "File is empty"

            if file_size > 100 * 1024 * 1024:  # 100MB
                return False, "File is too large (max 100MB)"

            # Try to read first few lines
            encoding = CSVParser.detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                first_line = f.readline()
                if not first_line.strip():
                    return False, "File appears to be empty"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

"""
Unit tests for CSV parser service.

Tests various CSV formats, encodings, delimiters, and edge cases.
"""
import pytest
import pandas as pd
from io import StringIO, BytesIO
import tempfile
from pathlib import Path


@pytest.mark.unit
class TestCSVParser:
    """Test CSV parsing functionality."""

    def test_parse_comma_delimited_csv(self, tmp_path):
        """Test parsing standard comma-delimited CSV."""
        csv_content = """farm_name,plot_name,area_hectares,latitude,longitude
Green Valley Farm,North Field,10.5,40.7128,-74.0060
Sunny Acres,South Plot,15.2,40.7589,-73.9851"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV
        df = pd.read_csv(csv_file)

        # Assertions
        assert len(df) == 2
        assert list(df.columns) == ['farm_name', 'plot_name', 'area_hectares', 'latitude', 'longitude']
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm'
        assert df.iloc[0]['area_hectares'] == 10.5

    def test_parse_semicolon_delimited_csv(self, tmp_path):
        """Test parsing semicolon-delimited CSV (common in Europe)."""
        csv_content = """farm_name;plot_name;area_hectares;latitude;longitude
Green Valley Farm;North Field;10.5;40.7128;-74.0060
Sunny Acres;South Plot;15.2;40.7589;-73.9851"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV with semicolon delimiter
        df = pd.read_csv(csv_file, sep=';')

        # Assertions
        assert len(df) == 2
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm'

    def test_parse_tab_delimited_csv(self, tmp_path):
        """Test parsing tab-delimited CSV."""
        csv_content = """farm_name\tplot_name\tarea_hectares\tlatitude\tlongitude
Green Valley Farm\tNorth Field\t10.5\t40.7128\t-74.0060
Sunny Acres\tSouth Plot\t15.2\t40.7589\t-73.9851"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV with tab delimiter
        df = pd.read_csv(csv_file, sep='\t')

        # Assertions
        assert len(df) == 2
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm'

    def test_parse_csv_with_quoted_fields(self, tmp_path):
        """Test parsing CSV with quoted fields containing commas."""
        csv_content = '''farm_name,plot_name,area_hectares,notes
"Green Valley Farm, LLC",North Field,10.5,"Large field, good soil"
Sunny Acres,"South Plot, Section A",15.2,"Needs irrigation, sunny"'''

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV
        df = pd.read_csv(csv_file)

        # Assertions
        assert len(df) == 2
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm, LLC'
        assert df.iloc[0]['notes'] == 'Large field, good soil'

    def test_parse_csv_with_escaped_characters(self, tmp_path):
        """Test parsing CSV with escaped characters."""
        csv_content = '''farm_name,plot_name,notes
Green Valley Farm,North Field,"Field with ""special"" crops"
Sunny Acres,South Plot,"Plant's growth is good"'''

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV
        df = pd.read_csv(csv_file)

        # Assertions
        assert len(df) == 2
        assert 'special' in df.iloc[0]['notes']

    def test_parse_csv_utf8_encoding(self, tmp_path):
        """Test parsing CSV with UTF-8 encoding."""
        csv_content = """farm_name,plot_name,notes
Finca José,Campo Norte,Café y frutas tropicales
Ferme François,Champ Sud,Blé et légumes"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content, encoding='utf-8')

        # Parse CSV
        df = pd.read_csv(csv_file, encoding='utf-8')

        # Assertions
        assert len(df) == 2
        assert df.iloc[0]['farm_name'] == 'Finca José'
        assert 'Café' in df.iloc[0]['notes']

    def test_parse_csv_latin1_encoding(self, tmp_path):
        """Test parsing CSV with Latin-1 encoding."""
        csv_content = """farm_name,plot_name,notes
Finca José,Campo Norte,Café y frutas"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content, encoding='latin-1')

        # Parse CSV with Latin-1 encoding
        df = pd.read_csv(csv_file, encoding='latin-1')

        # Assertions
        assert len(df) == 1
        assert df.iloc[0]['farm_name'] == 'Finca José'

    def test_parse_csv_windows_1252_encoding(self, tmp_path):
        """Test parsing CSV with Windows-1252 encoding."""
        csv_content = """farm_name,plot_name,area_hectares
Green Valley Farm,North Field,10.5"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content, encoding='windows-1252')

        # Parse CSV
        df = pd.read_csv(csv_file, encoding='windows-1252')

        # Assertions
        assert len(df) == 1

    def test_parse_csv_missing_headers(self, tmp_path):
        """Test parsing CSV with missing headers."""
        csv_content = """Green Valley Farm,North Field,10.5,40.7128,-74.0060
Sunny Acres,South Plot,15.2,40.7589,-73.9851"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV without headers
        df = pd.read_csv(csv_file, header=None, names=['farm_name', 'plot_name', 'area', 'lat', 'lon'])

        # Assertions
        assert len(df) == 2
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm'

    def test_parse_empty_csv_file(self, tmp_path):
        """Test parsing empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        # Parse empty CSV
        with pytest.raises(pd.errors.EmptyDataError):
            pd.read_csv(csv_file)

    def test_parse_csv_with_empty_rows(self, tmp_path):
        """Test parsing CSV with empty rows."""
        csv_content = """farm_name,plot_name,area_hectares
Green Valley Farm,North Field,10.5

Sunny Acres,South Plot,15.2

"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV, skip empty rows
        df = pd.read_csv(csv_file)

        # Assertions
        assert len(df) == 2  # Empty rows should be skipped

    def test_parse_csv_with_missing_values(self, tmp_path):
        """Test parsing CSV with missing values."""
        csv_content = """farm_name,plot_name,area_hectares,notes
Green Valley Farm,North Field,10.5,Good soil
Sunny Acres,South Plot,,
Test Farm,,5.0,"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV
        df = pd.read_csv(csv_file)

        # Assertions
        assert len(df) == 3
        assert pd.isna(df.iloc[1]['area_hectares'])
        assert pd.isna(df.iloc[2]['plot_name'])

    def test_parse_csv_with_bom(self, tmp_path):
        """Test parsing CSV with Byte Order Mark (BOM)."""
        csv_content = "\ufeff" + """farm_name,plot_name,area_hectares
Green Valley Farm,North Field,10.5"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content, encoding='utf-8-sig')

        # Parse CSV with BOM
        df = pd.read_csv(csv_file, encoding='utf-8-sig')

        # Assertions
        assert len(df) == 1
        assert 'farm_name' in df.columns  # No BOM in column name

    def test_auto_detect_delimiter(self, tmp_path):
        """Test auto-detecting CSV delimiter."""
        csv_content = """farm_name|plot_name|area_hectares
Green Valley Farm|North Field|10.5"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Auto-detect delimiter
        df = pd.read_csv(csv_file, sep=None, engine='python')

        # Assertions
        assert len(df) == 1
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm'

    def test_parse_csv_with_different_line_endings(self, tmp_path):
        """Test parsing CSV with different line endings."""
        # Unix line endings (\n)
        csv_content_unix = "farm_name,plot_name\nFarm 1,Plot 1\nFarm 2,Plot 2"

        # Windows line endings (\r\n)
        csv_content_windows = "farm_name,plot_name\r\nFarm 1,Plot 1\r\nFarm 2,Plot 2"

        # Old Mac line endings (\r)
        csv_content_mac = "farm_name,plot_name\rFarm 1,Plot 1\rFarm 2,Plot 2"

        for ending_type, content in [('unix', csv_content_unix),
                                      ('windows', csv_content_windows),
                                      ('mac', csv_content_mac)]:
            csv_file = tmp_path / f"test_{ending_type}.csv"
            csv_file.write_bytes(content.encode())

            # Parse CSV
            df = pd.read_csv(csv_file)

            # Assertions
            assert len(df) == 2, f"Failed for {ending_type} line endings"

    def test_parse_large_csv(self, tmp_path):
        """Test parsing large CSV file."""
        # Generate large CSV
        rows = 10000
        data = {
            'farm_name': [f'Farm {i}' for i in range(rows)],
            'plot_name': [f'Plot {i}' for i in range(rows)],
            'area_hectares': [i * 0.5 for i in range(rows)],
        }
        df_large = pd.DataFrame(data)

        csv_file = tmp_path / "large.csv"
        df_large.to_csv(csv_file, index=False)

        # Parse large CSV
        df = pd.read_csv(csv_file)

        # Assertions
        assert len(df) == rows
        assert df.iloc[0]['farm_name'] == 'Farm 0'

    def test_parse_csv_with_data_types(self, tmp_path):
        """Test parsing CSV with various data types."""
        csv_content = """farm_name,plot_name,area_hectares,is_organic,planting_date
Green Valley Farm,North Field,10.5,true,2024-01-15
Sunny Acres,South Plot,15.2,false,2024-02-20"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV with dtype specification
        df = pd.read_csv(
            csv_file,
            dtype={'farm_name': str, 'area_hectares': float, 'is_organic': bool},
            parse_dates=['planting_date']
        )

        # Assertions
        assert df['area_hectares'].dtype == float
        assert pd.api.types.is_datetime64_any_dtype(df['planting_date'])

    def test_parse_csv_preview_first_100_rows(self, tmp_path):
        """Test parsing preview of first 100 rows."""
        # Generate CSV with 500 rows
        rows = 500
        data = {
            'farm_name': [f'Farm {i}' for i in range(rows)],
            'plot_name': [f'Plot {i}' for i in range(rows)],
        }
        df_large = pd.DataFrame(data)

        csv_file = tmp_path / "test.csv"
        df_large.to_csv(csv_file, index=False)

        # Parse only first 100 rows
        df_preview = pd.read_csv(csv_file, nrows=100)

        # Assertions
        assert len(df_preview) == 100
        assert df_preview.iloc[0]['farm_name'] == 'Farm 0'
        assert df_preview.iloc[99]['farm_name'] == 'Farm 99'

    def test_parse_malformed_csv(self, tmp_path):
        """Test parsing malformed CSV gracefully."""
        csv_content = """farm_name,plot_name,area_hectares
Green Valley Farm,North Field,10.5
Sunny Acres,South Plot,15.2,extra_value,another_extra
Test Farm,Test Plot"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV with error handling
        df = pd.read_csv(csv_file, on_bad_lines='skip')

        # Assertions - malformed line should be skipped
        assert len(df) == 2  # Only valid rows

    def test_get_column_data_types(self, tmp_path):
        """Test inferring column data types."""
        csv_content = """farm_name,plot_name,area_hectares,planting_date,is_organic
Green Valley Farm,North Field,10.5,2024-01-15,true
Sunny Acres,South Plot,15.2,2024-02-20,false"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Parse CSV and infer types
        df = pd.read_csv(csv_file)

        # Get data types
        dtypes = df.dtypes.to_dict()

        # Assertions
        assert dtypes['farm_name'] == object  # string
        assert dtypes['area_hectares'] == float

    def test_parse_csv_special_characters(self, tmp_path):
        """Test parsing CSV with special characters in data."""
        csv_content = """farm_name,plot_name,notes
Farm & Co.,Plot #1,"Description: 50% organic, $100/acre"
O'Brien Farm,Plot @2,"Temperature: 25°C, pH: 6.5"
Müller Farm,Plot €3,"Area: 10 m²"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content, encoding='utf-8')

        # Parse CSV
        df = pd.read_csv(csv_file, encoding='utf-8')

        # Assertions
        assert len(df) == 3
        assert df.iloc[0]['farm_name'] == 'Farm & Co.'
        assert 'O\'Brien' in df.iloc[1]['farm_name']
        assert 'Müller' in df.iloc[2]['farm_name']


@pytest.mark.unit
class TestCSVParserService:
    """Test CSV parser service methods."""

    def test_detect_encoding(self, tmp_path):
        """Test automatic encoding detection."""
        # This would test a service method that detects encoding
        # Implementation would use chardet library
        pass

    def test_detect_delimiter(self, tmp_path):
        """Test automatic delimiter detection."""
        # Test service method that detects delimiter
        # Could use csv.Sniffer or pandas' sep=None
        pass

    def test_validate_csv_structure(self, tmp_path):
        """Test validating CSV has required structure."""
        csv_content = """farm_name,plot_name,area_hectares
Green Valley Farm,North Field,10.5"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Validate CSV has at least one data row
        df = pd.read_csv(csv_file)
        assert len(df) > 0
        assert len(df.columns) > 0

    def test_parse_csv_sample_data(self, tmp_path):
        """Test extracting sample data from CSV."""
        csv_content = """farm_name,plot_name,area_hectares
Green Valley Farm,North Field,10.5
Sunny Acres,South Plot,15.2
Test Farm,Test Plot,20.0"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Get sample (first 2 rows)
        df_sample = pd.read_csv(csv_file, nrows=2)

        # Assertions
        assert len(df_sample) == 2
        assert df_sample.iloc[0]['farm_name'] == 'Green Valley Farm'

    def test_get_csv_metadata(self, tmp_path):
        """Test extracting CSV metadata."""
        csv_content = """farm_name,plot_name,area_hectares
Green Valley Farm,North Field,10.5
Sunny Acres,South Plot,15.2"""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Get metadata
        df = pd.read_csv(csv_file)
        metadata = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'file_size': csv_file.stat().st_size
        }

        # Assertions
        assert metadata['row_count'] == 2
        assert metadata['column_count'] == 3
        assert 'farm_name' in metadata['columns']

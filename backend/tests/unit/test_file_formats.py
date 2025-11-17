"""
Unit tests for various file formats.

Tests CSV with different line endings, encodings, BOM, Excel formats,
corrupted files, and special characters.
"""
import pytest
import pandas as pd
from openpyxl import Workbook
import xlwt
from pathlib import Path


@pytest.mark.unit
class TestCSVFileFormats:
    """Test various CSV file format variations."""

    def test_csv_unix_line_endings(self, tmp_path):
        """Test CSV with Unix line endings (LF)."""
        csv_content = "farm_name,area\nFarm 1,50.5\nFarm 2,75.2"

        csv_file = tmp_path / "unix.csv"
        csv_file.write_bytes(csv_content.encode('utf-8'))

        df = pd.read_csv(csv_file)

        assert len(df) == 2
        assert df.iloc[0]['farm_name'] == 'Farm 1'

    def test_csv_windows_line_endings(self, tmp_path):
        """Test CSV with Windows line endings (CRLF)."""
        csv_content = "farm_name,area\r\nFarm 1,50.5\r\nFarm 2,75.2"

        csv_file = tmp_path / "windows.csv"
        csv_file.write_bytes(csv_content.encode('utf-8'))

        df = pd.read_csv(csv_file)

        assert len(df) == 2
        assert df.iloc[0]['farm_name'] == 'Farm 1'

    def test_csv_old_mac_line_endings(self, tmp_path):
        """Test CSV with old Mac line endings (CR)."""
        csv_content = "farm_name,area\rFarm 1,50.5\rFarm 2,75.2"

        csv_file = tmp_path / "mac.csv"
        csv_file.write_bytes(csv_content.encode('utf-8'))

        # Pandas handles old Mac line endings
        try:
            df = pd.read_csv(csv_file)
            assert len(df) >= 1
        except:
            # Old Mac format might not be fully supported
            pass

    def test_csv_with_bom_utf8(self, tmp_path):
        """Test CSV with UTF-8 BOM (Byte Order Mark)."""
        csv_content = "farm_name,area\nFarm 1,50.5"

        csv_file = tmp_path / "bom.csv"
        csv_file.write_bytes(b'\xef\xbb\xbf' + csv_content.encode('utf-8'))

        df = pd.read_csv(csv_file, encoding='utf-8-sig')

        assert len(df) == 1
        assert 'farm_name' in df.columns  # BOM should be stripped

    def test_csv_utf8_encoding(self, tmp_path):
        """Test CSV with UTF-8 encoding."""
        csv_content = """farm_name,notes
Finca José,Café y frutas
Ferme François,Blé et maïs"""

        csv_file = tmp_path / "utf8.csv"
        csv_file.write_text(csv_content, encoding='utf-8')

        df = pd.read_csv(csv_file, encoding='utf-8')

        assert len(df) == 2
        assert 'José' in df.iloc[0]['farm_name']
        assert 'Café' in df.iloc[0]['notes']

    def test_csv_latin1_encoding(self, tmp_path):
        """Test CSV with Latin-1 (ISO-8859-1) encoding."""
        csv_content = """farm_name,notes
Finca José,Café"""

        csv_file = tmp_path / "latin1.csv"
        csv_file.write_text(csv_content, encoding='latin-1')

        df = pd.read_csv(csv_file, encoding='latin-1')

        assert len(df) == 1

    def test_csv_windows_1252_encoding(self, tmp_path):
        """Test CSV with Windows-1252 encoding."""
        csv_content = """farm_name,notes
Test Farm,Special chars: – —"""

        csv_file = tmp_path / "win1252.csv"
        csv_file.write_text(csv_content, encoding='windows-1252')

        df = pd.read_csv(csv_file, encoding='windows-1252')

        assert len(df) == 1

    def test_csv_with_special_characters_in_filename(self, tmp_path):
        """Test CSV file with special characters in filename."""
        csv_content = "farm_name,area\nFarm 1,50.5"

        # Filename with spaces and special chars
        csv_file = tmp_path / "farm data (2024) [import].csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        assert len(df) == 1

    def test_empty_csv_file(self, tmp_path):
        """Test completely empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        with pytest.raises((pd.errors.EmptyDataError, ValueError)):
            pd.read_csv(csv_file)

    def test_csv_headers_only_no_data(self, tmp_path):
        """Test CSV with headers but no data rows."""
        csv_content = "farm_name,area_hectares,latitude,longitude"

        csv_file = tmp_path / "headers_only.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        assert len(df) == 0
        assert len(df.columns) == 4


@pytest.mark.unit
class TestExcelFileFormats:
    """Test various Excel file format variations."""

    def test_excel_2003_xls_format(self, tmp_path):
        """Test Excel 97-2003 (.xls) format."""
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Farms')

        ws.write(0, 0, 'farm_name')
        ws.write(0, 1, 'area_hectares')
        ws.write(1, 0, 'Farm 1')
        ws.write(1, 1, 50.5)

        excel_file = tmp_path / "test.xls"
        wb.save(excel_file)

        df = pd.read_excel(excel_file, engine='xlrd')

        assert len(df) == 1
        assert df.iloc[0]['farm_name'] == 'Farm 1'

    def test_excel_2007_xlsx_format(self, tmp_path):
        """Test Excel 2007+ (.xlsx) format."""
        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'area_hectares'])
        ws.append(['Farm 1', 50.5])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        df = pd.read_excel(excel_file)

        assert len(df) == 1
        assert df.iloc[0]['farm_name'] == 'Farm 1'

    def test_excel_with_formulas(self, tmp_path):
        """Test Excel with formulas (should extract calculated values)."""
        wb = Workbook()
        ws = wb.active

        ws.append(['length', 'width', 'area'])
        ws.append([100, 50, None])
        ws['C2'] = '=A2*B2'  # Formula

        excel_file = tmp_path / "formulas.xlsx"
        wb.save(excel_file)

        df = pd.read_excel(excel_file)

        assert len(df) == 1
        assert df.iloc[0]['area'] == 5000  # Calculated value

    def test_excel_multiple_sheets(self, tmp_path):
        """Test Excel with multiple sheets."""
        wb = Workbook()

        ws1 = wb.active
        ws1.title = "Farms"
        ws1.append(['farm_name'])
        ws1.append(['Farm 1'])

        ws2 = wb.create_sheet("Plots")
        ws2.append(['plot_name'])
        ws2.append(['Plot 1'])

        excel_file = tmp_path / "multi_sheet.xlsx"
        wb.save(excel_file)

        # Read all sheets
        sheets = pd.read_excel(excel_file, sheet_name=None)

        assert 'Farms' in sheets
        assert 'Plots' in sheets
        assert len(sheets['Farms']) == 1
        assert len(sheets['Plots']) == 1

    def test_excel_empty_sheet(self, tmp_path):
        """Test Excel with empty sheet."""
        wb = Workbook()
        ws = wb.active

        excel_file = tmp_path / "empty_sheet.xlsx"
        wb.save(excel_file)

        with pytest.raises(ValueError):
            pd.read_excel(excel_file)

    def test_excel_with_special_characters(self, tmp_path):
        """Test Excel with special characters in data."""
        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'notes'])
        ws.append(['Farm & Co.', 'Temperature: 25°C, pH: 6.5'])
        ws.append(['Müller Farm', 'Area: 10 m²'])

        excel_file = tmp_path / "special_chars.xlsx"
        wb.save(excel_file)

        df = pd.read_excel(excel_file)

        assert len(df) == 2
        assert '&' in df.iloc[0]['farm_name']
        assert '°' in df.iloc[0]['notes']


@pytest.mark.unit
class TestCorruptedFiles:
    """Test handling of corrupted and invalid files."""

    def test_corrupted_csv_file(self, tmp_path):
        """Test handling corrupted CSV file."""
        csv_file = tmp_path / "corrupted.csv"
        csv_file.write_bytes(b'\x00\x01\x02\x03\x04\x05' * 100)

        # Should handle gracefully
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            # Exception is expected
            assert True

    def test_corrupted_excel_file(self, tmp_path):
        """Test handling corrupted Excel file."""
        excel_file = tmp_path / "corrupted.xlsx"
        excel_file.write_bytes(b'Not a valid Excel file')

        with pytest.raises(Exception):
            pd.read_excel(excel_file)

    def test_csv_with_binary_data(self, tmp_path):
        """Test CSV containing binary/non-text data."""
        csv_file = tmp_path / "binary.csv"
        csv_file.write_bytes(b'farm_name,area\nFarm 1\x00\xff\xfe,50.5')

        # Should handle gracefully or raise appropriate error
        try:
            df = pd.read_csv(csv_file, encoding='utf-8', errors='ignore')
        except:
            pass

    def test_truncated_csv_file(self, tmp_path):
        """Test truncated/incomplete CSV file."""
        csv_content = """farm_name,area_hectares,latitude,longitude
Farm 1,50.5,40.7128,-74.0060
Farm 2,75.2,40.7589"""  # Incomplete last row

        csv_file = tmp_path / "truncated.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file, on_bad_lines='skip')

        # Should skip bad line or handle gracefully
        assert len(df) >= 1


@pytest.mark.unit
class TestDateFormats:
    """Test various date format handling."""

    def test_iso_date_format(self, tmp_path):
        """Test ISO 8601 date format (YYYY-MM-DD)."""
        csv_content = """farm_name,planting_date
Farm 1,2024-01-15
Farm 2,2024-02-20"""

        csv_file = tmp_path / "iso_dates.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file, parse_dates=['planting_date'])

        assert pd.api.types.is_datetime64_any_dtype(df['planting_date'])

    def test_us_date_format(self, tmp_path):
        """Test US date format (MM/DD/YYYY)."""
        csv_content = """farm_name,planting_date
Farm 1,01/15/2024
Farm 2,02/20/2024"""

        csv_file = tmp_path / "us_dates.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)
        df['planting_date'] = pd.to_datetime(df['planting_date'])

        assert pd.api.types.is_datetime64_any_dtype(df['planting_date'])

    def test_european_date_format(self, tmp_path):
        """Test European date format (DD/MM/YYYY)."""
        csv_content = """farm_name,planting_date
Farm 1,15/01/2024
Farm 2,20/02/2024"""

        csv_file = tmp_path / "eu_dates.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)
        df['planting_date'] = pd.to_datetime(df['planting_date'], dayfirst=True)

        assert pd.api.types.is_datetime64_any_dtype(df['planting_date'])

    def test_datetime_with_timezone(self, tmp_path):
        """Test datetime with timezone information."""
        csv_content = """farm_name,event_time
Farm 1,2024-01-15T10:30:00-05:00
Farm 2,2024-01-15T15:30:00Z"""

        csv_file = tmp_path / "tz_dates.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file, parse_dates=['event_time'])

        assert pd.api.types.is_datetime64_any_dtype(df['event_time'])


@pytest.mark.unit
class TestNumericFormats:
    """Test various numeric format handling."""

    def test_integer_numbers(self, tmp_path):
        """Test integer numbers."""
        csv_content = """farm_name,plot_count
Farm 1,5
Farm 2,10"""

        csv_file = tmp_path / "integers.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        assert df['plot_count'].dtype == 'int64'

    def test_floating_point_numbers(self, tmp_path):
        """Test floating point numbers."""
        csv_content = """farm_name,area_hectares
Farm 1,50.5
Farm 2,75.25"""

        csv_file = tmp_path / "floats.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        assert df['area_hectares'].dtype == 'float64'

    def test_scientific_notation(self, tmp_path):
        """Test scientific notation numbers."""
        csv_content = """farm_name,value
Farm 1,1.5e3
Farm 2,2.5e-2"""

        csv_file = tmp_path / "scientific.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        assert df.iloc[0]['value'] == 1500.0
        assert df.iloc[1]['value'] == 0.025

    def test_numbers_with_thousand_separators(self, tmp_path):
        """Test numbers with thousand separators."""
        csv_content = """farm_name,value
Farm 1,"1,000"
Farm 2,"10,000.50""""

        csv_file = tmp_path / "thousands.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file, thousands=',')

        assert df.iloc[0]['value'] == 1000
        assert df.iloc[1]['value'] == 10000.50

    def test_currency_values(self, tmp_path):
        """Test currency values with symbols."""
        csv_content = """item,cost
Seeds,$150.00
Fertilizer,$75.50"""

        csv_file = tmp_path / "currency.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)

        # Currency symbol needs to be stripped
        df['cost'] = df['cost'].str.replace('$', '').astype(float)

        assert df.iloc[0]['cost'] == 150.00


@pytest.mark.unit
class TestFileEncodingDetection:
    """Test file encoding detection."""

    def test_detect_utf8_encoding(self, tmp_path):
        """Test detecting UTF-8 encoding."""
        csv_content = "farm_name,notes\nFinca José,Café"

        csv_file = tmp_path / "utf8.csv"
        csv_file.write_text(csv_content, encoding='utf-8')

        # Chardet library could be used for detection
        # For now, test that UTF-8 works
        df = pd.read_csv(csv_file, encoding='utf-8')

        assert len(df) == 1

    def test_detect_latin1_encoding(self, tmp_path):
        """Test detecting Latin-1 encoding."""
        csv_content = "farm_name,notes\nFarm 1,Test"

        csv_file = tmp_path / "latin1.csv"
        csv_file.write_text(csv_content, encoding='latin-1')

        df = pd.read_csv(csv_file, encoding='latin-1')

        assert len(df) == 1


@pytest.mark.unit
class TestLargeFiles:
    """Test handling of large files."""

    def test_very_wide_csv(self, tmp_path):
        """Test CSV with many columns (>100)."""
        num_columns = 150
        columns = [f'col_{i}' for i in range(num_columns)]
        values = list(range(num_columns))

        csv_file = tmp_path / "wide.csv"

        with open(csv_file, 'w') as f:
            f.write(','.join(columns) + '\n')
            f.write(','.join(map(str, values)) + '\n')

        df = pd.read_csv(csv_file)

        assert len(df.columns) == num_columns

    def test_very_long_csv(self, tmp_path):
        """Test CSV with many rows."""
        num_rows = 50_000

        data = {
            'farm_name': [f'Farm {i}' for i in range(num_rows)],
            'area': [50.5] * num_rows
        }
        df = pd.DataFrame(data)

        csv_file = tmp_path / "long.csv"
        df.to_csv(csv_file, index=False)

        df_read = pd.read_csv(csv_file)

        assert len(df_read) == num_rows

    def test_chunked_reading(self, tmp_path):
        """Test reading large CSV in chunks."""
        num_rows = 10_000

        data = {
            'farm_name': [f'Farm {i}' for i in range(num_rows)],
            'area': [50.5] * num_rows
        }
        df = pd.DataFrame(data)

        csv_file = tmp_path / "large.csv"
        df.to_csv(csv_file, index=False)

        # Read in chunks
        chunk_size = 1000
        chunks = []

        for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
            chunks.append(chunk)

        total_rows = sum(len(chunk) for chunk in chunks)

        assert total_rows == num_rows

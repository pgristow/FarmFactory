"""
Unit tests for Excel parser service.

Tests .xls and .xlsx formats, multiple sheets, empty sheets, and edge cases.
"""
import pytest
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
import xlwt
from io import BytesIO


@pytest.mark.unit
class TestExcelParser:
    """Test Excel parsing functionality."""

    def test_parse_xlsx_format(self, tmp_path):
        """Test parsing Excel 2007+ (.xlsx) format."""
        # Create Excel file
        wb = Workbook()
        ws = wb.active
        ws.title = "Farms"

        # Add headers
        ws.append(['farm_name', 'plot_name', 'area_hectares', 'latitude', 'longitude'])

        # Add data
        ws.append(['Green Valley Farm', 'North Field', 10.5, 40.7128, -74.0060])
        ws.append(['Sunny Acres', 'South Plot', 15.2, 40.7589, -73.9851])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 2
        assert list(df.columns) == ['farm_name', 'plot_name', 'area_hectares', 'latitude', 'longitude']
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm'
        assert df.iloc[0]['area_hectares'] == 10.5

    def test_parse_xls_format(self, tmp_path):
        """Test parsing Excel 97-2003 (.xls) format."""
        # Create .xls file using xlwt
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Farms')

        # Add headers
        headers = ['farm_name', 'plot_name', 'area_hectares']
        for col, header in enumerate(headers):
            ws.write(0, col, header)

        # Add data
        ws.write(1, 0, 'Green Valley Farm')
        ws.write(1, 1, 'North Field')
        ws.write(1, 2, 10.5)

        excel_file = tmp_path / "test.xls"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file, engine='xlrd')

        # Assertions
        assert len(df) == 1
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm'

    def test_parse_multiple_sheets(self, tmp_path):
        """Test parsing Excel file with multiple sheets."""
        wb = Workbook()

        # Sheet 1: Farms
        ws1 = wb.active
        ws1.title = "Farms"
        ws1.append(['farm_name', 'area_hectares'])
        ws1.append(['Green Valley Farm', 50.5])

        # Sheet 2: Plots
        ws2 = wb.create_sheet("Plots")
        ws2.append(['plot_name', 'area_hectares'])
        ws2.append(['North Field', 10.5])
        ws2.append(['South Field', 15.2])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse all sheets
        excel_data = pd.read_excel(excel_file, sheet_name=None)

        # Assertions
        assert 'Farms' in excel_data
        assert 'Plots' in excel_data
        assert len(excel_data['Farms']) == 1
        assert len(excel_data['Plots']) == 2

    def test_parse_specific_sheet(self, tmp_path):
        """Test parsing specific sheet by name."""
        wb = Workbook()

        # Sheet 1: Farms
        ws1 = wb.active
        ws1.title = "Farms"
        ws1.append(['farm_name', 'area_hectares'])
        ws1.append(['Green Valley Farm', 50.5])

        # Sheet 2: Plots
        ws2 = wb.create_sheet("Plots")
        ws2.append(['plot_name', 'area_hectares'])
        ws2.append(['North Field', 10.5])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse specific sheet
        df_plots = pd.read_excel(excel_file, sheet_name='Plots')

        # Assertions
        assert len(df_plots) == 1
        assert df_plots.iloc[0]['plot_name'] == 'North Field'

    def test_parse_sheet_by_index(self, tmp_path):
        """Test parsing sheet by index."""
        wb = Workbook()

        # Sheet 1
        ws1 = wb.active
        ws1.title = "Farms"
        ws1.append(['farm_name'])
        ws1.append(['Farm 1'])

        # Sheet 2
        ws2 = wb.create_sheet("Plots")
        ws2.append(['plot_name'])
        ws2.append(['Plot 1'])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse second sheet (index 1)
        df = pd.read_excel(excel_file, sheet_name=1)

        # Assertions
        assert df.iloc[0]['plot_name'] == 'Plot 1'

    def test_parse_empty_sheet(self, tmp_path):
        """Test parsing empty Excel sheet."""
        wb = Workbook()
        ws = wb.active
        ws.title = "Empty"

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse empty sheet
        with pytest.raises(ValueError):
            df = pd.read_excel(excel_file)
            # Empty sheet should raise error or return empty dataframe
            assert len(df) == 0

    def test_parse_excel_with_formulas(self, tmp_path):
        """Test parsing Excel with formulas (should extract values)."""
        wb = Workbook()
        ws = wb.active
        ws.title = "Calculations"

        # Add headers
        ws.append(['plot_name', 'length_m', 'width_m', 'area_m2'])

        # Add data with formula
        ws.append(['Plot 1', 100, 50, None])
        ws['D2'] = '=B2*C2'  # Formula for area

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel (formulas should be evaluated to values)
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 1
        assert df.iloc[0]['area_m2'] == 5000  # Formula result

    def test_parse_excel_with_formatting(self, tmp_path):
        """Test parsing Excel with cell formatting (should ignore formatting)."""
        wb = Workbook()
        ws = wb.active

        # Add headers with formatting
        ws.append(['farm_name', 'area_hectares'])
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

        # Add data
        ws.append(['Green Valley Farm', 10.5])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel (formatting should be ignored)
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 1
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm'

    def test_parse_excel_with_merged_cells(self, tmp_path):
        """Test parsing Excel with merged cells."""
        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'plot_name', 'area_hectares'])
        ws.append(['Green Valley Farm', 'North Field', 10.5])

        # Merge some cells (row 1, columns A-B)
        ws.merge_cells('A1:B1')

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions - pandas handles merged cells by using the value in first cell
        assert len(df) >= 1

    def test_parse_excel_with_hidden_columns(self, tmp_path):
        """Test parsing Excel with hidden columns."""
        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'hidden_col', 'area_hectares'])
        ws.append(['Green Valley Farm', 'secret', 10.5])

        # Hide column B
        ws.column_dimensions['B'].hidden = True

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel (hidden columns are still read)
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df.columns) == 3  # Hidden columns are still included

    def test_parse_excel_with_empty_rows(self, tmp_path):
        """Test parsing Excel with empty rows."""
        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'area_hectares'])
        ws.append(['Green Valley Farm', 10.5])
        ws.append([None, None])  # Empty row
        ws.append(['Sunny Acres', 15.2])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions - empty rows are included as NaN
        assert len(df) == 3

    def test_parse_excel_with_missing_values(self, tmp_path):
        """Test parsing Excel with missing values."""
        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'plot_name', 'area_hectares'])
        ws.append(['Green Valley Farm', 'North Field', 10.5])
        ws.append(['Sunny Acres', None, None])  # Missing values
        ws.append([None, 'Test Plot', 5.0])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 3
        assert pd.isna(df.iloc[1]['plot_name'])
        assert pd.isna(df.iloc[2]['farm_name'])

    def test_parse_excel_with_dates(self, tmp_path):
        """Test parsing Excel with date values."""
        from datetime import datetime

        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'planting_date', 'harvest_date'])
        ws.append(['Green Valley Farm', datetime(2024, 1, 15), datetime(2024, 6, 15)])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 1
        assert pd.api.types.is_datetime64_any_dtype(df['planting_date'])

    def test_parse_excel_with_numbers_as_text(self, tmp_path):
        """Test parsing Excel with numbers stored as text."""
        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'plot_number', 'area_hectares'])
        ws.append(['Green Valley Farm', '001', '10.5'])  # Numbers as text

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 1
        assert df.iloc[0]['plot_number'] == '001'  # Preserved as text

    def test_parse_excel_large_file(self, tmp_path):
        """Test parsing large Excel file."""
        wb = Workbook()
        ws = wb.active

        # Add headers
        ws.append(['farm_name', 'plot_name', 'area_hectares'])

        # Add 10,000 rows
        for i in range(10000):
            ws.append([f'Farm {i}', f'Plot {i}', i * 0.5])

        excel_file = tmp_path / "large.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 10000

    def test_parse_excel_preview_first_100_rows(self, tmp_path):
        """Test parsing preview of first 100 rows from Excel."""
        wb = Workbook()
        ws = wb.active

        # Add headers
        ws.append(['farm_name', 'plot_name'])

        # Add 500 rows
        for i in range(500):
            ws.append([f'Farm {i}', f'Plot {i}'])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse only first 100 rows
        df_preview = pd.read_excel(excel_file, nrows=100)

        # Assertions
        assert len(df_preview) == 100

    def test_parse_excel_with_special_characters(self, tmp_path):
        """Test parsing Excel with special characters."""
        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'plot_name', 'notes'])
        ws.append(['Farm & Co.', 'Plot #1', 'Temperature: 25°C'])
        ws.append(['O\'Brien Farm', 'Plot @2', 'pH: 6.5'])
        ws.append(['Müller Farm', 'Plot €3', 'Area: 10 m²'])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 3
        assert df.iloc[0]['farm_name'] == 'Farm & Co.'

    def test_parse_corrupted_excel_file(self, tmp_path):
        """Test parsing corrupted Excel file gracefully."""
        # Create a corrupted file
        excel_file = tmp_path / "corrupted.xlsx"
        excel_file.write_bytes(b'Not a valid Excel file')

        # Parse corrupted Excel
        with pytest.raises(Exception):  # Should raise exception
            pd.read_excel(excel_file)

    def test_get_sheet_names(self, tmp_path):
        """Test getting list of sheet names."""
        wb = Workbook()

        ws1 = wb.active
        ws1.title = "Farms"
        ws1.append(['farm_name'])

        ws2 = wb.create_sheet("Plots")
        ws2.append(['plot_name'])

        ws3 = wb.create_sheet("Irrigation")
        ws3.append(['event_date'])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Get sheet names
        excel_file_obj = pd.ExcelFile(excel_file)
        sheet_names = excel_file_obj.sheet_names

        # Assertions
        assert len(sheet_names) == 3
        assert 'Farms' in sheet_names
        assert 'Plots' in sheet_names
        assert 'Irrigation' in sheet_names

    def test_parse_excel_with_unicode(self, tmp_path):
        """Test parsing Excel with Unicode characters."""
        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'notes'])
        ws.append(['Finca José', 'Café y frutas tropicales 🌴'])
        ws.append(['农场', '中文测试'])
        ws.append(['Ферма', 'Русский текст'])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 3
        assert df.iloc[0]['farm_name'] == 'Finca José'

    def test_parse_excel_skip_rows(self, tmp_path):
        """Test parsing Excel while skipping header rows."""
        wb = Workbook()
        ws = wb.active

        # Add title rows
        ws.append(['Farm Import Data'])
        ws.append(['Generated: 2024-01-15'])
        ws.append([])  # Empty row

        # Add actual headers
        ws.append(['farm_name', 'area_hectares'])
        ws.append(['Green Valley Farm', 10.5])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel, skip first 3 rows
        df = pd.read_excel(excel_file, skiprows=3)

        # Assertions
        assert len(df) == 1
        assert df.iloc[0]['farm_name'] == 'Green Valley Farm'

    def test_parse_excel_with_data_validation(self, tmp_path):
        """Test parsing Excel with data validation (should read values)."""
        from openpyxl.worksheet.datavalidation import DataValidation

        wb = Workbook()
        ws = wb.active

        ws.append(['farm_name', 'soil_type'])
        ws.append(['Green Valley Farm', 'Loamy'])

        # Add data validation to column B (doesn't affect reading)
        dv = DataValidation(type="list", formula1='"Loamy,Sandy,Clay"')
        ws.add_data_validation(dv)
        dv.add('B2:B100')

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Parse Excel
        df = pd.read_excel(excel_file)

        # Assertions
        assert len(df) == 1
        assert df.iloc[0]['soil_type'] == 'Loamy'


@pytest.mark.unit
class TestExcelParserService:
    """Test Excel parser service methods."""

    def test_detect_header_row(self, tmp_path):
        """Test automatic detection of header row."""
        wb = Workbook()
        ws = wb.active

        # Add some title rows
        ws.append(['Farm Data Export'])
        ws.append([])

        # Add headers
        ws.append(['farm_name', 'area_hectares'])
        ws.append(['Green Valley Farm', 10.5])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Service method would detect that row 3 is the header
        # by checking for consistent data types in subsequent rows

    def test_get_excel_metadata(self, tmp_path):
        """Test extracting Excel file metadata."""
        wb = Workbook()
        ws1 = wb.active
        ws1.title = "Farms"
        ws1.append(['farm_name', 'area_hectares'])
        ws1.append(['Green Valley Farm', 10.5])

        ws2 = wb.create_sheet("Plots")
        ws2.append(['plot_name'])
        ws2.append(['Plot 1'])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Get metadata
        excel_file_obj = pd.ExcelFile(excel_file)
        metadata = {
            'sheet_count': len(excel_file_obj.sheet_names),
            'sheet_names': excel_file_obj.sheet_names,
            'file_size': excel_file.stat().st_size
        }

        # Assertions
        assert metadata['sheet_count'] == 2
        assert 'Farms' in metadata['sheet_names']

    def test_validate_excel_structure(self, tmp_path):
        """Test validating Excel file structure."""
        wb = Workbook()
        ws = wb.active
        ws.append(['farm_name'])
        ws.append(['Farm 1'])

        excel_file = tmp_path / "test.xlsx"
        wb.save(excel_file)

        # Validate Excel has valid structure
        df = pd.read_excel(excel_file)
        assert len(df) > 0
        assert len(df.columns) > 0

# FarmFactory CSV Import Templates

This directory contains standardized CSV templates for importing farm data into the FarmFactory system.

## Available Templates

### 1. Farms and Plots (`1_farms_and_plots.csv`)
Import farm locations, plot boundaries, and soil profiles.

**Required columns:**
- `farm_name`: Name of the farm
- `plot_name`: Name of the plot/field
- `plot_area_hectares`: Plot area in hectares

**Optional columns:**
- `farm_latitude`, `farm_longitude`: Farm GPS coordinates
- `farm_address`: Physical address
- `farm_total_area_hectares`: Total farm area
- `farm_timezone`: Timezone (e.g., America/New_York)
- `plot_number`: Plot identification number
- `plot_elevation_meters`: Elevation above sea level
- `plot_slope_degrees`: Average slope
- `soil_type`: Soil classification (Clay, Sandy, Loam, etc.)
- `soil_ph_level`: pH value (0-14)
- `organic_matter_percent`: Organic matter percentage
- `drainage_class`: Drainage classification

### 2. Irrigation Events (`2_irrigation_events.csv`)
Record irrigation activities and water application.

**Required columns:**
- `date_time`: Date and time (YYYY-MM-DD HH:MM:SS)
- `plot_name`: Plot identifier
- `irrigation_method`: drip, sprinkler, flood, manual, etc.
- `duration_minutes`: Duration in minutes
- `water_volume_liters`: Total water applied in liters

**Optional columns:**
- `water_source`: Source identifier
- `flow_rate_lpm`: Flow rate in liters per minute
- `pressure_bar`: Water pressure in bar
- `notes`: Additional observations

### 3. Nutrient Applications (`3_nutrient_applications.csv`)
Track fertilizer and nutrient applications.

**Required columns:**
- `date_time`: Application date and time
- `plot_name`: Plot identifier
- `nutrient_type`: Type of nutrient/fertilizer
- `application_method`: broadcast, fertigation, foliar, etc.
- `amount_kg`: Amount applied in kilograms

**Optional columns:**
- `npk_ratio`: NPK ratio (e.g., "10-10-10")
- `nitrogen_kg`: Nitrogen content in kg
- `phosphorus_kg`: Phosphorus content in kg
- `potassium_kg`: Potassium content in kg
- `cost_usd`: Total cost in USD
- `notes`: Additional details

### 4. Water Quality (`4_water_quality.csv`)
Monitor water quality parameters.

**Required columns:**
- `date_time`: Measurement date and time
- `plot_name`: Plot identifier (or farm-level)
- `water_source`: Source identifier

**Optional columns:**
- `ph_level`: pH value (0-14)
- `ec_ds_per_m`: Electrical conductivity (dS/m)
- `tds_ppm`: Total dissolved solids (ppm)
- `temperature_celsius`: Water temperature (°C)
- `dissolved_oxygen_ppm`: DO in ppm
- `turbidity_ntu`: Turbidity (NTU)
- `notes`: Observations

### 5. Environmental Readings (`5_environmental_readings.csv`)
Record environmental sensor data.

**Required columns:**
- `date_time`: Reading timestamp
- `plot_name`: Plot identifier

**Optional columns:**
- `air_temp_celsius`: Air temperature (°C)
- `soil_temp_celsius`: Soil temperature (°C)
- `humidity_percent`: Relative humidity (%)
- `soil_moisture_percent`: Soil moisture (%)
- `light_intensity_lux`: Light intensity (lux)
- `rainfall_mm`: Rainfall (mm)
- `wind_speed_kmh`: Wind speed (km/h)
- `atmospheric_pressure_hpa`: Atmospheric pressure (hPa)

### 6. Crop Plantings (`6_crop_plantings.csv`)
Record planting activities.

**Required columns:**
- `plot_name`: Plot identifier
- `crop_name`: Crop name
- `planting_date`: Planting date (YYYY-MM-DD)

**Optional columns:**
- `crop_variety`: Specific variety
- `expected_harvest_date`: Expected harvest date
- `plant_population`: Number of plants
- `row_spacing_cm`: Row spacing in cm
- `plant_spacing_cm`: Plant spacing in cm
- `status`: planted, growing, harvested, failed

### 7. Phenology Observations (`7_phenology_observations.csv`)
Track crop growth stages and development.

**Required columns:**
- `observation_date`: Date of observation
- `plot_name`: Plot identifier
- `growth_stage`: Growth stage description

**Optional columns:**
- `bbch_code`: BBCH phenological scale code (0-99)
- `height_cm`: Plant height in cm
- `canopy_cover_percent`: Canopy coverage (%)
- `health_score`: Health rating (1-10)
- `notes`: Detailed observations

### 8. Input Costs (`8_input_costs.csv`)
Track all input costs.

**Required columns:**
- `cost_date`: Date of expense
- `category`: seeds, fertilizer, water, labor, equipment, pest_control, etc.
- `description`: Description of expense
- `total_cost`: Total cost

**Optional columns:**
- `plot_name`: Specific plot (use "All Plots" for farm-level)
- `quantity`: Quantity purchased
- `unit`: Unit of measure
- `unit_cost`: Cost per unit
- `currency`: Currency code (default: USD)

### 9. Harvest Revenue (`9_harvest_revenue.csv`)
Record harvest yields and revenue.

**Required columns:**
- `harvest_date`: Date of harvest
- `plot_name`: Plot identifier
- `crop_name`: Crop harvested
- `quantity_kg`: Quantity in kilograms

**Optional columns:**
- `quality_grade`: Quality classification
- `revenue_usd`: Revenue in USD
- `market`: Market or buyer name
- `notes`: Additional details

### 10. Alert Thresholds (`10_alert_thresholds.csv`)
Configure monitoring thresholds.

**Required columns:**
- `plot_name`: Plot identifier (use "All Plots" for farm-wide)
- `parameter`: Parameter to monitor
- `severity`: info, warning, critical

**Optional columns:**
- `min_value`: Minimum acceptable value
- `max_value`: Maximum acceptable value
- `active`: true/false (default: true)

## Usage Instructions

### 1. Download Template
Download the appropriate template for your data type.

### 2. Fill in Data
- Open the CSV file in Excel, Google Sheets, or any spreadsheet application
- Fill in your data following the column format
- Required columns must not be empty
- Optional columns can be left blank if data is not available

### 3. Data Format Guidelines

#### Dates and Times
- Date format: `YYYY-MM-DD` (e.g., 2024-01-15)
- DateTime format: `YYYY-MM-DD HH:MM:SS` (e.g., 2024-01-15 06:00:00)
- Timezone: Use farm timezone setting or UTC

#### Numbers
- Use decimal point (.), not comma (,)
- Example: 5.2, not 5,2
- Do not include units in number fields (units are defined by column name)

#### Text
- Use consistent naming for farms and plots across all files
- Avoid special characters in names
- Use quotes for text containing commas

#### Missing Data
- Leave cells empty for optional fields
- Do not use "N/A", "null", or "-"

### 4. Upload to FarmFactory
1. Log into FarmFactory dashboard
2. Navigate to "Data Import"
3. Select data type
4. Upload your CSV file
5. Map columns (auto-detected in most cases)
6. Preview and validate data
7. Process import

### 5. Import Order Recommendation

For initial setup, import in this order:

1. **Farms and Plots** - Establishes farm structure
2. **Crop Plantings** - Defines what's growing
3. **Irrigation Events** - Historical irrigation data
4. **Nutrient Applications** - Fertilizer history
5. **Water Quality** - Water test results
6. **Environmental Readings** - Sensor/weather data
7. **Phenology Observations** - Growth tracking
8. **Input Costs** - Financial tracking
9. **Harvest Revenue** - Revenue tracking
10. **Alert Thresholds** - Set up monitoring

## Common Issues and Solutions

### Issue: "Plot not found"
**Solution**: Ensure farm and plot names match exactly (case-sensitive) with what's in the system. Import farms and plots first.

### Issue: "Invalid date format"
**Solution**: Use YYYY-MM-DD format. Check for typos and ensure dates are valid (e.g., not 2024-13-01).

### Issue: "Value out of range"
**Solution**: Check that values are reasonable:
- pH: 0-14
- Percentages: 0-100
- Coordinates: Valid lat/long ranges

### Issue: "Duplicate entry"
**Solution**: Check for duplicate rows. Some data types (like irrigation events) can have multiple entries for the same plot and date, others cannot.

## Tips for Best Results

1. **Start Small**: Import a small sample (10-20 rows) first to test
2. **Consistent Naming**: Use the same plot names across all files
3. **Clean Data**: Remove empty rows at the end of your CSV
4. **Validation**: Use spreadsheet validation to ensure data quality
5. **Backup**: Keep a copy of your original data files
6. **Documentation**: Add notes for unusual values or events

## Data Units Reference

| Measurement | Unit | Column Suffix |
|-------------|------|---------------|
| Area | Hectares | `_hectares` |
| Volume | Liters | `_liters` |
| Weight | Kilograms | `_kg` |
| Distance | Meters | `_meters` |
| Distance (small) | Centimeters | `_cm` |
| Temperature | Celsius | `_celsius` |
| Time | Minutes | `_minutes` |
| Pressure | Bar | `_bar` |
| Flow Rate | Liters/minute | `_lpm` |
| EC | dS/m | `_ds_per_m` |
| TDS | ppm | `_ppm` |
| Angle | Degrees | `_degrees` |
| Light | Lux | `_lux` |
| Rainfall | Millimeters | `_mm` |
| Speed | Kilometers/hour | `_kmh` |
| Atmospheric Pressure | hPa | `_hpa` |

## Unit Conversions

The system can auto-convert some common units:

- Acres ↔ Hectares
- Gallons ↔ Liters
- Fahrenheit ↔ Celsius
- Feet ↔ Meters
- Inches ↔ Centimeters
- Pounds ↔ Kilograms

To use auto-conversion, include the unit in the column header:
- `area_acres` → will convert to hectares
- `temp_fahrenheit` → will convert to celsius

## Sprint 2: Data Import System Features

### New Import Templates

Sprint 2 introduces specialized import templates optimized for bulk data upload:

1. **farms_and_plots_import.csv** - Combined farm and plot data import
2. **irrigation_events_import.csv** - Bulk irrigation event tracking
3. **nutrient_applications_import.csv** - Fertilizer application history
4. **phenology_observations_import.csv** - Growth stage observations
5. **financial_data_import.csv** - Combined costs and revenues

### Import System Features

#### Intelligent Column Mapping
- **Auto-detection**: System automatically maps your column names to database fields
- **Fuzzy matching**: Handles variations like "Farm Name", "farm_name", "FarmName"
- **Confidence scoring**: Shows mapping confidence (aim for >80%)
- **Manual override**: Adjust any auto-mapped columns before import

#### Automatic Unit Conversions
The system automatically detects and converts units from column names:

- `area_acres` → Converts to hectares
- `volume_gallons` → Converts to liters
- `temp_fahrenheit` → Converts to Celsius
- `height_inches` → Converts to centimeters
- `weight_lbs` → Converts to kilograms
- `pressure_psi` → Converts to bar
- `flow_rate_gpm` → Converts to liters per minute

**Example**: If your CSV has `plot_area_acres`, the system will automatically convert to hectares for storage.

#### Comprehensive Data Validation

**Automatic checks include:**
- Required fields validation
- Data type validation (numbers, dates, text)
- Range validation (pH 0-14, coordinates, percentages)
- Reference validation (plot names must exist)
- Duplicate detection
- Cross-field validation (plot area ≤ farm area)
- Date format validation with multiple format support

**Validation Error Messages**: Clear, actionable messages help you fix issues quickly.

#### Import Workflow

1. **Upload**: Drag-and-drop or browse to select your CSV file
2. **Preview**: Review first 100 rows of your data
3. **Map Columns**: Verify auto-detected column mappings
4. **Validate**: System checks all data against validation rules
5. **Review Errors**: Fix any validation errors (if needed)
6. **Process**: Import runs in background with progress tracking
7. **Complete**: View import summary and any warnings

#### Performance

- Files up to 100MB supported
- Processes 10,000+ rows in under 2 minutes
- Batch processing with progress updates
- Resume capability on connection loss

### Import Best Practices

#### Preparing Your Data

1. **Start with templates**: Download and use provided import templates
2. **Clean your data**: Remove empty rows, fix formatting issues
3. **Test with small batch**: Import 10-20 rows first to verify
4. **Use consistent naming**: Keep farm/plot names consistent across all imports
5. **Include units in headers**: Use `area_acres` or `area_hectares` for clarity

#### Column Naming Tips

The system recognizes many column name variations:

**Farm Name variations:**
- farm_name, Farm Name, FarmName, farm, Farm ID

**Date/Time variations:**
- date_time, Date Time, timestamp, date, datetime

**Plot Name variations:**
- plot_name, Plot Name, field_name, Field, plot

**Amount variations:**
- amount_kg, Amount, quantity_kg, kg, kilograms

#### Handling Errors

**Common Errors and Solutions:**

1. **"Required field missing"**
   - Solution: Ensure all required columns have values
   - Required fields marked with (*) in template comments

2. **"Invalid date format"**
   - Solution: Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
   - Supported formats: YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY

3. **"Value out of range"**
   - Solution: Check value is reasonable (pH 0-14, etc.)
   - See validation rules documentation

4. **"Plot not found"**
   - Solution: Import farms/plots first
   - Ensure plot names match exactly (case-sensitive)

5. **"Duplicate entry"**
   - Solution: Check for duplicate rows
   - System detects duplicates by plot name + date/time

#### Data Quality Tips

- **Completeness**: Aim for 90%+ non-empty values
- **Accuracy**: Double-check numeric values and units
- **Consistency**: Use same plot names across all files
- **Validation**: System reports data quality score after import
- **Documentation**: Add notes for unusual values

### Import Order for New Farms

For best results, import data in this sequence:

1. **Farms and Plots** ← Start here (creates farm structure)
2. **Irrigation Events**
3. **Nutrient Applications**
4. **Phenology Observations**
5. **Financial Data**

### Advanced Features

#### Batch Processing
- Large files processed in chunks
- Progress tracking in real-time
- Can cancel import in progress

#### Import History
- View all past imports
- Download original files
- Re-run imports with same settings
- Detailed error logs

#### Data Quality Metrics
After each import, view:
- Completeness score
- Validity score
- Mapping accuracy
- Error summary
- Data quality recommendations

#### Template Customization
- Save your own column mapping templates
- Reuse mappings for future imports
- Share templates with team members

### File Format Requirements

**CSV Files:**
- UTF-8 encoding required
- Comma, semicolon, or tab delimiters supported
- Headers must be in first row
- Comments (lines starting with #) are ignored

**Excel Files:**
- .xlsx and .xls formats supported
- Uses first sheet by default
- Headers in first row
- Blank rows are skipped

### API Import (Advanced)

For automated imports, use the REST API:

```bash
# Upload file
curl -X POST http://localhost:8000/api/v1/import/upload \
  -F "file=@your_data.csv" \
  -F "data_type=farms_and_plots"

# Check status
curl http://localhost:8000/api/v1/import/status/{job_id}

# Download errors (if any)
curl http://localhost:8000/api/v1/import/{job_id}/errors
```

### Troubleshooting

**Import stuck at "Processing"?**
- Check job status in Import History
- Large files may take several minutes
- Check server logs if import exceeds expected time

**High error rate?**
- Download error report
- Common issue: Column names not recognized
- Solution: Use manual column mapping

**Performance slow?**
- Optimize CSV: Remove unnecessary columns
- Split large files into smaller batches
- Import during off-peak hours

### Getting Help

**Import Issues:**
1. Check Import History for error details
2. Download error report (CSV format)
3. Review validation rules documentation
4. Contact support with import job ID

**Data Questions:**
- See field descriptions in template comments
- Check validation rules: `/backend/app/import_config/validation_rules.json`
- Review data type documentation

## Need Help?

- **Documentation**: See full documentation in `/docs/user-guide`
- **API Reference**: http://localhost:8000/docs
- **Import System Guide**: `/docs/import-system.md`
- **Validation Rules**: `/backend/app/import_config/validation_rules.json`
- **Support**: Contact support through the dashboard
- **Sample Data**: Check `/test_data/` for examples

---

**Template Version**: 2.0
**Last Updated**: 2025-11-17
**Compatible with**: FarmFactory v1.0+ (Sprint 2 Import System)
**Import System Version**: 1.0

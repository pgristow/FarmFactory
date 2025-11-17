# FarmFactory Dashboards User Guide

**Version**: 1.0
**Last Updated**: 2025-11-17
**Audience**: Farmers, Farm Managers, Agricultural Technicians

---

## Table of Contents

1. [Introduction](#introduction)
2. [Water Management Dashboard](#water-management-dashboard)
3. [Nutrient Management Dashboard](#nutrient-management-dashboard)
4. [Environmental Monitoring Dashboard](#environmental-monitoring-dashboard)
5. [Crop Performance Dashboard](#crop-performance-dashboard)
6. [Financial Dashboard](#financial-dashboard)
7. [How to Use Dashboards](#how-to-use-dashboards)
8. [Understanding Charts](#understanding-charts)
9. [Understanding KPIs](#understanding-kpis)
10. [Filtering and Exporting Data](#filtering-and-exporting-data)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

FarmFactory dashboards provide real-time visualization of your farm's operational data. Each dashboard focuses on a specific aspect of farm management, displaying key performance indicators (KPIs) and interactive charts to help you make data-driven decisions.

### What You'll Find on Each Dashboard

- **KPI Cards**: Quick metrics showing current performance
- **Interactive Charts**: Visual representations of trends and patterns
- **Date Range Filters**: Control the time period displayed
- **Export Options**: Download data for further analysis

---

## Water Management Dashboard

### Purpose

Monitor irrigation practices, water usage efficiency, and costs to optimize water consumption and reduce expenses.

### Available KPIs

#### Total Water Used (30 Days)
- **What it shows**: Total irrigation water volume in the last 30 days
- **Units**: Liters
- **Target**: Keep under 75,000 liters per plot
- **Color codes**:
  - Green (Good): ≤ 50,000 liters
  - Orange (Warning): 50,000-75,000 liters
  - Red (Critical): > 75,000 liters

#### Water Use Efficiency
- **What it shows**: Liters of water needed to produce 1 kg of crop yield
- **Units**: Liters/kg
- **Target**: 200 liters/kg or less
- **How to interpret**: Lower is better. If above 350, you may be over-irrigating.

#### Irrigation Frequency
- **What it shows**: Average number of irrigation events per week
- **Units**: Events/week
- **Target**: 2-4 events per week
- **How to interpret**: Outside this range may indicate scheduling issues.

#### Cost Per Cubic Meter
- **What it shows**: Average cost of water per cubic meter
- **Units**: USD/m³
- **Target**: $0.50 or less
- **How to interpret**: Track to identify cost trends and optimize water sources.

### Available Charts

#### Water Usage Over Time
- **Type**: Line chart
- **Shows**: Daily water consumption trends
- **Use for**: Identifying seasonal patterns and unusual spikes
- **Time period**: Last 30 days (adjustable)

#### Water Distribution by Method
- **Type**: Pie chart
- **Shows**: Percentage breakdown by irrigation method (drip, sprinkler, flood, etc.)
- **Use for**: Understanding which methods consume most water
- **Tip**: Drip irrigation typically uses 30-50% less water than flood irrigation

#### Irrigation Frequency
- **Type**: Bar chart
- **Shows**: Number of irrigation events per week
- **Use for**: Monitoring irrigation consistency
- **Tip**: Consistent frequency indicates good scheduling

### Use Cases

1. **Reduce Water Costs**: Monitor usage patterns to identify opportunities to reduce consumption
2. **Optimize Irrigation Schedules**: Adjust frequency based on weekly trends
3. **Evaluate Method Efficiency**: Compare water usage across different irrigation methods
4. **Detect Leaks**: Sudden spikes in usage may indicate system leaks

---

## Nutrient Management Dashboard

### Purpose

Track fertilizer applications, monitor NPK balance, and optimize nutrient use efficiency to improve crop health and reduce costs.

### Available KPIs

#### NPK Balance (Current)
- **What it shows**: Current nitrogen (N), phosphorus (P), and potassium (K) levels per hectare
- **Units**: kg/ha
- **Target**: N: 100-140, P: 50-70, K: 80-120 kg/ha
- **Color codes**:
  - Green (Good): Within target range
  - Orange (Warning): Outside target range
- **How to interpret**: Compare actual levels to optimal ranges for your crop

#### Nutrient Use Efficiency
- **What it shows**: Kg of crop yield produced per kg of fertilizer applied
- **Units**: kg yield/kg fertilizer
- **Target**: 15 or higher
- **Color codes**:
  - Green (Excellent): ≥ 20
  - Light Green (Good): 15-20
  - Orange (Warning): 10-15
  - Red (Critical): < 10
- **How to interpret**: Higher values mean better conversion of fertilizer to yield

#### Nutrient Cost Per Hectare
- **What it shows**: Total fertilizer expenses per hectare
- **Units**: USD/ha
- **Target**: $500 or less
- **How to interpret**: Track over seasons to budget accurately

#### Application Frequency
- **What it shows**: Average fertilizer applications per month
- **Units**: Applications/month
- **Target**: 2-4 applications per month
- **How to interpret**: Too frequent may indicate over-fertilization

### Available Charts

#### NPK Balance Over Time
- **Type**: Multi-line chart
- **Shows**: Trends of nitrogen, phosphorus, and potassium applications
- **Use for**: Ensuring balanced nutrition throughout growth stages
- **Time period**: Last 90 days (adjustable)
- **Tip**: Different growth stages require different NPK ratios

#### Nutrient Cost Over Time
- **Type**: Area chart (cumulative)
- **Shows**: Running total of fertilizer costs
- **Use for**: Budget tracking and cost forecasting
- **Time period**: Last 90 days

#### Nutrient Type Breakdown
- **Type**: Pie chart
- **Shows**: Distribution of organic vs. synthetic fertilizers
- **Use for**: Tracking fertilizer diversity
- **Tip**: Balanced use of organic and synthetic can improve soil health

### Use Cases

1. **Match Growth Stage Needs**: Adjust NPK ratios based on crop development
2. **Budget Planning**: Track costs to predict seasonal expenses
3. **Soil Health Monitoring**: Balance organic and synthetic applications
4. **Optimize Application Timing**: Identify most effective application schedules

---

## Environmental Monitoring Dashboard

### Purpose

Monitor real-time weather and soil conditions to make informed decisions about irrigation, planting, and crop protection.

### Available KPIs

#### Average Temperature (7 Days)
- **What it shows**: Mean air temperature over the last week
- **Units**: °C
- **Optimal range**: 20-28°C (varies by crop)
- **Color codes**:
  - Green (Optimal): 20-28°C
  - Yellow (Acceptable): 15-32°C
  - Red (Critical): Outside 15-32°C
- **How to interpret**: Sustained extremes may stress crops

#### Average Soil Moisture
- **What it shows**: Current average soil moisture percentage (last 24 hours)
- **Units**: %
- **Target**: 60%
- **Optimal range**: 55-75%
- **Color codes**:
  - Green (Excellent): 55-75%
  - Light Green (Good): 40-85%
  - Orange (Warning): 30-95%
  - Red (Critical): < 30% or > 95%
- **How to interpret**:
  - < 30%: Risk of wilting
  - 55-75%: Ideal for most crops
  - > 85%: Risk of root disease

#### Total Rainfall (30 Days)
- **What it shows**: Cumulative rainfall in the last month
- **Units**: mm
- **Color codes**:
  - Red (Drought): < 25 mm
  - Orange (Low): 25-50 mm
  - Green (Normal): 50-150 mm
  - Blue (High): > 150 mm
- **How to interpret**: Adjust irrigation based on natural rainfall

#### Growing Degree Days (GDD)
- **What it shows**: Accumulated heat units since planting
- **Units**: GDD
- **How to interpret**: Used to predict crop development stages
- **Tip**: Compare to expected GDD for your crop variety to estimate maturity

### Available Charts

#### Temperature & Humidity Trends
- **Type**: Multi-line chart (dual Y-axes)
- **Shows**: Hourly temperature and humidity readings
- **Use for**: Identifying stress conditions and disease risk
- **Time period**: Last 7 days (adjustable)
- **Tip**: High humidity + high temp = increased disease risk

#### Soil Moisture Levels
- **Type**: Line chart
- **Shows**: Hourly soil moisture percentage
- **Use for**: Fine-tuning irrigation timing
- **Time period**: Last 7 days
- **Reference lines**:
  - 30%: Wilting point (irrigate immediately)
  - 70%: Field capacity (optimal)

#### Daily Environmental Summary
- **Type**: Bar chart
- **Shows**: Daily average temperature
- **Use for**: Spotting temperature trends
- **Time period**: Last 30 days

#### Cumulative Rainfall
- **Type**: Area chart
- **Shows**: Running total of rainfall
- **Use for**: Tracking water availability and irrigation needs
- **Time period**: Last 30 days

### Use Cases

1. **Irrigation Scheduling**: Use soil moisture to determine when to irrigate
2. **Pest and Disease Prediction**: High humidity + warm temps favor many pests
3. **Planting Decisions**: Use temperature trends to time planting
4. **Harvest Planning**: Use GDD to predict harvest readiness
5. **Frost Protection**: Monitor temperature lows during vulnerable periods

---

## Crop Performance Dashboard

### Purpose

Track plant growth, health, and development to optimize crop management and predict yields.

### Available KPIs

#### Days to Maturity (Actual vs Expected)
- **What it shows**: Difference between actual and expected days from planting to harvest
- **Units**: Days (+ or -)
- **Target**: 0 (on schedule)
- **Color codes**:
  - Green (On Time): -5 to +5 days
  - Yellow (Acceptable): -10 to +10 days
  - Orange (Delayed): > +10 days
  - Blue (Early): < -10 days
- **How to interpret**:
  - Positive: Crop taking longer than expected (may need investigation)
  - Negative: Crop ahead of schedule

#### Growth Rate
- **What it shows**: Average plant height increase per day
- **Units**: cm/day
- **Color codes**:
  - Green (Excellent): ≥ 0.5 cm/day
  - Light Green (Good): 0.3-0.5 cm/day
  - Orange (Slow): < 0.3 cm/day
- **How to interpret**: Slow growth may indicate nutrient deficiency or stress

#### Average Health Score
- **What it shows**: Mean plant health rating from observations (1-10 scale)
- **Units**: Score (1-10)
- **Target**: 8 or higher
- **Color codes**:
  - Green (Excellent): ≥ 8
  - Light Green (Good): 7-8
  - Yellow (Fair): 5-7
  - Red (Poor): < 5
- **How to interpret**: Declining scores require immediate investigation

#### Projected Yield Per Hectare
- **What it shows**: Estimated yield based on current growth and health
- **Units**: kg/ha
- **How to interpret**: Compare to variety's expected yield
- **Note**: Projection becomes more accurate as crop matures

### Available Charts

#### Growth Stages Timeline
- **Type**: Bar chart
- **Shows**: Progression through phenological stages
- **Use for**: Tracking crop development
- **Stages**: Germination → Vegetative → Flowering → Fruiting → Maturity
- **Tip**: Each stage has specific nutrient and water requirements

#### Plant Height Growth
- **Type**: Line chart with trend line
- **Shows**: Plant height over time
- **Use for**: Monitoring growth patterns
- **Time period**: Entire season
- **Tip**: Consistent upward trend indicates healthy growth

#### Health Score Timeline
- **Type**: Line chart
- **Shows**: Health score trends over time
- **Use for**: Early detection of problems
- **Time period**: Last 90 days
- **Tip**: Sudden drops require immediate investigation

### Use Cases

1. **Early Problem Detection**: Declining health scores alert you to issues
2. **Growth Stage Management**: Apply correct inputs for each stage
3. **Yield Forecasting**: Plan harvesting and marketing based on projections
4. **Performance Comparison**: Compare across plots to identify best practices

---

## Financial Dashboard

### Purpose

Track income and expenses to understand profitability, manage budgets, and make informed financial decisions.

### Available KPIs

#### Total Revenue (Season)
- **What it shows**: Total income from harvests this growing season
- **Units**: USD
- **How to interpret**: Compare to previous seasons and targets

#### Total Costs (Season)
- **What it shows**: Sum of all input costs (seeds, fertilizer, water, labor, etc.)
- **Units**: USD
- **How to interpret**: Track against budget to control spending

#### Profit Margin
- **What it shows**: Profit as a percentage of revenue
- **Units**: %
- **Target**: 30% or higher
- **Color codes**:
  - Green (Excellent): ≥ 40%
  - Light Green (Good): 25-40%
  - Yellow (Acceptable): 15-25%
  - Orange (Low): 0-15%
  - Red (Loss): < 0%
- **Formula**: (Revenue - Costs) / Revenue × 100
- **How to interpret**: Higher margins mean more efficient operations

#### ROI Per Plot
- **What it shows**: Return on investment by plot
- **Units**: %
- **Target**: 50% or higher
- **Color codes**:
  - Green (Excellent): ≥ 75%
  - Light Green (Good): 50-75%
  - Yellow (Acceptable): 25-50%
  - Orange (Low): 0-25%
  - Red (Loss): < 0%
- **Formula**: (Revenue - Costs) / Costs × 100

#### Cost Per Kilogram
- **What it shows**: Production cost per kg of yield
- **Units**: USD/kg
- **How to interpret**: Compare to market price to assess profitability

### Available Charts

#### Revenue vs Costs
- **Type**: Composed chart (bars + line)
- **Shows**: Monthly revenue, costs, and profit
- **Use for**: Tracking financial performance over time
- **Time period**: Last 12 months
- **Tip**: Seasonal patterns are normal in agriculture

#### Cost Breakdown
- **Type**: Pie chart
- **Shows**: Percentage of costs by category (seeds, fertilizer, water, labor, etc.)
- **Use for**: Identifying major cost drivers
- **Tip**: Largest categories offer greatest savings opportunities

#### Profit Margin Timeline
- **Type**: Line chart
- **Shows**: Profit margin percentage over time
- **Use for**: Monitoring profitability trends
- **Time period**: Last 12 months
- **Reference line**: 20% target margin

### Use Cases

1. **Budget Management**: Track spending against planned budget
2. **Cost Optimization**: Identify and reduce major expenses
3. **Profitability Analysis**: Understand which crops/plots are most profitable
4. **Investment Decisions**: Use ROI to prioritize resource allocation
5. **Pricing Decisions**: Ensure prices cover costs with adequate margin

---

## How to Use Dashboards

### Accessing Dashboards

1. Log in to FarmFactory
2. Click **Dashboards** in the main navigation menu
3. Select the dashboard you want to view:
   - Water Management
   - Nutrient Management
   - Environmental Monitoring
   - Crop Performance
   - Financial

### Dashboard Layout

Each dashboard has a consistent layout:

```
┌─────────────────────────────────────────────────┐
│  Dashboard Title                   [Date Filter] │
├─────────────┬─────────────┬─────────────────────┤
│   KPI Card  │  KPI Card   │    KPI Card         │
├─────────────┴─────────────┴─────────────────────┤
│                                                   │
│              Chart 1 (Large)                      │
│                                                   │
├───────────────────────┬───────────────────────────┤
│                       │                           │
│     Chart 2           │      Chart 3              │
│                       │                           │
└───────────────────────┴───────────────────────────┘
```

### Interacting with Charts

**Hover**: Move your mouse over data points to see detailed values

**Zoom**:
- Click and drag on a chart to zoom into a specific time range
- Double-click to reset zoom

**Toggle Data Series**:
- Click legend items to show/hide specific data series
- Useful for focusing on particular metrics

**Refresh**:
- Charts auto-refresh every 5 minutes
- Click the refresh icon to update immediately

---

## Understanding Charts

### Line Charts

**Best for**: Showing trends over time

**How to read**:
- X-axis: Time (dates/hours)
- Y-axis: Measured value
- Upward slope: Increasing trend
- Downward slope: Decreasing trend
- Flat line: Stable value

**Example**: Water usage over time shows if consumption is increasing or decreasing

### Bar Charts

**Best for**: Comparing values across categories or time periods

**How to read**:
- X-axis: Categories or time periods
- Y-axis: Measured value
- Taller bars: Higher values
- Compare heights to identify differences

**Example**: Irrigation frequency by week shows consistency of watering schedule

### Pie Charts

**Best for**: Showing proportions of a whole

**How to read**:
- Each slice: Percentage of total
- Larger slices: Greater proportion
- Colors: Different categories

**Example**: Cost breakdown shows which expense categories are largest

### Area Charts

**Best for**: Showing cumulative totals over time

**How to read**:
- X-axis: Time
- Y-axis: Cumulative value
- Filled area: Running total
- Steeper slope: Faster accumulation

**Example**: Cumulative rainfall shows total water received over a period

### Multi-line Charts

**Best for**: Comparing multiple metrics on the same timeline

**How to read**:
- X-axis: Time
- Y-axis: Measured values (may have 2 Y-axes for different units)
- Multiple lines: Different metrics
- Line intersections: Points where metrics are equal

**Example**: Temperature and humidity together help identify stress conditions

---

## Understanding KPIs

### What are KPIs?

Key Performance Indicators (KPIs) are metrics that help you measure success and make decisions. FarmFactory calculates these automatically from your data.

### KPI Color Coding

All KPIs use color codes to indicate performance:

- **Green**: Good/Optimal - everything is on track
- **Yellow/Orange**: Warning - attention may be needed
- **Red**: Critical - immediate action required
- **Blue**: Informational - neutral indicator

### How KPIs Are Calculated

Each KPI has a specific formula. For example:

**Water Use Efficiency**:
```
Water Use Efficiency = Total Water Used (liters) / Total Yield (kg)
```

**Profit Margin**:
```
Profit Margin = ((Revenue - Costs) / Revenue) × 100
```

See KPI definitions in the Technical Documentation for complete formulas.

### When KPIs Update

- **Real-time KPIs**: Environmental readings (updated every hour)
- **Daily KPIs**: Water usage, costs (updated nightly)
- **Weekly KPIs**: Nutrient efficiency, growth rate (updated every Sunday)
- **On-demand KPIs**: Financial metrics (updated when new data added)

---

## Filtering and Exporting Data

### Date Range Filtering

All dashboards support date range filtering:

1. Click the **Date Range** selector in the top right
2. Choose a preset range:
   - Last 24 hours
   - Last 7 days
   - Last 30 days
   - Last 90 days
   - Current season
   - Custom range
3. For custom range:
   - Select start date
   - Select end date
   - Click Apply

### Plot Filtering

If you manage multiple plots:

1. Click the **Plot** dropdown
2. Select specific plot(s) or "All Plots"
3. Charts and KPIs update automatically

### Exporting Data

#### Export Chart as Image

1. Hover over any chart
2. Click the camera icon (top right of chart)
3. Choose format: PNG or SVG
4. Image downloads automatically

#### Export Data as CSV

1. Click the **Export** button (top right of dashboard)
2. Choose what to export:
   - Current view only
   - All data in date range
3. Select format: CSV or Excel
4. File downloads automatically

**CSV file includes**:
- All raw data points shown in charts
- Calculated KPI values
- Date range and filters applied
- Timestamp of export

### Best Practices for Export

- **Regular backups**: Export data monthly for records
- **Reporting**: Export before season-end for reporting
- **Sharing**: Use PNG exports for presentations
- **Analysis**: Use CSV for detailed analysis in Excel

---

## Best Practices

### Data Collection

#### Irrigation Data
- **Log immediately**: Record irrigation events right after completion
- **Be accurate**: Measure actual volumes, don't estimate
- **Include notes**: Record any anomalies or special conditions
- **Check sensors**: Verify flow meters are calibrated

#### Nutrient Applications
- **Record before/after**: Enter planned applications, update with actuals
- **Track products**: Include product names and NPK ratios
- **Keep receipts**: Link costs to applications for accurate tracking
- **Note weather**: Rainfall after application affects uptake

#### Environmental Readings
- **Automate if possible**: Use connected sensors for continuous data
- **Manual readings**: Take at consistent times (e.g., 8am daily)
- **Calibrate regularly**: Check sensor accuracy monthly
- **Record extremes**: Note unusual weather events

#### Phenology Observations
- **Weekly minimum**: Observe at least once per week
- **Consistent timing**: Same day/time each week
- **Measure height**: Use fixed reference point
- **Photo documentation**: Take photos to track visual changes
- **Be objective**: Use standard scales for health scoring

#### Financial Data
- **Enter daily**: Don't wait - enter costs and revenues same day
- **Categorize correctly**: Use consistent categories
- **Include details**: More detail = better analysis
- **Save receipts**: Attach or file for reference

### Dashboard Usage

#### Daily Checks (5 minutes)
1. Check **Environmental Dashboard**: Monitor today's conditions
2. Review **Soil Moisture**: Decide on irrigation needs
3. Check **Alerts**: Respond to any threshold warnings

#### Weekly Reviews (15 minutes)
1. **Water Dashboard**: Review usage trends, adjust schedules
2. **Crop Performance**: Check growth rates and health scores
3. **Plan week ahead**: Schedule applications, activities

#### Monthly Analysis (30 minutes)
1. **Financial Dashboard**: Review expenses vs budget
2. **Nutrient Dashboard**: Analyze application patterns
3. **Compare plots**: Identify best and worst performers
4. **Export data**: Backup for records

#### Seasonal Planning (2 hours)
1. Review all dashboards for entire season
2. Calculate ROI per crop/plot
3. Identify improvements for next season
4. Export reports for stakeholders

---

## Troubleshooting

### Common Issues

#### "No Data Available"

**Possible causes**:
- No data entered for selected date range
- Plot filter excluding all data
- Data not yet processed

**Solutions**:
1. Check date range - expand if needed
2. Verify plot filter is correct
3. Confirm data has been entered
4. Wait 5 minutes and refresh (for recent entries)

#### Charts Not Displaying

**Possible causes**:
- Browser compatibility
- Slow internet connection
- JavaScript disabled

**Solutions**:
1. Refresh the page (Ctrl+R or Cmd+R)
2. Clear browser cache
3. Try different browser (Chrome, Firefox recommended)
4. Check internet connection
5. Ensure JavaScript is enabled

#### KPIs Showing "N/A"

**Possible causes**:
- Insufficient data for calculation
- Required data missing (e.g., no harvest data for yield calculation)

**Solutions**:
1. Check which data is needed for that KPI
2. Ensure all required data types are being collected
3. Wait until sufficient data accumulated (e.g., need 7 days for weekly average)

#### Wrong Values Displayed

**Possible causes**:
- Incorrect units entered
- Data entry errors
- Calculation errors

**Solutions**:
1. Review recent data entries for errors
2. Check units (e.g., liters vs cubic meters)
3. Edit incorrect entries
4. Contact support if calculations seem wrong

#### Slow Dashboard Loading

**Possible causes**:
- Large date range selected
- Many plots included
- Slow internet

**Solutions**:
1. Reduce date range (e.g., 30 days instead of 1 year)
2. Filter to fewer plots
3. Close other browser tabs
4. Upgrade internet connection

### Getting Help

#### In-App Help
- Click the **?** icon in any dashboard
- Access context-sensitive help for each chart/KPI

#### Documentation
- Visit docs.farmfactory.com
- Download PDF user guides
- Watch video tutorials

#### Support
- Email: support@farmfactory.com
- Phone: 1-800-FARM-HELP
- Chat: Click chat icon (bottom right)

#### Community
- Forum: community.farmfactory.com
- Share tips and best practices
- Learn from other farmers

---

## Appendix: Quick Reference

### KPI Quick Reference

| KPI | Target | Warning | Critical |
|-----|--------|---------|----------|
| Total Water Used (30d) | ≤50k L | 50-75k L | >75k L |
| Water Use Efficiency | ≤200 L/kg | 200-350 L/kg | >350 L/kg |
| Nutrient Use Efficiency | ≥15 kg/kg | 10-15 kg/kg | <10 kg/kg |
| Soil Moisture | 55-75% | 40-85% | <30% or >95% |
| Avg Temperature (7d) | 20-28°C | 15-32°C | <15°C or >32°C |
| Health Score | ≥8 | 5-7 | <5 |
| Profit Margin | ≥40% | 15-40% | <15% |
| ROI | ≥75% | 25-75% | <25% |

### Dashboard Access Quick Keys

- **Ctrl+D, W**: Water Management Dashboard
- **Ctrl+D, N**: Nutrient Management Dashboard
- **Ctrl+D, E**: Environmental Monitoring Dashboard
- **Ctrl+D, C**: Crop Performance Dashboard
- **Ctrl+D, F**: Financial Dashboard
- **Ctrl+E**: Export current view
- **Ctrl+R**: Refresh dashboard

### Chart Icon Legend

| Icon | Meaning |
|------|---------|
| 📊 | Bar chart |
| 📈 | Line chart |
| 🥧 | Pie chart |
| 📉 | Area chart |
| 📸 | Export as image |
| 💾 | Export as CSV |
| 🔄 | Refresh |
| ⚙️ | Settings |
| ℹ️ | Information |

---

**Questions?** Contact our support team at support@farmfactory.com or visit our community forum at community.farmfactory.com.

**Happy Farming! 🌱**

/**
 * Chart Examples Page
 * Demonstrates all chart components from the FarmFactory chart library
 *
 * This page serves as:
 * - A visual catalog of all available chart types
 * - Interactive examples with sample farm data
 * - Developer reference for implementation
 * - Testing ground for chart functionality
 */

import React, { useState } from 'react';
import {
  Container,
  Grid,
  Typography,
  Box,
  Paper,
  Divider,
  Alert,
  Chip,
  Stack,
} from '@mui/material';
import {
  LineChart,
  BarChart,
  PieChart,
  AreaChart,
  MultiLineChart,
  ComposedChart,
  ChartContainer,
  DateRangeSelector,
  getDateRange,
} from '../components/charts';
import type { DateRange, ChartSeries } from '../types/chart';

const ChartExamples: React.FC = () => {
  const [dateRange, setDateRange] = useState<DateRange>(() => {
    const range = getDateRange('30d');
    return { startDate: range.startDate, endDate: range.endDate };
  });

  // Sample data for different chart types

  // 1. Temperature trend data (LineChart)
  const temperatureData = [
    { date: 'Jan 1', temperature: 18.5 },
    { date: 'Jan 2', temperature: 19.2 },
    { date: 'Jan 3', temperature: 17.8 },
    { date: 'Jan 4', temperature: 20.1 },
    { date: 'Jan 5', temperature: 21.5 },
    { date: 'Jan 6', temperature: 22.3 },
    { date: 'Jan 7', temperature: 20.8 },
  ];

  // 2. Yield comparison data (BarChart)
  const yieldData = [
    { plot: 'Plot A', yield: 4500 },
    { plot: 'Plot B', yield: 5200 },
    { plot: 'Plot C', yield: 3800 },
    { plot: 'Plot D', yield: 4900 },
    { plot: 'Plot E', yield: 5500 },
  ];

  // 3. Soil type distribution (PieChart)
  const soilTypeData = [
    { type: 'Loamy', area: 35 },
    { type: 'Sandy', area: 25 },
    { type: 'Clay', area: 20 },
    { type: 'Silty', area: 15 },
    { type: 'Rocky', area: 5 },
  ];

  // 4. Cumulative water usage (AreaChart)
  const waterUsageData = [
    { date: 'Week 1', cumulative: 1200 },
    { date: 'Week 2', cumulative: 2500 },
    { date: 'Week 3', cumulative: 3900 },
    { date: 'Week 4', cumulative: 5100 },
    { date: 'Week 5', cumulative: 6400 },
    { date: 'Week 6', cumulative: 7500 },
  ];

  // 5. NPK levels over time (MultiLineChart)
  const npkData = [
    { date: 'Jan 1', nitrogen: 45, phosphorus: 30, potassium: 35 },
    { date: 'Jan 8', nitrogen: 42, phosphorus: 28, potassium: 33 },
    { date: 'Jan 15', nitrogen: 48, phosphorus: 32, potassium: 38 },
    { date: 'Jan 22', nitrogen: 50, phosphorus: 35, potassium: 40 },
    { date: 'Jan 29', nitrogen: 46, phosphorus: 31, potassium: 36 },
    { date: 'Feb 5', nitrogen: 44, phosphorus: 29, potassium: 34 },
  ];

  // 6. Revenue vs Target (ComposedChart)
  const revenueData = [
    { month: 'Jan', revenue: 45000, target: 50000, cost: 30000 },
    { month: 'Feb', revenue: 52000, target: 50000, cost: 32000 },
    { month: 'Mar', revenue: 48000, target: 55000, cost: 31000 },
    { month: 'Apr', revenue: 61000, target: 60000, cost: 35000 },
    { month: 'May', revenue: 58000, target: 60000, cost: 34000 },
    { month: 'Jun', revenue: 67000, target: 65000, cost: 38000 },
  ];

  const revenueSeries: ChartSeries[] = [
    { key: 'revenue', name: 'Revenue', color: '#2e7d32', type: 'bar' },
    { key: 'target', name: 'Target', color: '#1976d2', type: 'line' },
    { key: 'cost', name: 'Cost', color: '#ed6c02', type: 'area' },
  ];

  // Export handlers
  const handleExportPNG = (chartName: string) => {
    console.log(`Exporting ${chartName} as PNG`);
    alert(`PNG export for ${chartName} - In production, this would download the chart as an image`);
  };

  const handleExportCSV = (data: any[], chartName: string) => {
    console.log(`Exporting ${chartName} data as CSV`, data);
    alert(`CSV export for ${chartName} - In production, this would download the data as CSV`);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, color: 'primary.main' }}>
          Chart Component Library
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Interactive examples of all available chart components for FarmFactory data visualization
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          This page demonstrates all chart types with sample agricultural data.
          Use these components in your data visualization pages by importing from <code>@/components/charts</code>
        </Alert>

        {/* Technology Stack */}
        <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
          <Chip label="Recharts 2.10.3" color="primary" size="small" />
          <Chip label="Material-UI" color="secondary" size="small" />
          <Chip label="TypeScript" color="default" size="small" />
          <Chip label="Responsive Design" color="success" size="small" />
        </Stack>
      </Box>

      {/* Date Range Selector Example */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          Date Range Selector
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Interactive date range picker with quick select presets
        </Typography>
        <DateRangeSelector
          startDate={dateRange.startDate}
          endDate={dateRange.endDate}
          onChange={setDateRange}
        />
        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
          <Typography variant="caption" component="pre">
            {`Selected Range: ${dateRange.startDate?.toLocaleDateString() || 'Not selected'} - ${dateRange.endDate?.toLocaleDateString() || 'Not selected'}`}
          </Typography>
        </Box>
      </Paper>

      <Divider sx={{ my: 4 }} />

      {/* Chart Examples Grid */}
      <Grid container spacing={3}>
        {/* 1. LineChart Example */}
        <Grid item xs={12} lg={6}>
          <ChartContainer
            title="Daily Temperature Trends"
            loading={false}
            error={null}
            isEmpty={false}
            showExport={true}
            showRefresh={true}
            onExportPNG={() => handleExportPNG('Temperature Chart')}
            onExportCSV={() => handleExportCSV(temperatureData, 'Temperature Data')}
            onRefresh={() => console.log('Refreshing temperature data')}
          >
            <Box>
              <LineChart
                data={temperatureData}
                xKey="date"
                yKey="temperature"
                color="#2e7d32"
                showGrid={true}
                showLegend={true}
                showDots={true}
                height={300}
              />
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  <strong>LineChart:</strong> Time-series trends, temperature monitoring, growth tracking
                </Typography>
              </Box>
            </Box>
          </ChartContainer>
        </Grid>

        {/* 2. BarChart Example */}
        <Grid item xs={12} lg={6}>
          <ChartContainer
            title="Yield by Plot"
            loading={false}
            error={null}
            isEmpty={false}
            showExport={true}
            onExportPNG={() => handleExportPNG('Yield Chart')}
            onExportCSV={() => handleExportCSV(yieldData, 'Yield Data')}
          >
            <Box>
              <BarChart
                data={yieldData}
                xKey="plot"
                yKey="yield"
                color="#1976d2"
                horizontal={false}
                showValues={true}
                showGrid={true}
                height={300}
              />
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  <strong>BarChart:</strong> Comparisons, plot performance, categorical data
                </Typography>
              </Box>
            </Box>
          </ChartContainer>
        </Grid>

        {/* 3. PieChart Example */}
        <Grid item xs={12} lg={6}>
          <ChartContainer
            title="Soil Type Distribution"
            loading={false}
            error={null}
            isEmpty={false}
            showExport={true}
            onExportPNG={() => handleExportPNG('Soil Type Chart')}
            onExportCSV={() => handleExportCSV(soilTypeData, 'Soil Type Data')}
          >
            <Box>
              <PieChart
                data={soilTypeData}
                nameKey="type"
                valueKey="area"
                showPercentage={true}
                showLegend={true}
                innerRadius={0}
                height={350}
              />
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  <strong>PieChart:</strong> Proportions, distributions, cost breakdowns
                </Typography>
              </Box>
            </Box>
          </ChartContainer>
        </Grid>

        {/* 4. AreaChart Example */}
        <Grid item xs={12} lg={6}>
          <ChartContainer
            title="Cumulative Water Usage"
            loading={false}
            error={null}
            isEmpty={false}
            showExport={true}
            onExportPNG={() => handleExportPNG('Water Usage Chart')}
            onExportCSV={() => handleExportCSV(waterUsageData, 'Water Usage Data')}
          >
            <Box>
              <AreaChart
                data={waterUsageData}
                xKey="date"
                yKey="cumulative"
                color="#0288d1"
                stacked={false}
                fillOpacity={0.6}
                showGrid={true}
                height={300}
              />
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  <strong>AreaChart:</strong> Cumulative trends, stock levels, accumulated costs
                </Typography>
              </Box>
            </Box>
          </ChartContainer>
        </Grid>

        {/* 5. MultiLineChart Example */}
        <Grid item xs={12}>
          <ChartContainer
            title="NPK Nutrient Levels Over Time"
            loading={false}
            error={null}
            isEmpty={false}
            showExport={true}
            onExportPNG={() => handleExportPNG('NPK Chart')}
            onExportCSV={() => handleExportCSV(npkData, 'NPK Data')}
          >
            <Box>
              <MultiLineChart
                data={npkData}
                xKey="date"
                yKeys={['nitrogen', 'phosphorus', 'potassium']}
                seriesNames={['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)']}
                colors={['#2e7d32', '#1976d2', '#ed6c02']}
                toggleSeries={true}
                showGrid={true}
                showLegend={true}
                height={350}
              />
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  <strong>MultiLineChart:</strong> Multiple metrics comparison, NPK tracking, sensor data.
                  Click legend items to toggle series visibility.
                </Typography>
              </Box>
            </Box>
          </ChartContainer>
        </Grid>

        {/* 6. ComposedChart Example */}
        <Grid item xs={12}>
          <ChartContainer
            title="Revenue vs Target vs Cost"
            loading={false}
            error={null}
            isEmpty={false}
            showExport={true}
            onExportPNG={() => handleExportPNG('Revenue Chart')}
            onExportCSV={() => handleExportCSV(revenueData, 'Revenue Data')}
          >
            <Box>
              <ComposedChart
                data={revenueData}
                xKey="month"
                series={revenueSeries}
                showGrid={true}
                showLegend={true}
                height={350}
              />
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  <strong>ComposedChart:</strong> Mixed chart types (bars + lines + areas),
                  complex dashboards, actual vs target comparisons
                </Typography>
              </Box>
            </Box>
          </ChartContainer>
        </Grid>

        {/* Loading State Example */}
        <Grid item xs={12} md={6}>
          <ChartContainer
            title="Loading State Example"
            loading={true}
            error={null}
            isEmpty={false}
          >
            <div />
          </ChartContainer>
        </Grid>

        {/* Error State Example */}
        <Grid item xs={12} md={6}>
          <ChartContainer
            title="Error State Example"
            loading={false}
            error="Failed to load chart data. Please try again."
            isEmpty={false}
          >
            <div />
          </ChartContainer>
        </Grid>

        {/* Empty State Example */}
        <Grid item xs={12}>
          <ChartContainer
            title="Empty State Example"
            loading={false}
            error={null}
            isEmpty={true}
          >
            <div />
          </ChartContainer>
        </Grid>
      </Grid>

      {/* Code Examples Section */}
      <Divider sx={{ my: 4 }} />

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          Quick Start Code Examples
        </Typography>

        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
            1. Import Chart Components
          </Typography>
          <Paper sx={{ p: 2, bgcolor: 'grey.900', color: 'white', overflow: 'auto' }}>
            <Typography component="pre" variant="body2" sx={{ fontFamily: 'monospace', m: 0 }}>
{`import {
  LineChart,
  BarChart,
  PieChart,
  AreaChart,
  MultiLineChart,
  ComposedChart,
  ChartContainer,
  DateRangeSelector,
} from '@/components/charts';`}
            </Typography>
          </Paper>
        </Box>

        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
            2. Basic LineChart Usage
          </Typography>
          <Paper sx={{ p: 2, bgcolor: 'grey.900', color: 'white', overflow: 'auto' }}>
            <Typography component="pre" variant="body2" sx={{ fontFamily: 'monospace', m: 0 }}>
{`<ChartContainer
  title="Temperature Trends"
  loading={loading}
  error={error}
  isEmpty={data.length === 0}
  onExportPNG={() => exportToPNG('temperature')}
  onExportCSV={() => exportToCSV(data, 'temperature')}
>
  <LineChart
    data={temperatureData}
    xKey="date"
    yKey="temperature"
    color="#2e7d32"
    showGrid={true}
    showLegend={true}
    height={300}
  />
</ChartContainer>`}
            </Typography>
          </Paper>
        </Box>

        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
            3. MultiLineChart with Toggle
          </Typography>
          <Paper sx={{ p: 2, bgcolor: 'grey.900', color: 'white', overflow: 'auto' }}>
            <Typography component="pre" variant="body2" sx={{ fontFamily: 'monospace', m: 0 }}>
{`<MultiLineChart
  data={npkData}
  xKey="date"
  yKeys={['nitrogen', 'phosphorus', 'potassium']}
  seriesNames={['N', 'P', 'K']}
  colors={['#2e7d32', '#1976d2', '#ed6c02']}
  toggleSeries={true}
  height={350}
/>`}
            </Typography>
          </Paper>
        </Box>

        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
            4. Helper Functions
          </Typography>
          <Paper sx={{ p: 2, bgcolor: 'grey.900', color: 'white', overflow: 'auto' }}>
            <Typography component="pre" variant="body2" sx={{ fontFamily: 'monospace', m: 0 }}>
{`import {
  formatChartData,
  aggregateData,
  exportChartToPNG,
  exportChartToCSV,
  getDateRange,
} from '@/utils/chartHelpers';

// Format API data for charts
const chartData = formatChartData(apiData, 'date', 'value');

// Aggregate data by day/week/month
const aggregated = aggregateData(data, {
  period: 'day',
  method: 'avg',
  dateKey: 'date',
  valueKey: 'temperature'
});

// Get date ranges
const last30Days = getDateRange('30d');
const thisMonth = getDateRange('thisMonth');`}
            </Typography>
          </Paper>
        </Box>
      </Paper>

      {/* Feature Summary */}
      <Paper sx={{ p: 3, bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          Chart Library Features
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" gutterBottom>✓ 6 chart types (Line, Bar, Pie, Area, MultiLine, Composed)</Typography>
            <Typography variant="body2" gutterBottom>✓ Responsive design (mobile, tablet, desktop)</Typography>
            <Typography variant="body2" gutterBottom>✓ Loading, error, and empty states</Typography>
            <Typography variant="body2" gutterBottom>✓ Date range selector with presets</Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" gutterBottom>✓ Export to PNG and CSV</Typography>
            <Typography variant="body2" gutterBottom>✓ Agricultural green color theme</Typography>
            <Typography variant="body2" gutterBottom>✓ TypeScript type definitions</Typography>
            <Typography variant="body2" gutterBottom>✓ Tooltips, legends, and grid lines</Typography>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default ChartExamples;

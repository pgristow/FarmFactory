# FarmFactory Chart Component Library

Comprehensive, reusable chart component library built with Recharts for agricultural data visualization across all FarmFactory dashboard pages.

## Overview

This library provides 6 chart types, wrapper components, and utilities for creating beautiful, responsive, and accessible charts with an agricultural theme.

## Components

### 1. LineChart

**Purpose**: Time-series trends visualization

**Use Cases**:
- Temperature trends over time
- Growth tracking
- Any continuous time-series data

**Props**:
- `data: ChartData[]` - Array of data points
- `xKey: string` - Key for x-axis (usually date)
- `yKey: string` - Key for y-axis (metric value)
- `title?: string` - Chart title
- `color?: string` - Line color (default: #2e7d32)
- `showGrid?: boolean` - Show grid lines (default: true)
- `showLegend?: boolean` - Show legend (default: true)
- `showDots?: boolean` - Show data point dots (default: true)
- `strokeWidth?: number` - Line width (default: 2)
- `height?: number` - Chart height in pixels (default: 300)

**Example**:
```tsx
import { LineChart, ChartContainer } from '@/components/charts';

const temperatureData = [
  { date: '2024-01-01', temperature: 22.5 },
  { date: '2024-01-02', temperature: 23.1 },
  { date: '2024-01-03', temperature: 21.8 },
];

<ChartContainer title="Daily Temperature" period="30D">
  <LineChart
    data={temperatureData}
    xKey="date"
    yKey="temperature"
    color="#2e7d32"
  />
</ChartContainer>
```

---

### 2. BarChart

**Purpose**: Categorical comparisons

**Use Cases**:
- Compare yields across plots
- Compare monthly totals
- Any categorical comparison

**Props**:
- `data: ChartData[]` - Array of data points
- `xKey: string` - Key for x-axis (category)
- `yKey: string` - Key for y-axis (value)
- `title?: string` - Chart title
- `color?: string` - Bar color (default: #2e7d32)
- `horizontal?: boolean` - Horizontal orientation (default: false)
- `showValues?: boolean` - Show value labels (default: false)
- `showGrid?: boolean` - Show grid lines (default: true)
- `showLegend?: boolean` - Show legend (default: true)
- `height?: number` - Chart height (default: 300)

**Example**:
```tsx
import { BarChart, ChartContainer } from '@/components/charts';

const yieldData = [
  { plot: 'Plot A', yield: 450 },
  { plot: 'Plot B', yield: 520 },
  { plot: 'Plot C', yield: 380 },
];

<ChartContainer title="Yield by Plot">
  <BarChart
    data={yieldData}
    xKey="plot"
    yKey="yield"
    color="#2e7d32"
    showValues={true}
  />
</ChartContainer>
```

---

### 3. PieChart

**Purpose**: Proportional data visualization

**Use Cases**:
- Soil type distribution
- Cost breakdown by category
- Crop distribution

**Props**:
- `data: ChartData[]` - Array of data points
- `nameKey: string` - Key for category names
- `valueKey: string` - Key for values
- `title?: string` - Chart title
- `colors?: string[]` - Array of colors for segments
- `showPercentage?: boolean` - Show percentages (default: true)
- `showLegend?: boolean` - Show legend (default: true)
- `innerRadius?: number` - Inner radius for donut chart (default: 0)
- `height?: number` - Chart height (default: 300)

**Example**:
```tsx
import { PieChart, ChartContainer } from '@/components/charts';

const soilData = [
  { type: 'Clay', area: 35 },
  { type: 'Loam', area: 45 },
  { type: 'Sandy', area: 20 },
];

<ChartContainer title="Soil Type Distribution">
  <PieChart
    data={soilData}
    nameKey="type"
    valueKey="area"
    showPercentage={true}
  />
</ChartContainer>
```

---

### 4. AreaChart

**Purpose**: Cumulative data visualization

**Use Cases**:
- Cumulative water usage
- Accumulated costs
- Stock levels over time

**Props**:
- `data: ChartData[]` - Array of data points
- `xKey: string` - Key for x-axis
- `yKey: string` - Key for y-axis
- `title?: string` - Chart title
- `color?: string` - Area color (default: #2e7d32)
- `stacked?: boolean` - Stack multiple series (default: false)
- `fillOpacity?: number` - Fill opacity (default: 0.6)
- `showGrid?: boolean` - Show grid lines (default: true)
- `showLegend?: boolean` - Show legend (default: true)
- `height?: number` - Chart height (default: 300)

**Example**:
```tsx
import { AreaChart, ChartContainer } from '@/components/charts';

const waterData = [
  { date: '2024-01-01', cumulative: 1000 },
  { date: '2024-01-02', cumulative: 1250 },
  { date: '2024-01-03', cumulative: 1600 },
];

<ChartContainer title="Cumulative Water Usage">
  <AreaChart
    data={waterData}
    xKey="date"
    yKey="cumulative"
    color="#1976d2"
    fillOpacity={0.6}
  />
</ChartContainer>
```

---

### 5. MultiLineChart

**Purpose**: Multiple data series comparison

**Use Cases**:
- Compare multiple plots
- NPK levels over time (3 lines)
- Multiple sensor readings

**Props**:
- `data: ChartData[]` - Array of data points
- `xKey: string` - Key for x-axis
- `yKeys: string[]` - Array of keys for y-axis series
- `title?: string` - Chart title
- `colors?: string[]` - Array of colors for lines
- `seriesNames?: string[]` - Names for each series (defaults to yKeys)
- `toggleSeries?: boolean` - Allow toggling series visibility (default: true)
- `showGrid?: boolean` - Show grid lines (default: true)
- `showLegend?: boolean` - Show legend (default: true)
- `height?: number` - Chart height (default: 300)

**Example**:
```tsx
import { MultiLineChart, ChartContainer } from '@/components/charts';

const npkData = [
  { date: '2024-01-01', nitrogen: 45, phosphorus: 20, potassium: 35 },
  { date: '2024-01-02', nitrogen: 48, phosphorus: 22, potassium: 36 },
  { date: '2024-01-03', nitrogen: 46, phosphorus: 21, potassium: 38 },
];

<ChartContainer title="NPK Levels Over Time">
  <MultiLineChart
    data={npkData}
    xKey="date"
    yKeys={['nitrogen', 'phosphorus', 'potassium']}
    seriesNames={['N', 'P', 'K']}
    colors={['#2e7d32', '#1976d2', '#ed6c02']}
    toggleSeries={true}
  />
</ChartContainer>
```

---

### 6. ComposedChart

**Purpose**: Mixed chart types (bars, lines, areas)

**Use Cases**:
- Revenue (bars) with trend line
- Actual vs. target comparison
- Complex multi-metric dashboards

**Props**:
- `data: ChartData[]` - Array of data points
- `xKey: string` - Key for x-axis
- `series: ChartSeries[]` - Array of series configurations
- `title?: string` - Chart title
- `showGrid?: boolean` - Show grid lines (default: true)
- `showLegend?: boolean` - Show legend (default: true)
- `height?: number` - Chart height (default: 300)

**ChartSeries Interface**:
```tsx
interface ChartSeries {
  key: string;           // Data key
  name: string;          // Display name
  color: string;         // Color
  type?: 'line' | 'bar' | 'area';  // Chart type
  yAxisId?: string;      // 'left' or 'right'
}
```

**Example**:
```tsx
import { ComposedChart, ChartContainer } from '@/components/charts';

const revenueData = [
  { month: 'Jan', revenue: 4000, target: 4500 },
  { month: 'Feb', revenue: 4500, target: 4500 },
  { month: 'Mar', revenue: 5200, target: 5000 },
];

<ChartContainer title="Revenue vs Target">
  <ComposedChart
    data={revenueData}
    xKey="month"
    series={[
      { key: 'revenue', name: 'Revenue', color: '#2e7d32', type: 'bar' },
      { key: 'target', name: 'Target', color: '#1976d2', type: 'line' }
    ]}
  />
</ChartContainer>
```

---

### 7. ChartContainer

**Purpose**: Wrapper component for charts with common features

**Features**:
- Card/Paper wrapper
- Title header
- Loading state
- Error state
- Empty state ("No data available")
- Export buttons (PNG, CSV)
- Refresh button
- Time period selector

**Props**:
- `title: string` - Chart title (required)
- `children: React.ReactNode` - Chart component
- `loading?: boolean` - Show loading spinner
- `error?: string | null` - Error message
- `isEmpty?: boolean` - Show empty state
- `period?: TimePeriod` - Current time period ('7D' | '30D' | '90D' | 'Custom')
- `onPeriodChange?: (period: TimePeriod) => void` - Period change callback
- `onExportPNG?: () => void` - Export PNG callback
- `onExportCSV?: () => void` - Export CSV callback
- `onRefresh?: () => void` - Refresh callback
- `showExport?: boolean` - Show export buttons (default: true)
- `showRefresh?: boolean` - Show refresh button (default: true)
- `showPeriodSelector?: boolean` - Show period selector (default: false)

**Example**:
```tsx
import { LineChart, ChartContainer } from '@/components/charts';
import { useState } from 'react';

const [loading, setLoading] = useState(false);
const [period, setPeriod] = useState<TimePeriod>('30D');

<ChartContainer
  title="Temperature Trends"
  loading={loading}
  period={period}
  onPeriodChange={setPeriod}
  onRefresh={() => fetchData()}
  onExportPNG={() => exportChartToPNG(chartRef.current, 'temperature')}
  onExportCSV={() => exportChartToCSV(data, 'temperature-data')}
  showPeriodSelector={true}
>
  <LineChart data={data} xKey="date" yKey="temperature" />
</ChartContainer>
```

---

### 8. DateRangeSelector

**Purpose**: Date range picker with quick select buttons

**Features**:
- Material-UI date pickers
- Quick select buttons (Today, Last 7 days, etc.)
- Custom date range input
- onChange callback

**Props**:
- `startDate: Date | null` - Start date
- `endDate: Date | null` - End date
- `onChange: (range: DateRange) => void` - Change callback
- `quickSelectOptions?: QuickSelectOption[]` - Custom quick select options

**Example**:
```tsx
import { DateRangeSelector } from '@/components/charts';
import { useState } from 'react';

const [dateRange, setDateRange] = useState({ startDate: null, endDate: null });

<DateRangeSelector
  startDate={dateRange.startDate}
  endDate={dateRange.endDate}
  onChange={setDateRange}
/>
```

---

## Utility Functions

### Data Formatting

```tsx
import { formatChartData } from '@/components/charts';

// Transform API data for charts
const formatted = formatChartData(
  apiData,
  'timestamp',
  'value',
  'MMM dd'  // Date format
);
```

### Data Aggregation

```tsx
import { aggregateData } from '@/components/charts';

// Aggregate by day/week/month
const aggregated = aggregateData(data, {
  period: 'day',          // 'day' | 'week' | 'month'
  method: 'avg',          // 'sum' | 'avg' | 'min' | 'max' | 'count'
  dateKey: 'timestamp',
  valueKey: 'temperature'
});
```

### Export Functions

```tsx
import { exportChartToPNG, exportChartToCSV } from '@/components/charts';

// Export chart as PNG
const chartRef = useRef(null);
exportChartToPNG(chartRef.current, 'my-chart');

// Export data as CSV
exportChartToCSV(data, 'chart-data');
```

### Date Range Helpers

```tsx
import { getDateRange } from '@/components/charts';

// Get preset date ranges
const range = getDateRange('30d');  // Returns { startDate, endDate }
// Options: 'today', '7d', '30d', '90d', 'thisMonth', 'thisYear'
```

### Axis Formatting

```tsx
import { formatAxisLabel } from '@/components/charts';

// Format axis labels
const label = formatAxisLabel(value, {
  type: 'currency',     // 'date' | 'number' | 'currency' | 'percentage'
  decimals: 2,
  prefix: '$',
  suffix: ' USD'
});
```

---

## Design System

### Color Palette

```tsx
import { CHART_COLORS } from '@/components/charts';

CHART_COLORS.primary     // #2e7d32 (green)
CHART_COLORS.secondary   // #1976d2 (blue)
CHART_COLORS.warning     // #ed6c02 (orange)
CHART_COLORS.error       // #d32f2f (red)
CHART_COLORS.success     // #2e7d32 (green)
CHART_COLORS.info        // #0288d1 (light blue)
```

### Default Chart Settings

- **Grid**: Dashed lines, light gray (#e0e0e0)
- **Tooltips**: Always enabled, white background, shadow
- **Legend**: Show by default, 12px font
- **Animation**: 500ms ease
- **Responsive**: 100% width, min-height 300px
- **Font**: 12px for axes and legend

---

## TypeScript Types

All components are fully typed. Import types:

```tsx
import type {
  ChartData,
  ChartSeries,
  DateRange,
  TimePeriod,
  LineChartProps,
  BarChartProps,
  // ... etc
} from '@/components/charts';
```

---

## Responsive Design

All charts are responsive and work on:
- **Desktop**: Full features
- **Tablet**: Optimized layout
- **Mobile**: Simplified view, touch-friendly

Charts use `ResponsiveContainer` from Recharts to automatically adjust to container width.

---

## Accessibility

- **ARIA labels**: All interactive elements have labels
- **Keyboard navigation**: Support for Tab, Enter, Space
- **Screen readers**: Descriptive text for all charts
- **Color contrast**: WCAG AA compliant

---

## Performance

- **Lazy loading**: Components loaded on demand
- **Virtualization**: For large datasets (>1000 points)
- **Memoization**: Prevent unnecessary re-renders
- **Optimized**: <500ms render time for most charts

---

## Best Practices

### 1. Always Use ChartContainer

```tsx
// ✅ Good
<ChartContainer title="Temperature">
  <LineChart data={data} xKey="date" yKey="temp" />
</ChartContainer>

// ❌ Bad
<LineChart data={data} xKey="date" yKey="temp" />
```

### 2. Handle Loading and Error States

```tsx
<ChartContainer
  title="Temperature"
  loading={isLoading}
  error={error}
  isEmpty={data.length === 0}
>
  <LineChart data={data} xKey="date" yKey="temp" />
</ChartContainer>
```

### 3. Format Data Before Passing to Charts

```tsx
import { formatChartData } from '@/components/charts';

const formattedData = formatChartData(apiData, 'timestamp', 'value');
<LineChart data={formattedData} xKey="timestamp" yKey="value" />
```

### 4. Use Aggregation for Large Datasets

```tsx
import { aggregateData } from '@/components/charts';

// If you have hourly data for 90 days (2160 points), aggregate by day
const aggregated = aggregateData(data, {
  period: 'day',
  method: 'avg',
  dateKey: 'timestamp',
  valueKey: 'temperature'
});
```

### 5. Provide Meaningful Colors

```tsx
// Use semantic colors
<LineChart
  data={temperatureData}
  xKey="date"
  yKey="temp"
  color={CHART_COLORS.warning}  // Orange for temperature
/>
```

---

## File Structure

```
frontend/src/
├── components/
│   └── charts/
│       ├── LineChart.tsx
│       ├── BarChart.tsx
│       ├── PieChart.tsx
│       ├── AreaChart.tsx
│       ├── MultiLineChart.tsx
│       ├── ComposedChart.tsx
│       ├── ChartContainer.tsx
│       ├── DateRangeSelector.tsx
│       ├── index.ts
│       └── README.md (this file)
├── types/
│   └── chart.ts
└── utils/
    └── chartHelpers.ts
```

---

## Dependencies

- **recharts**: ^2.10.3 - Chart library
- **@mui/material**: ^5.15.0 - Material-UI components
- **@mui/icons-material**: ^5.15.0 - Material-UI icons
- **date-fns**: ^3.0.6 - Date utilities
- **react**: ^18.2.0
- **typescript**: ^5.3.3

---

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Contributing

When adding new chart types:

1. Create component in `/components/charts/`
2. Add TypeScript interface in `/types/chart.ts`
3. Export from `/components/charts/index.ts`
4. Update this README with usage examples
5. Add tests in `__tests__/` directory

---

## Support

For issues or questions:
- Check this README first
- Review component source code
- Check Recharts documentation: https://recharts.org/
- Contact frontend team

---

**Version**: 1.0.0
**Last Updated**: 2025-11-17
**Sprint**: Sprint 3 - Core Data Management
**Task**: FE-208

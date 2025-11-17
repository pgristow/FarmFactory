# Chart Library Quick Reference

**For Sprint 3 Data Visualization Pages**

---

## 🚀 Quick Start

### 1. Import Charts

```tsx
import {
  LineChart,
  BarChart,
  PieChart,
  AreaChart,
  MultiLineChart,
  ComposedChart,
  ChartContainer,
  DateRangeSelector,
} from '@/components/charts';
```

### 2. Import Helpers

```tsx
import {
  getChartColors,
  formatChartData,
  aggregateData,
  exportChartToPNG,
  exportChartToCSV,
  getDateRange,
} from '@/utils/chartHelpers';
```

---

## 📊 Chart Components Cheat Sheet

| Chart | Use For | Key Props |
|-------|---------|-----------|
| **LineChart** | Time-series trends | `xKey`, `yKey`, `color` |
| **BarChart** | Comparisons | `xKey`, `yKey`, `horizontal` |
| **PieChart** | Proportions | `nameKey`, `valueKey`, `colors[]` |
| **AreaChart** | Cumulative data | `xKey`, `yKey`, `fillOpacity` |
| **MultiLineChart** | Multiple metrics | `xKey`, `yKeys[]`, `colors[]` |
| **ComposedChart** | Mixed types | `xKey`, `series[]` |

---

## 🎨 Color Palette

```tsx
import { CHART_COLORS, getChartColors } from '@/utils/chartHelpers';

// Single color
color={CHART_COLORS.primary}    // '#2e7d32' - Green

// Multiple colors
colors={getChartColors(3)}       // ['#2e7d32', '#1976d2', '#ed6c02']
```

---

## 🔧 Common Patterns

### Basic Chart with Container

```tsx
<ChartContainer
  title="Temperature Trends"
  loading={loading}
  error={error}
  isEmpty={data.length === 0}
  onExportPNG={() => exportToPNG()}
  onExportCSV={() => exportToCSV()}
>
  <LineChart data={data} xKey="date" yKey="value" />
</ChartContainer>
```

### With Date Range Filter

```tsx
const [range, setRange] = useState(() => getDateRange('30d'));

<DateRangeSelector
  startDate={range.startDate}
  endDate={range.endDate}
  onChange={setRange}
/>
```

### Aggregate Large Datasets

```tsx
const dailyData = aggregateData(hourlyData, {
  period: 'day',
  method: 'avg',
  dateKey: 'timestamp',
  valueKey: 'temperature'
});
```

---

## 📖 Full Documentation

- **Complete Guide**: `/CHART_LIBRARY_IMPLEMENTATION.md`
- **Live Examples**: Visit `/chart-examples` in the app
- **TypeScript Types**: `/frontend/src/types/chart.ts`

---

**Happy Charting! 📊🌱**

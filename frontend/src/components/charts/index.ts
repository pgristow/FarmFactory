/**
 * Chart Component Library - Entry Point
 * Export all chart components for easy importing
 *
 * @example
 * ```tsx
 * import { LineChart, BarChart, ChartContainer } from '@/components/charts';
 * ```
 */

// Chart Components
export { default as LineChart } from './LineChart';
export { default as BarChart } from './BarChart';
export { default as PieChart } from './PieChart';
export { default as AreaChart } from './AreaChart';
export { default as MultiLineChart } from './MultiLineChart';
export { default as ComposedChart } from './ComposedChart';

// Container and Helper Components
export { default as ChartContainer } from './ChartContainer';
export { default as DateRangeSelector } from './DateRangeSelector';
export { default as ChartLegend, ChartLegendChip } from './ChartLegend';
export { default as ChartTooltip, SimpleTooltip, ComparisonTooltip } from './ChartTooltip';

// Re-export types
export type {
  ChartData,
  ChartSeries,
  DateRange,
  TimePeriod,
  AggregationType,
  LineChartProps,
  BarChartProps,
  PieChartProps,
  AreaChartProps,
  MultiLineChartProps,
  ComposedChartProps,
  ChartContainerProps,
  DateRangeSelectorProps,
} from '../../types/chart';

// Re-export utilities
export {
  CHART_COLORS,
  getChartColors,
  formatChartData,
  aggregateData,
  formatAxisLabel,
  exportChartToPNG,
  exportChartToCSV,
  getDateRange,
  calculatePercentage,
} from '../../utils/chartHelpers';

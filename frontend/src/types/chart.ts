/**
 * Chart Component Library Types
 * TypeScript interfaces for all chart components
 */

export interface ChartData {
  [key: string]: string | number | Date;
}

export interface ChartSeries {
  key: string;
  name: string;
  color: string;
  type?: 'line' | 'bar' | 'area';
  yAxisId?: string;
}

export interface DateRange {
  startDate: Date | null;
  endDate: Date | null;
}

export type TimePeriod = '7D' | '30D' | '90D' | 'Custom';

export type AggregationType = 'day' | 'week' | 'month';

// Base props for all chart components
export interface BaseChartProps {
  data: ChartData[];
  title?: string;
  showGrid?: boolean;
  showLegend?: boolean;
  height?: number;
  loading?: boolean;
  error?: string | null;
}

// LineChart specific props
export interface LineChartProps extends BaseChartProps {
  xKey: string;
  yKey: string;
  color?: string;
  showDots?: boolean;
  strokeWidth?: number;
}

// BarChart specific props
export interface BarChartProps extends BaseChartProps {
  xKey: string;
  yKey: string;
  color?: string;
  horizontal?: boolean;
  showValues?: boolean;
}

// PieChart specific props
export interface PieChartProps extends Omit<BaseChartProps, 'showGrid'> {
  nameKey: string;
  valueKey: string;
  colors?: string[];
  showPercentage?: boolean;
  innerRadius?: number;
}

// AreaChart specific props
export interface AreaChartProps extends BaseChartProps {
  xKey: string;
  yKey: string;
  color?: string;
  stacked?: boolean;
  fillOpacity?: number;
}

// MultiLineChart specific props
export interface MultiLineChartProps extends BaseChartProps {
  xKey: string;
  yKeys: string[];
  colors?: string[];
  seriesNames?: string[];
  toggleSeries?: boolean;
}

// ComposedChart specific props
export interface ComposedChartProps extends BaseChartProps {
  xKey: string;
  series: ChartSeries[];
}

// ChartContainer props
export interface ChartContainerProps {
  title: string;
  children: React.ReactNode;
  loading?: boolean;
  error?: string | null;
  isEmpty?: boolean;
  period?: TimePeriod;
  onPeriodChange?: (period: TimePeriod) => void;
  onExportPNG?: () => void;
  onExportCSV?: () => void;
  onRefresh?: () => void;
  showExport?: boolean;
  showRefresh?: boolean;
  showPeriodSelector?: boolean;
}

// DateRangeSelector props
export interface DateRangeSelectorProps {
  startDate: Date | null;
  endDate: Date | null;
  onChange: (range: DateRange) => void;
  quickSelectOptions?: QuickSelectOption[];
}

export interface QuickSelectOption {
  label: string;
  value: string;
  getRange: () => DateRange;
}

// Chart export options
export interface ExportOptions {
  filename: string;
  format: 'png' | 'csv';
  width?: number;
  height?: number;
}

// Chart color configuration
export interface ChartColorConfig {
  primary: string;
  secondary: string;
  warning: string;
  error: string;
  success: string;
  info: string;
  gradient: {
    start: string;
    end: string;
  };
}

// Axis formatting options
export interface AxisFormatterOptions {
  type: 'date' | 'number' | 'currency' | 'percentage';
  format?: string;
  decimals?: number;
  prefix?: string;
  suffix?: string;
}

// Data aggregation options
export interface AggregationOptions {
  period: AggregationType;
  method: 'sum' | 'avg' | 'min' | 'max' | 'count';
  dateKey: string;
  valueKey: string;
}

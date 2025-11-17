/**
 * Chart Helper Utilities
 * Functions for chart data transformation, formatting, and export
 */

import { format, parseISO, startOfDay, endOfDay, subDays, startOfMonth, endOfMonth, startOfYear } from 'date-fns';
import type { ChartData, AggregationOptions, AxisFormatterOptions, ChartColorConfig } from '../types/chart';

/**
 * Agricultural Color Palette
 */
export const CHART_COLORS: ChartColorConfig = {
  primary: '#2e7d32',      // Green
  secondary: '#1976d2',    // Blue
  warning: '#ed6c02',      // Orange
  error: '#d32f2f',        // Red
  success: '#2e7d32',      // Green
  info: '#0288d1',         // Light Blue
  gradient: {
    start: '#2e7d32',
    end: '#81c784',
  },
};

/**
 * Get color palette for multiple series
 */
export const getChartColors = (count: number = 1): string[] => {
  const baseColors = [
    CHART_COLORS.primary,
    CHART_COLORS.secondary,
    CHART_COLORS.warning,
    CHART_COLORS.info,
    '#9c27b0',  // Purple
    '#e91e63',  // Pink
    '#00bcd4',  // Cyan
    '#4caf50',  // Light Green
    '#ff9800',  // Orange
    '#795548',  // Brown
  ];

  if (count <= baseColors.length) {
    return baseColors.slice(0, count);
  }

  // Generate additional colors if needed
  const colors = [...baseColors];
  while (colors.length < count) {
    const hue = (colors.length * 137.5) % 360;
    colors.push(`hsl(${hue}, 70%, 50%)`);
  }

  return colors;
};

/**
 * Format chart data from API response
 */
export const formatChartData = (
  data: any[],
  xKey: string,
  yKey: string | string[],
  dateFormat?: string
): ChartData[] => {
  if (!data || data.length === 0) return [];

  return data.map((item) => {
    const formattedItem: ChartData = {};

    // Format x-axis (date or string)
    if (item[xKey] instanceof Date || typeof item[xKey] === 'string') {
      try {
        const date = typeof item[xKey] === 'string' ? parseISO(item[xKey]) : item[xKey];
        formattedItem[xKey] = dateFormat ? format(date, dateFormat) : item[xKey];
      } catch {
        formattedItem[xKey] = item[xKey];
      }
    } else {
      formattedItem[xKey] = item[xKey];
    }

    // Format y-axis (single or multiple)
    if (Array.isArray(yKey)) {
      yKey.forEach((key) => {
        formattedItem[key] = parseFloat(item[key]) || 0;
      });
    } else {
      formattedItem[yKey] = parseFloat(item[yKey]) || 0;
    }

    return formattedItem;
  });
};

/**
 * Aggregate data by time period
 */
export const aggregateData = (
  data: ChartData[],
  options: AggregationOptions
): ChartData[] => {
  const { period, method, dateKey, valueKey } = options;

  if (!data || data.length === 0) return [];

  // Group data by period
  const grouped = new Map<string, number[]>();

  data.forEach((item) => {
    try {
      const date = typeof item[dateKey] === 'string'
        ? parseISO(item[dateKey] as string)
        : item[dateKey] as Date;

      let periodKey: string;
      switch (period) {
        case 'day':
          periodKey = format(date, 'yyyy-MM-dd');
          break;
        case 'week':
          periodKey = format(date, 'yyyy-ww');
          break;
        case 'month':
          periodKey = format(date, 'yyyy-MM');
          break;
        default:
          periodKey = format(date, 'yyyy-MM-dd');
      }

      const value = parseFloat(String(item[valueKey])) || 0;

      if (!grouped.has(periodKey)) {
        grouped.set(periodKey, []);
      }
      grouped.get(periodKey)!.push(value);
    } catch (error) {
      console.warn('Error aggregating data point:', item, error);
    }
  });

  // Apply aggregation method
  const aggregated: ChartData[] = [];
  grouped.forEach((values, periodKey) => {
    let aggregatedValue: number;

    switch (method) {
      case 'sum':
        aggregatedValue = values.reduce((sum, val) => sum + val, 0);
        break;
      case 'avg':
        aggregatedValue = values.reduce((sum, val) => sum + val, 0) / values.length;
        break;
      case 'min':
        aggregatedValue = Math.min(...values);
        break;
      case 'max':
        aggregatedValue = Math.max(...values);
        break;
      case 'count':
        aggregatedValue = values.length;
        break;
      default:
        aggregatedValue = values.reduce((sum, val) => sum + val, 0);
    }

    aggregated.push({
      [dateKey]: periodKey,
      [valueKey]: aggregatedValue,
    });
  });

  return aggregated.sort((a, b) =>
    String(a[dateKey]).localeCompare(String(b[dateKey]))
  );
};

/**
 * Format axis labels
 */
export const formatAxisLabel = (
  value: any,
  options: AxisFormatterOptions
): string => {
  const { type, format: formatStr, decimals = 0, prefix = '', suffix = '' } = options;

  try {
    switch (type) {
      case 'date':
        if (typeof value === 'string') {
          const date = parseISO(value);
          return format(date, formatStr || 'MMM dd');
        }
        return value instanceof Date ? format(value, formatStr || 'MMM dd') : String(value);

      case 'number':
        const num = parseFloat(value);
        return `${prefix}${num.toFixed(decimals)}${suffix}`;

      case 'currency':
        const currency = parseFloat(value);
        return `${prefix}$${currency.toFixed(decimals || 2)}${suffix}`;

      case 'percentage':
        const percent = parseFloat(value);
        return `${prefix}${percent.toFixed(decimals)}%${suffix}`;

      default:
        return String(value);
    }
  } catch {
    return String(value);
  }
};

/**
 * Export chart as PNG
 */
export const exportChartToPNG = (
  chartRef: HTMLElement | null,
  filename: string = 'chart'
): void => {
  if (!chartRef) {
    console.error('Chart reference not found');
    return;
  }

  try {
    // Use html2canvas or similar library in production
    // For now, we'll use a simple approach
    import('html2canvas').then((html2canvas) => {
      html2canvas.default(chartRef, {
        backgroundColor: '#ffffff',
        scale: 2,
      }).then((canvas) => {
        const link = document.createElement('a');
        link.download = `${filename}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
      });
    }).catch(() => {
      // Fallback if html2canvas is not available
      console.warn('html2canvas not available. PNG export requires html2canvas library.');
      alert('PNG export requires html2canvas library. Please install: npm install html2canvas');
    });
  } catch (error) {
    console.error('Error exporting chart to PNG:', error);
  }
};

/**
 * Export chart data as CSV
 */
export const exportChartToCSV = (
  data: ChartData[],
  filename: string = 'chart-data'
): void => {
  if (!data || data.length === 0) {
    console.warn('No data to export');
    return;
  }

  try {
    // Get all unique keys from data
    const keys = Array.from(
      new Set(data.flatMap((item) => Object.keys(item)))
    );

    // Create CSV header
    const header = keys.join(',');

    // Create CSV rows
    const rows = data.map((item) =>
      keys.map((key) => {
        const value = item[key];
        // Escape commas and quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value ?? '';
      }).join(',')
    );

    // Combine header and rows
    const csv = [header, ...rows].join('\n');

    // Create blob and download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Error exporting chart to CSV:', error);
  }
};

/**
 * Get date range for quick select options
 */
export const getDateRange = (option: string): { startDate: Date; endDate: Date } => {
  const now = new Date();
  const end = endOfDay(now);

  switch (option) {
    case 'today':
      return { startDate: startOfDay(now), endDate: end };

    case '7d':
      return { startDate: startOfDay(subDays(now, 6)), endDate: end };

    case '30d':
      return { startDate: startOfDay(subDays(now, 29)), endDate: end };

    case '90d':
      return { startDate: startOfDay(subDays(now, 89)), endDate: end };

    case 'thisMonth':
      return { startDate: startOfMonth(now), endDate: end };

    case 'thisYear':
      return { startDate: startOfYear(now), endDate: end };

    default:
      return { startDate: startOfDay(subDays(now, 29)), endDate: end };
  }
};

/**
 * Calculate percentage for pie chart labels
 */
export const calculatePercentage = (value: number, total: number): string => {
  if (total === 0) return '0%';
  const percentage = (value / total) * 100;
  return `${percentage.toFixed(1)}%`;
};

/**
 * Generate gradient definition for area charts
 */
export const generateGradientId = (baseId: string): string => {
  return `gradient-${baseId}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Validate chart data
 */
export const validateChartData = (data: ChartData[]): boolean => {
  if (!Array.isArray(data)) {
    console.warn('Chart data must be an array');
    return false;
  }

  if (data.length === 0) {
    console.warn('Chart data is empty');
    return false;
  }

  return true;
};

/**
 * Format tooltip value
 */
export const formatTooltipValue = (
  value: number,
  name: string,
  type: 'number' | 'currency' | 'percentage' = 'number'
): string => {
  switch (type) {
    case 'currency':
      return `$${value.toFixed(2)}`;
    case 'percentage':
      return `${value.toFixed(1)}%`;
    default:
      return value.toFixed(2);
  }
};

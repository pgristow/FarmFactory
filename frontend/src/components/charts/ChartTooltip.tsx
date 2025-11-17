/**
 * ChartTooltip Component
 * Reusable custom tooltip for charts
 *
 * Features:
 * - Consistent styling across all charts
 * - Multiple data points support
 * - Value formatting (currency, percentage, number)
 * - Icon indicators
 * - Responsive design
 *
 * Use Cases:
 * - Standardized tooltip appearance
 * - Complex multi-metric tooltips
 * - Formatted value display
 *
 * @example
 * ```tsx
 * const CustomTooltip = ({ active, payload }: any) => {
 *   if (active && payload && payload.length) {
 *     return (
 *       <ChartTooltip
 *         title={payload[0].payload.date}
 *         items={payload.map((p: any) => ({
 *           label: p.name,
 *           value: p.value,
 *           color: p.color,
 *           format: 'number'
 *         }))}
 *       />
 *     );
 *   }
 *   return null;
 * };
 * ```
 */

import React from 'react';
import { Box, Paper, Typography, Divider, Stack } from '@mui/material';
import { Circle as CircleIcon } from '@mui/icons-material';

export type TooltipValueFormat = 'number' | 'currency' | 'percentage' | 'custom';

export interface TooltipItem {
  label: string;
  value: number | string;
  color?: string;
  format?: TooltipValueFormat;
  unit?: string;
  decimals?: number;
  prefix?: string;
  suffix?: string;
}

export interface ChartTooltipProps {
  title?: string;
  subtitle?: string;
  items: TooltipItem[];
  showIcons?: boolean;
  maxWidth?: number;
  backgroundColor?: string;
  borderColor?: string;
  textColor?: string;
}

const ChartTooltip: React.FC<ChartTooltipProps> = ({
  title,
  subtitle,
  items,
  showIcons = true,
  maxWidth = 250,
  backgroundColor = '#ffffff',
  borderColor = '#e0e0e0',
  textColor = '#333333',
}) => {
  /**
   * Format value based on specified format type
   */
  const formatValue = (item: TooltipItem): string => {
    const { value, format = 'number', decimals = 2, prefix = '', suffix = '', unit = '' } = item;

    if (typeof value === 'string') {
      return `${prefix}${value}${suffix}${unit}`;
    }

    const numValue = typeof value === 'number' ? value : parseFloat(value);

    if (isNaN(numValue)) {
      return 'N/A';
    }

    let formatted: string;

    switch (format) {
      case 'currency':
        formatted = `$${numValue.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        break;

      case 'percentage':
        formatted = `${numValue.toFixed(decimals)}%`;
        break;

      case 'number':
        if (numValue >= 1000000) {
          formatted = `${(numValue / 1000000).toFixed(1)}M`;
        } else if (numValue >= 1000) {
          formatted = `${(numValue / 1000).toFixed(1)}K`;
        } else {
          formatted = numValue.toFixed(decimals);
        }
        break;

      case 'custom':
      default:
        formatted = numValue.toFixed(decimals);
    }

    return `${prefix}${formatted}${suffix}${unit}`;
  };

  if (items.length === 0) {
    return null;
  }

  return (
    <Paper
      elevation={3}
      sx={{
        p: 1.5,
        maxWidth,
        backgroundColor,
        border: `1px solid ${borderColor}`,
        borderRadius: 1,
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      }}
    >
      {/* Title */}
      {title && (
        <Typography
          variant="body2"
          sx={{
            fontWeight: 600,
            color: textColor,
            mb: subtitle || items.length > 0 ? 0.5 : 0,
            fontSize: '0.875rem',
          }}
        >
          {title}
        </Typography>
      )}

      {/* Subtitle */}
      {subtitle && (
        <Typography
          variant="caption"
          sx={{
            color: 'text.secondary',
            display: 'block',
            mb: items.length > 0 ? 1 : 0,
            fontSize: '0.75rem',
          }}
        >
          {subtitle}
        </Typography>
      )}

      {/* Divider after title */}
      {(title || subtitle) && items.length > 0 && (
        <Divider sx={{ mb: 1 }} />
      )}

      {/* Data Items */}
      <Stack spacing={0.5}>
        {items.map((item, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 1,
            }}
          >
            {/* Label with optional icon */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flex: 1 }}>
              {showIcons && item.color && (
                <CircleIcon
                  sx={{
                    fontSize: 10,
                    color: item.color,
                  }}
                />
              )}
              <Typography
                variant="body2"
                sx={{
                  color: item.color || textColor,
                  fontSize: '0.8125rem',
                  fontWeight: 500,
                }}
              >
                {item.label}
              </Typography>
            </Box>

            {/* Formatted Value */}
            <Typography
              variant="body2"
              sx={{
                fontWeight: 600,
                color: textColor,
                fontSize: '0.8125rem',
                textAlign: 'right',
              }}
            >
              {formatValue(item)}
            </Typography>
          </Box>
        ))}
      </Stack>
    </Paper>
  );
};

/**
 * SimpleTooltip - Minimal single-value tooltip
 * For simple charts with one data point
 */
export interface SimpleTooltipProps {
  label: string;
  value: number | string;
  color?: string;
  format?: TooltipValueFormat;
  unit?: string;
}

export const SimpleTooltip: React.FC<SimpleTooltipProps> = ({
  label,
  value,
  color = '#2e7d32',
  format = 'number',
  unit = '',
}) => {
  return (
    <ChartTooltip
      items={[
        {
          label,
          value,
          color,
          format,
          unit,
        },
      ]}
      showIcons={false}
    />
  );
};

/**
 * ComparisonTooltip - Tooltip for comparing multiple values
 * Shows differences and percentages
 */
export interface ComparisonTooltipProps {
  title: string;
  actual: number;
  target: number;
  actualLabel?: string;
  targetLabel?: string;
  format?: TooltipValueFormat;
}

export const ComparisonTooltip: React.FC<ComparisonTooltipProps> = ({
  title,
  actual,
  target,
  actualLabel = 'Actual',
  targetLabel = 'Target',
  format = 'number',
}) => {
  const difference = actual - target;
  const percentDiff = target !== 0 ? ((difference / target) * 100) : 0;
  const isPositive = difference >= 0;

  return (
    <ChartTooltip
      title={title}
      items={[
        {
          label: actualLabel,
          value: actual,
          color: '#2e7d32',
          format,
        },
        {
          label: targetLabel,
          value: target,
          color: '#1976d2',
          format,
        },
        {
          label: 'Difference',
          value: difference,
          color: isPositive ? '#4caf50' : '#f44336',
          format,
          prefix: isPositive ? '+' : '',
        },
        {
          label: 'vs Target',
          value: percentDiff,
          color: isPositive ? '#4caf50' : '#f44336',
          format: 'percentage',
          prefix: isPositive ? '+' : '',
        },
      ]}
    />
  );
};

export default ChartTooltip;

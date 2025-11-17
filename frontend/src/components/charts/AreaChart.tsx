/**
 * AreaChart Component
 * Cumulative data visualization with filled areas
 *
 * Features:
 * - Gradient fill
 * - Stacked option for multiple series
 * - Responsive design
 * - Tooltips
 * - Customizable colors
 * - Grid lines
 *
 * Use Cases:
 * - Cumulative water usage
 * - Accumulated costs over time
 * - Stock levels
 *
 * @example
 * ```tsx
 * <AreaChart
 *   data={waterUsageData}
 *   xKey="date"
 *   yKey="cumulativeVolume"
 *   title="Cumulative Water Usage"
 *   color="#2e7d32"
 *   stacked={false}
 *   fillOpacity={0.6}
 * />
 * ```
 */

import React, { useMemo } from 'react';
import {
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { CHART_COLORS, generateGradientId } from '../../utils/chartHelpers';
import type { AreaChartProps } from '../../types/chart';

const AreaChart: React.FC<AreaChartProps> = ({
  data,
  xKey,
  yKey,
  title,
  color = CHART_COLORS.primary,
  stacked = false,
  fillOpacity = 0.6,
  showGrid = true,
  showLegend = true,
  height = 300,
}) => {
  // Generate unique gradient ID
  const gradientId = useMemo(() => generateGradientId(yKey), [yKey]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div
          style={{
            backgroundColor: 'white',
            padding: '10px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}
        >
          <p style={{ margin: 0, fontWeight: 600 }}>
            {payload[0].payload[xKey]}
          </p>
          <p style={{ margin: '4px 0 0 0', color }}>
            {`${yKey}: ${payload[0].value.toFixed(2)}`}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsAreaChart
        data={data}
        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
      >
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={fillOpacity} />
            <stop offset="95%" stopColor={color} stopOpacity={0.1} />
          </linearGradient>
        </defs>
        {showGrid && (
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#e0e0e0"
            vertical={false}
          />
        )}
        <XAxis
          dataKey={xKey}
          stroke="#666"
          style={{ fontSize: '12px' }}
          tick={{ fill: '#666' }}
        />
        <YAxis
          stroke="#666"
          style={{ fontSize: '12px' }}
          tick={{ fill: '#666' }}
        />
        <Tooltip content={<CustomTooltip />} />
        {showLegend && (
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            iconType="rect"
          />
        )}
        <Area
          type="monotone"
          dataKey={yKey}
          stroke={color}
          strokeWidth={2}
          fill={`url(#${gradientId})`}
          fillOpacity={1}
          animationDuration={500}
          animationEasing="ease"
          stackId={stacked ? '1' : undefined}
        />
      </RechartsAreaChart>
    </ResponsiveContainer>
  );
};

export default AreaChart;

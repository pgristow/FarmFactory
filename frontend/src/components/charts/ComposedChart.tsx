/**
 * ComposedChart Component
 * Mixed chart types (bars, lines, areas) in one visualization
 *
 * Features:
 * - Combine multiple chart types
 * - Multiple series configurations
 * - Dual Y-axes support
 * - Responsive design
 * - Tooltips
 * - Legend
 *
 * Use Cases:
 * - Revenue (bars) with trend line
 * - Actual vs. target (bars vs. line)
 * - Complex multi-metric dashboards
 *
 * @example
 * ```tsx
 * <ComposedChart
 *   data={revenueData}
 *   xKey="month"
 *   series={[
 *     { key: 'revenue', name: 'Revenue', color: '#2e7d32', type: 'bar' },
 *     { key: 'target', name: 'Target', color: '#1976d2', type: 'line' }
 *   ]}
 *   title="Revenue vs Target"
 * />
 * ```
 */

import React from 'react';
import {
  ComposedChart as RechartsComposedChart,
  Line,
  Bar,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { ComposedChartProps } from '../../types/chart';

const ComposedChart: React.FC<ComposedChartProps> = ({
  data,
  xKey,
  series,
  title,
  showGrid = true,
  showLegend = true,
  height = 300,
}) => {
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
          <p style={{ margin: 0, fontWeight: 600, marginBottom: '4px' }}>
            {payload[0].payload[xKey]}
          </p>
          {payload.map((entry: any, index: number) => (
            <p
              key={index}
              style={{
                margin: '2px 0',
                color: entry.color,
                fontSize: '12px',
              }}
            >
              {`${entry.name}: ${entry.value.toFixed(2)}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Render appropriate chart component based on type
  const renderSeries = (seriesConfig: typeof series[0]) => {
    const { key, name, color, type = 'line', yAxisId = 'left' } = seriesConfig;

    switch (type) {
      case 'bar':
        return (
          <Bar
            key={key}
            dataKey={key}
            name={name}
            fill={color}
            yAxisId={yAxisId}
            radius={[4, 4, 0, 0]}
            animationDuration={500}
          />
        );

      case 'area':
        return (
          <Area
            key={key}
            type="monotone"
            dataKey={key}
            name={name}
            fill={color}
            stroke={color}
            yAxisId={yAxisId}
            fillOpacity={0.6}
            animationDuration={500}
          />
        );

      case 'line':
      default:
        return (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            name={name}
            stroke={color}
            strokeWidth={2}
            yAxisId={yAxisId}
            dot={{ fill: color, r: 4 }}
            activeDot={{ r: 6 }}
            animationDuration={500}
          />
        );
    }
  };

  // Check if we need dual Y-axes
  const hasRightAxis = series.some((s) => s.yAxisId === 'right');

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsComposedChart
        data={data}
        margin={{ top: 5, right: hasRightAxis ? 30 : 20, left: 20, bottom: 5 }}
      >
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
          yAxisId="left"
          stroke="#666"
          style={{ fontSize: '12px' }}
          tick={{ fill: '#666' }}
        />
        {hasRightAxis && (
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#666"
            style={{ fontSize: '12px' }}
            tick={{ fill: '#666' }}
          />
        )}
        <Tooltip content={<CustomTooltip />} />
        {showLegend && (
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            iconType="line"
          />
        )}
        {series.map((seriesConfig) => renderSeries(seriesConfig))}
      </RechartsComposedChart>
    </ResponsiveContainer>
  );
};

export default ComposedChart;

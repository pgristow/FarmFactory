/**
 * LineChart Component
 * Time-series trends visualization
 *
 * Features:
 * - Responsive design
 * - Date formatting
 * - Tooltips
 * - Customizable colors
 * - Grid lines
 * - Legend
 *
 * Use Cases:
 * - Temperature trends over time
 * - Growth tracking
 * - Any time-series data
 *
 * @example
 * ```tsx
 * <LineChart
 *   data={temperatureData}
 *   xKey="date"
 *   yKey="temperature"
 *   title="Daily Temperature"
 *   color="#2e7d32"
 *   showGrid={true}
 *   showLegend={true}
 * />
 * ```
 */

import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { CHART_COLORS } from '../../utils/chartHelpers';
import type { LineChartProps } from '../../types/chart';

const LineChart: React.FC<LineChartProps> = ({
  data,
  xKey,
  yKey,
  title,
  color = CHART_COLORS.primary,
  showGrid = true,
  showLegend = true,
  showDots = true,
  strokeWidth = 2,
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
      <RechartsLineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
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
          stroke="#666"
          style={{ fontSize: '12px' }}
          tick={{ fill: '#666' }}
        />
        <Tooltip content={<CustomTooltip />} />
        {showLegend && (
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            iconType="line"
          />
        )}
        <Line
          type="monotone"
          dataKey={yKey}
          stroke={color}
          strokeWidth={strokeWidth}
          dot={showDots ? { fill: color, r: 4 } : false}
          activeDot={{ r: 6 }}
          animationDuration={500}
          animationEasing="ease"
        />
      </RechartsLineChart>
    </ResponsiveContainer>
  );
};

export default LineChart;

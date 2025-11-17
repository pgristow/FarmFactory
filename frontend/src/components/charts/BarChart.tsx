/**
 * BarChart Component
 * Comparison visualization with bars
 *
 * Features:
 * - Vertical or horizontal orientation
 * - Value labels
 * - Responsive design
 * - Tooltips
 * - Customizable colors
 *
 * Use Cases:
 * - Compare plots
 * - Compare months
 * - Any categorical comparisons
 *
 * @example
 * ```tsx
 * <BarChart
 *   data={plotData}
 *   xKey="plotName"
 *   yKey="yield"
 *   title="Yield by Plot"
 *   color="#2e7d32"
 *   horizontal={false}
 *   showValues={true}
 * />
 * ```
 */

import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  LabelList,
} from 'recharts';
import { CHART_COLORS } from '../../utils/chartHelpers';
import type { BarChartProps } from '../../types/chart';

const BarChart: React.FC<BarChartProps> = ({
  data,
  xKey,
  yKey,
  title,
  color = CHART_COLORS.primary,
  horizontal = false,
  showValues = false,
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

  // Custom label formatter
  const renderCustomLabel = (props: any) => {
    const { x, y, width, height, value } = props;
    const radius = 10;

    if (horizontal) {
      return (
        <text
          x={x + width + 5}
          y={y + height / 2}
          fill="#666"
          textAnchor="start"
          dominantBaseline="middle"
          fontSize={12}
        >
          {value.toFixed(1)}
        </text>
      );
    }

    return (
      <text
        x={x + width / 2}
        y={y - 5}
        fill="#666"
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={12}
      >
        {value.toFixed(1)}
      </text>
    );
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBarChart
        data={data}
        layout={horizontal ? 'vertical' : 'horizontal'}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      >
        {showGrid && (
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#e0e0e0"
            horizontal={!horizontal}
            vertical={horizontal}
          />
        )}
        {horizontal ? (
          <>
            <XAxis
              type="number"
              stroke="#666"
              style={{ fontSize: '12px' }}
              tick={{ fill: '#666' }}
            />
            <YAxis
              dataKey={xKey}
              type="category"
              stroke="#666"
              style={{ fontSize: '12px' }}
              tick={{ fill: '#666' }}
              width={100}
            />
          </>
        ) : (
          <>
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
          </>
        )}
        <Tooltip content={<CustomTooltip />} />
        {showLegend && (
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            iconType="rect"
          />
        )}
        <Bar
          dataKey={yKey}
          fill={color}
          radius={[4, 4, 0, 0]}
          animationDuration={500}
          animationEasing="ease"
        >
          {showValues && <LabelList content={renderCustomLabel} />}
        </Bar>
      </RechartsBarChart>
    </ResponsiveContainer>
  );
};

export default BarChart;

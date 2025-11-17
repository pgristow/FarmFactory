/**
 * MultiLineChart Component
 * Multiple data series visualization
 *
 * Features:
 * - Multiple lines with different colors
 * - Toggle series visibility
 * - Legend
 * - Responsive design
 * - Tooltips
 * - Customizable colors
 *
 * Use Cases:
 * - Compare multiple plots
 * - NPK levels over time (3 lines)
 * - Multiple sensor readings
 *
 * @example
 * ```tsx
 * <MultiLineChart
 *   data={npkData}
 *   xKey="date"
 *   yKeys={['nitrogen', 'phosphorus', 'potassium']}
 *   seriesNames={['N', 'P', 'K']}
 *   title="NPK Levels Over Time"
 *   colors={['#2e7d32', '#1976d2', '#ed6c02']}
 *   toggleSeries={true}
 * />
 * ```
 */

import React, { useState } from 'react';
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
import { getChartColors } from '../../utils/chartHelpers';
import type { MultiLineChartProps } from '../../types/chart';

const MultiLineChart: React.FC<MultiLineChartProps> = ({
  data,
  xKey,
  yKeys,
  title,
  colors,
  seriesNames,
  toggleSeries = true,
  showGrid = true,
  showLegend = true,
  height = 300,
}) => {
  const chartColors = colors || getChartColors(yKeys.length);
  const names = seriesNames || yKeys;

  // State for toggling series visibility
  const [visibleSeries, setVisibleSeries] = useState<Record<string, boolean>>(
    yKeys.reduce((acc, key) => ({ ...acc, [key]: true }), {})
  );

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

  // Handle legend click to toggle series
  const handleLegendClick = (dataKey: string) => {
    if (toggleSeries) {
      setVisibleSeries((prev) => ({
        ...prev,
        [dataKey]: !prev[dataKey],
      }));
    }
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
            wrapperStyle={{
              fontSize: '12px',
              cursor: toggleSeries ? 'pointer' : 'default',
            }}
            onClick={(e) => handleLegendClick(e.dataKey as string)}
            iconType="line"
          />
        )}
        {yKeys.map((key, index) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            name={names[index]}
            stroke={chartColors[index]}
            strokeWidth={2}
            dot={{ fill: chartColors[index], r: 4 }}
            activeDot={{ r: 6 }}
            animationDuration={500}
            animationEasing="ease"
            hide={toggleSeries && !visibleSeries[key]}
            connectNulls
          />
        ))}
      </RechartsLineChart>
    </ResponsiveContainer>
  );
};

export default MultiLineChart;

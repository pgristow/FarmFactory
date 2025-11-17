/**
 * PieChart Component
 * Proportional data visualization
 *
 * Features:
 * - Percentage labels
 * - Custom colors
 * - Responsive design
 * - Tooltips
 * - Legend
 * - Optional donut chart (innerRadius)
 *
 * Use Cases:
 * - Soil types distribution
 * - Cost breakdown by category
 * - Crop distribution
 *
 * @example
 * ```tsx
 * <PieChart
 *   data={soilTypeData}
 *   nameKey="soilType"
 *   valueKey="area"
 *   title="Soil Type Distribution"
 *   colors={['#2e7d32', '#1976d2', '#ed6c02']}
 *   showPercentage={true}
 * />
 * ```
 */

import React from 'react';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { getChartColors, calculatePercentage } from '../../utils/chartHelpers';
import type { PieChartProps } from '../../types/chart';

const PieChart: React.FC<PieChartProps> = ({
  data,
  nameKey,
  valueKey,
  title,
  colors,
  showPercentage = true,
  showLegend = true,
  innerRadius = 0,
  height = 300,
}) => {
  const chartColors = colors || getChartColors(data.length);

  // Calculate total for percentages
  const total = data.reduce((sum, item) => sum + (parseFloat(String(item[valueKey])) || 0), 0);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const value = payload[0].value;
      const percentage = calculatePercentage(value, total);

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
            {payload[0].name}
          </p>
          <p style={{ margin: '4px 0 0 0', color: payload[0].payload.fill }}>
            {`Value: ${value.toFixed(2)}`}
          </p>
          {showPercentage && (
            <p style={{ margin: '4px 0 0 0', color: '#666' }}>
              {`Percentage: ${percentage}`}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  // Custom label
  const renderCustomLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
    name,
  }: any) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    if (percent < 0.05) return null; // Don't show label for very small slices

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize={12}
        fontWeight={600}
      >
        {showPercentage ? `${(percent * 100).toFixed(0)}%` : name}
      </text>
    );
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={renderCustomLabel}
          outerRadius={height / 3}
          innerRadius={innerRadius}
          fill="#8884d8"
          dataKey={valueKey}
          nameKey={nameKey}
          animationDuration={500}
          animationEasing="ease"
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={chartColors[index % chartColors.length]}
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        {showLegend && (
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            iconType="circle"
            layout="vertical"
            align="right"
            verticalAlign="middle"
          />
        )}
      </RechartsPieChart>
    </ResponsiveContainer>
  );
};

export default PieChart;

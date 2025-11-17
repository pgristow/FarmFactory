/**
 * ChartLegend Component
 * Reusable custom legend for charts
 *
 * Features:
 * - Customizable layout (horizontal, vertical)
 * - Icon types (circle, square, line)
 * - Click handlers for toggling series
 * - Responsive design
 * - Agricultural theme colors
 *
 * Use Cases:
 * - Custom legend positioning
 * - Interactive series toggling
 * - Consistent legend styling across charts
 *
 * @example
 * ```tsx
 * <ChartLegend
 *   items={[
 *     { key: 'nitrogen', label: 'Nitrogen', color: '#2e7d32', visible: true },
 *     { key: 'phosphorus', label: 'Phosphorus', color: '#1976d2', visible: true }
 *   ]}
 *   onToggle={(key) => console.log('Toggled:', key)}
 *   layout="horizontal"
 *   iconType="circle"
 * />
 * ```
 */

import React from 'react';
import { Box, Typography, Stack, Chip } from '@mui/material';
import {
  Circle as CircleIcon,
  Square as SquareIcon,
  Remove as LineIcon,
} from '@mui/icons-material';

export interface ChartLegendItem {
  key: string;
  label: string;
  color: string;
  visible?: boolean;
  disabled?: boolean;
}

export interface ChartLegendProps {
  items: ChartLegendItem[];
  onToggle?: (key: string) => void;
  layout?: 'horizontal' | 'vertical';
  iconType?: 'circle' | 'square' | 'line';
  align?: 'left' | 'center' | 'right';
  interactive?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const ChartLegend: React.FC<ChartLegendProps> = ({
  items,
  onToggle,
  layout = 'horizontal',
  iconType = 'circle',
  align = 'center',
  interactive = true,
  size = 'medium',
}) => {
  const iconSize = size === 'small' ? 12 : size === 'large' ? 20 : 16;
  const fontSize = size === 'small' ? '0.75rem' : size === 'large' ? '1rem' : '0.875rem';

  const handleClick = (item: ChartLegendItem) => {
    if (interactive && !item.disabled && onToggle) {
      onToggle(item.key);
    }
  };

  const renderIcon = (color: string, visible: boolean = true) => {
    const iconProps = {
      sx: {
        fontSize: iconSize,
        color: visible ? color : '#ccc',
        opacity: visible ? 1 : 0.4,
      },
    };

    switch (iconType) {
      case 'square':
        return <SquareIcon {...iconProps} />;
      case 'line':
        return <LineIcon {...iconProps} />;
      case 'circle':
      default:
        return <CircleIcon {...iconProps} />;
    }
  };

  const getAlignment = () => {
    switch (align) {
      case 'left':
        return 'flex-start';
      case 'right':
        return 'flex-end';
      case 'center':
      default:
        return 'center';
    }
  };

  return (
    <Stack
      direction={layout === 'horizontal' ? 'row' : 'column'}
      spacing={layout === 'horizontal' ? 2 : 1}
      sx={{
        justifyContent: getAlignment(),
        alignItems: layout === 'horizontal' ? 'center' : 'flex-start',
        flexWrap: 'wrap',
        gap: 1,
      }}
    >
      {items.map((item) => (
        <Box
          key={item.key}
          onClick={() => handleClick(item)}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            cursor: interactive && !item.disabled ? 'pointer' : 'default',
            opacity: item.visible === false ? 0.5 : 1,
            transition: 'opacity 0.2s ease',
            userSelect: 'none',
            '&:hover': {
              opacity: interactive && !item.disabled ? 0.8 : undefined,
            },
          }}
        >
          {renderIcon(item.color, item.visible)}
          <Typography
            variant="body2"
            sx={{
              fontSize,
              color: item.visible === false ? 'text.disabled' : 'text.secondary',
              fontWeight: item.visible === false ? 400 : 500,
              textDecoration: item.visible === false ? 'line-through' : 'none',
            }}
          >
            {item.label}
          </Typography>
        </Box>
      ))}
    </Stack>
  );
};

/**
 * ChartLegendChip - Alternative chip-based legend
 * More compact, modern design with chip components
 */
export interface ChartLegendChipProps {
  items: ChartLegendItem[];
  onToggle?: (key: string) => void;
  variant?: 'filled' | 'outlined';
  size?: 'small' | 'medium';
}

export const ChartLegendChip: React.FC<ChartLegendChipProps> = ({
  items,
  onToggle,
  variant = 'outlined',
  size = 'small',
}) => {
  const handleClick = (item: ChartLegendItem) => {
    if (!item.disabled && onToggle) {
      onToggle(item.key);
    }
  };

  return (
    <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
      {items.map((item) => (
        <Chip
          key={item.key}
          label={item.label}
          size={size}
          variant={variant}
          onClick={() => handleClick(item)}
          disabled={item.disabled}
          sx={{
            borderColor: item.color,
            color: variant === 'outlined' ? item.color : 'white',
            bgcolor: variant === 'filled' ? item.color : 'transparent',
            opacity: item.visible === false ? 0.4 : 1,
            textDecoration: item.visible === false ? 'line-through' : 'none',
            '&:hover': {
              bgcolor: variant === 'filled' ? item.color : `${item.color}15`,
              borderColor: item.color,
            },
          }}
        />
      ))}
    </Stack>
  );
};

export default ChartLegend;

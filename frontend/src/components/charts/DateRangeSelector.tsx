/**
 * DateRangeSelector Component
 * Material-UI date picker with quick select buttons
 * - Today, Last 7 days, Last 30 days, Last 90 days
 * - This month, This year, Custom
 * - onChange callback with start/end dates
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  ButtonGroup,
  TextField,
  Paper,
  Typography,
} from '@mui/material';
import { getDateRange } from '../../utils/chartHelpers';
import type { DateRangeSelectorProps, QuickSelectOption } from '../../types/chart';

const DateRangeSelector: React.FC<DateRangeSelectorProps> = ({
  startDate,
  endDate,
  onChange,
  quickSelectOptions,
}) => {
  const [selectedOption, setSelectedOption] = useState<string>('30d');

  // Default quick select options
  const defaultOptions: QuickSelectOption[] = [
    {
      label: 'Today',
      value: 'today',
      getRange: () => {
        const range = getDateRange('today');
        return { startDate: range.startDate, endDate: range.endDate };
      },
    },
    {
      label: 'Last 7 days',
      value: '7d',
      getRange: () => {
        const range = getDateRange('7d');
        return { startDate: range.startDate, endDate: range.endDate };
      },
    },
    {
      label: 'Last 30 days',
      value: '30d',
      getRange: () => {
        const range = getDateRange('30d');
        return { startDate: range.startDate, endDate: range.endDate };
      },
    },
    {
      label: 'Last 90 days',
      value: '90d',
      getRange: () => {
        const range = getDateRange('90d');
        return { startDate: range.startDate, endDate: range.endDate };
      },
    },
    {
      label: 'This Month',
      value: 'thisMonth',
      getRange: () => {
        const range = getDateRange('thisMonth');
        return { startDate: range.startDate, endDate: range.endDate };
      },
    },
    {
      label: 'This Year',
      value: 'thisYear',
      getRange: () => {
        const range = getDateRange('thisYear');
        return { startDate: range.startDate, endDate: range.endDate };
      },
    },
    {
      label: 'Custom',
      value: 'custom',
      getRange: () => ({ startDate: null, endDate: null }),
    },
  ];

  const options = quickSelectOptions || defaultOptions;

  const handleQuickSelect = (option: QuickSelectOption) => {
    setSelectedOption(option.value);

    if (option.value !== 'custom') {
      const range = option.getRange();
      onChange(range);
    }
  };

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newStartDate = e.target.value ? new Date(e.target.value) : null;
    onChange({ startDate: newStartDate, endDate });
    setSelectedOption('custom');
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEndDate = e.target.value ? new Date(e.target.value) : null;
    onChange({ startDate, endDate: newEndDate });
    setSelectedOption('custom');
  };

  const formatDateForInput = (date: Date | null): string => {
    if (!date) return '';
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
        Date Range
      </Typography>

      {/* Quick Select Buttons */}
      <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {options.map((option) => (
          <Button
            key={option.value}
            variant={selectedOption === option.value ? 'contained' : 'outlined'}
            size="small"
            onClick={() => handleQuickSelect(option)}
            sx={{
              textTransform: 'none',
              ...(selectedOption === option.value && {
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
              }),
            }}
          >
            {option.label}
          </Button>
        ))}
      </Box>

      {/* Custom Date Inputs */}
      {selectedOption === 'custom' && (
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            label="Start Date"
            type="date"
            size="small"
            value={formatDateForInput(startDate)}
            onChange={handleStartDateChange}
            InputLabelProps={{
              shrink: true,
            }}
            sx={{ flex: 1, minWidth: 150 }}
          />
          <TextField
            label="End Date"
            type="date"
            size="small"
            value={formatDateForInput(endDate)}
            onChange={handleEndDateChange}
            InputLabelProps={{
              shrink: true,
            }}
            sx={{ flex: 1, minWidth: 150 }}
          />
        </Box>
      )}
    </Paper>
  );
};

export default DateRangeSelector;

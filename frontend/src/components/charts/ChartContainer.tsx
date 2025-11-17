/**
 * ChartContainer Component
 * Wrapper component for all charts with common features:
 * - Card/Paper wrapper
 * - Title header
 * - Loading/Error/Empty states
 * - Export buttons (PNG, CSV)
 * - Refresh button
 * - Time period selector
 */

import React, { useRef } from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  IconButton,
  CircularProgress,
  Alert,
  Box,
  Typography,
  Tooltip,
  ButtonGroup,
  Button,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  FileDownload as DownloadIcon,
  Image as ImageIcon,
  TableChart as CsvIcon,
} from '@mui/icons-material';
import type { ChartContainerProps, TimePeriod } from '../../types/chart';

const ChartContainer: React.FC<ChartContainerProps> = ({
  title,
  children,
  loading = false,
  error = null,
  isEmpty = false,
  period,
  onPeriodChange,
  onExportPNG,
  onExportCSV,
  onRefresh,
  showExport = true,
  showRefresh = true,
  showPeriodSelector = false,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);

  const periodOptions: TimePeriod[] = ['7D', '30D', '90D', 'Custom'];

  const handlePeriodChange = (newPeriod: TimePeriod) => {
    if (onPeriodChange) {
      onPeriodChange(newPeriod);
    }
  };

  return (
    <Card
      ref={chartRef}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: 2,
      }}
    >
      <CardHeader
        title={
          <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
        }
        action={
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {/* Period Selector */}
            {showPeriodSelector && period && onPeriodChange && (
              <ButtonGroup size="small" variant="outlined">
                {periodOptions.map((p) => (
                  <Button
                    key={p}
                    variant={period === p ? 'contained' : 'outlined'}
                    onClick={() => handlePeriodChange(p)}
                    sx={{
                      minWidth: 60,
                      ...(period === p && {
                        bgcolor: 'primary.main',
                        color: 'white',
                        '&:hover': {
                          bgcolor: 'primary.dark',
                        },
                      }),
                    }}
                  >
                    {p}
                  </Button>
                ))}
              </ButtonGroup>
            )}

            {/* Export Buttons */}
            {showExport && !loading && !error && !isEmpty && (
              <>
                <Tooltip title="Export as PNG">
                  <IconButton
                    size="small"
                    onClick={onExportPNG}
                    sx={{ color: 'primary.main' }}
                  >
                    <ImageIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Export as CSV">
                  <IconButton
                    size="small"
                    onClick={onExportCSV}
                    sx={{ color: 'primary.main' }}
                  >
                    <CsvIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </>
            )}

            {/* Refresh Button */}
            {showRefresh && onRefresh && (
              <Tooltip title="Refresh">
                <IconButton
                  size="small"
                  onClick={onRefresh}
                  disabled={loading}
                  sx={{ color: 'primary.main' }}
                >
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        }
        sx={{
          borderBottom: 1,
          borderColor: 'divider',
          pb: 1,
        }}
      />

      <CardContent sx={{ flexGrow: 1, position: 'relative', p: 2 }}>
        {/* Loading State */}
        {loading && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 300,
            }}
          >
            <CircularProgress sx={{ color: 'primary.main' }} />
          </Box>
        )}

        {/* Error State */}
        {!loading && error && (
          <Box sx={{ minHeight: 300, display: 'flex', alignItems: 'center' }}>
            <Alert severity="error" sx={{ width: '100%' }}>
              {error}
            </Alert>
          </Box>
        )}

        {/* Empty State */}
        {!loading && !error && isEmpty && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 300,
              color: 'text.secondary',
            }}
          >
            <DownloadIcon sx={{ fontSize: 64, mb: 2, opacity: 0.3 }} />
            <Typography variant="h6" gutterBottom>
              No data available
            </Typography>
            <Typography variant="body2">
              There is no data to display for the selected period
            </Typography>
          </Box>
        )}

        {/* Chart Content */}
        {!loading && !error && !isEmpty && children}
      </CardContent>
    </Card>
  );
};

export default ChartContainer;

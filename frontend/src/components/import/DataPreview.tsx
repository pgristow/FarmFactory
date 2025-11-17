import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  ArrowForward as ForwardIcon,
  TableChart as TableIcon,
} from '@mui/icons-material';
import importService from '../../services/importService';
import { DataPreview as DataPreviewType } from '../../types/import';

interface DataPreviewProps {
  jobId: string;
  onNext: () => void;
  onBack: () => void;
}

export default function DataPreview({ jobId, onNext, onBack }: DataPreviewProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [preview, setPreview] = useState<DataPreviewType | null>(null);

  useEffect(() => {
    loadPreview();
  }, [jobId]);

  const loadPreview = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await importService.getPreview(jobId);
      setPreview(data);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load preview');
    } finally {
      setLoading(false);
    }
  };

  const getDataTypeColor = (dataType: string): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    switch (dataType.toLowerCase()) {
      case 'string':
      case 'text':
        return 'info';
      case 'number':
      case 'integer':
      case 'float':
        return 'success';
      case 'date':
      case 'datetime':
        return 'warning';
      case 'boolean':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getDataTypeIcon = (dataType: string): string => {
    switch (dataType.toLowerCase()) {
      case 'string':
      case 'text':
        return 'Abc';
      case 'number':
      case 'integer':
      case 'float':
        return '123';
      case 'date':
      case 'datetime':
        return '📅';
      case 'boolean':
        return '✓/✗';
      default:
        return '?';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button startIcon={<BackIcon />} onClick={onBack}>
            Back
          </Button>
          <Button variant="outlined" onClick={loadPreview}>
            Retry
          </Button>
        </Box>
      </Box>
    );
  }

  if (!preview) {
    return (
      <Alert severity="warning">
        No preview data available
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Data Preview
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Review the first 10 rows of your data before mapping columns
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Rows
              </Typography>
              <Typography variant="h4">
                {preview.total_rows.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Columns
              </Typography>
              <Typography variant="h4">
                {preview.columns.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Preview Rows
              </Typography>
              <Typography variant="h4">
                {preview.preview_rows}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Column Types */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Detected Column Types:
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
          {preview.columns.map((col) => (
            <Chip
              key={col}
              label={`${col}: ${preview.data_types[col] || 'unknown'}`}
              color={getDataTypeColor(preview.data_types[col] || 'unknown')}
              size="small"
              icon={<span>{getDataTypeIcon(preview.data_types[col] || 'unknown')}</span>}
            />
          ))}
        </Box>
      </Paper>

      {/* Data Table */}
      <TableContainer component={Paper} sx={{ maxHeight: 500, mb: 3 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ backgroundColor: 'primary.main', color: 'white', fontWeight: 'bold' }}>
                #
              </TableCell>
              {preview.columns.map((col) => (
                <TableCell
                  key={col}
                  sx={{ backgroundColor: 'primary.main', color: 'white', fontWeight: 'bold', minWidth: 150 }}
                >
                  <Box>
                    <div>{col}</div>
                    <Chip
                      label={preview.data_types[col] || 'unknown'}
                      size="small"
                      sx={{ mt: 0.5, height: 20, fontSize: '0.7rem' }}
                    />
                  </Box>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {preview.rows.map((row, index) => (
              <TableRow key={index} hover>
                <TableCell sx={{ fontWeight: 'bold', color: 'text.secondary' }}>
                  {index + 1}
                </TableCell>
                {preview.columns.map((col) => (
                  <TableCell key={col}>
                    {row[col] !== null && row[col] !== undefined ? String(row[col]) : (
                      <Typography variant="body2" color="text.disabled" fontStyle="italic">
                        (empty)
                      </Typography>
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {preview.total_rows > preview.preview_rows && (
        <Alert severity="info" icon={<TableIcon />} sx={{ mb: 3 }}>
          Showing first {preview.preview_rows} rows of {preview.total_rows.toLocaleString()} total rows
        </Alert>
      )}

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button startIcon={<BackIcon />} onClick={onBack}>
          Back
        </Button>
        <Button
          variant="contained"
          endIcon={<ForwardIcon />}
          onClick={onNext}
        >
          Continue to Mapping
        </Button>
      </Box>
    </Box>
  );
}

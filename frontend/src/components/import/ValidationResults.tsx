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
  Card,
  CardContent,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControlLabel,
  Radio,
  RadioGroup,
  IconButton,
  Collapse,
  TablePagination,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  ArrowForward as ForwardIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  KeyboardArrowDown as ArrowDownIcon,
  KeyboardArrowUp as ArrowUpIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip as RechartsTooltip } from 'recharts';
import importService from '../../services/importService';
import { DataType, ColumnMapping, ValidationResult, ImportError } from '../../types/import';

interface ValidationResultsProps {
  jobId: string;
  dataType: DataType;
  columnMappings: ColumnMapping[];
  onNext: (skipInvalidRows: boolean) => void;
  onBack: () => void;
}

const ERROR_TYPE_COLORS: Record<string, string> = {
  'data_type': '#f44336',
  'range': '#ff9800',
  'required': '#e91e63',
  'duplicate': '#9c27b0',
  'reference': '#3f51b5',
  'format': '#ff5722',
};

export default function ValidationResults({
  jobId,
  dataType,
  columnMappings,
  onNext,
  onBack,
}: ValidationResultsProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [proceedOption, setProceedOption] = useState<'valid_only' | 'fix_reupload'>('valid_only');
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    validateImport();
  }, [jobId, columnMappings]);

  const validateImport = async () => {
    try {
      setLoading(true);
      setError('');
      const result = await importService.validateImport({
        job_id: jobId,
        data_type: dataType,
        mappings: columnMappings,
      });
      setValidationResult(result);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to validate import');
    } finally {
      setLoading(false);
    }
  };

  const handleExportErrors = async () => {
    try {
      const blob = await importService.exportErrors(jobId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `import_errors_${jobId}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to export errors');
    }
  };

  const handleContinue = () => {
    if (!validationResult?.can_proceed && proceedOption === 'valid_only') {
      setError('Cannot proceed: too many errors. Please fix your data and re-upload.');
      return;
    }
    onNext(proceedOption === 'valid_only');
  };

  const toggleRowExpansion = (rowNumber: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(rowNumber)) {
      newExpanded.delete(rowNumber);
    } else {
      newExpanded.add(rowNumber);
    }
    setExpandedRows(newExpanded);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && !validationResult) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button startIcon={<BackIcon />} onClick={onBack}>
            Back
          </Button>
          <Button variant="outlined" onClick={validateImport}>
            Retry
          </Button>
        </Box>
      </Box>
    );
  }

  if (!validationResult) {
    return (
      <Alert severity="warning">
        No validation results available
      </Alert>
    );
  }

  const errorChartData = Object.entries(validationResult.error_summary).map(([type, count]) => ({
    name: type.replace('_', ' ').toUpperCase(),
    value: count,
    color: ERROR_TYPE_COLORS[type] || '#607d8b',
  }));

  const errorPercentage = validationResult.total_rows > 0
    ? (validationResult.invalid_rows / validationResult.total_rows * 100).toFixed(1)
    : 0;

  const paginatedErrors = validationResult.errors.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Validation Results
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Review validation errors before proceeding with the import
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total Rows
                  </Typography>
                  <Typography variant="h4">
                    {validationResult.total_rows.toLocaleString()}
                  </Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 48, color: 'action.disabled' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Valid Rows
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {validationResult.valid_rows.toLocaleString()}
                  </Typography>
                </Box>
                <SuccessIcon sx={{ fontSize: 48, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Errors
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {validationResult.invalid_rows.toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    ({errorPercentage}% of total)
                  </Typography>
                </Box>
                <ErrorIcon sx={{ fontSize: 48, color: 'error.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Status Alert */}
      {validationResult.invalid_rows === 0 ? (
        <Alert severity="success" sx={{ mb: 3 }} icon={<SuccessIcon />}>
          All rows passed validation! You can proceed with the import.
        </Alert>
      ) : (
        <Alert
          severity={validationResult.can_proceed ? 'warning' : 'error'}
          sx={{ mb: 3 }}
          icon={validationResult.can_proceed ? <WarningIcon /> : <ErrorIcon />}
        >
          Found {validationResult.invalid_rows} rows with errors.{' '}
          {validationResult.can_proceed
            ? 'You can choose to import only valid rows or fix the errors and re-upload.'
            : 'Too many errors to proceed. Please fix your data and re-upload.'}
        </Alert>
      )}

      {/* Error Breakdown Chart */}
      {validationResult.invalid_rows > 0 && (
        <Accordion defaultExpanded sx={{ mb: 3 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Error Breakdown</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={errorChartData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label={(entry) => `${entry.name}: ${entry.value}`}
                    >
                      {errorChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 3 }}>
                  {Object.entries(validationResult.error_summary).map(([type, count]) => (
                    <Box key={type} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Chip
                        label={type.replace('_', ' ').toUpperCase()}
                        sx={{
                          backgroundColor: ERROR_TYPE_COLORS[type] || '#607d8b',
                          color: 'white',
                        }}
                      />
                      <Typography variant="h6">{count}</Typography>
                    </Box>
                  ))}
                </Box>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Error Table */}
      {validationResult.errors.length > 0 && (
        <Paper sx={{ mb: 3 }}>
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Error Details</Typography>
            <Button
              startIcon={<DownloadIcon />}
              onClick={handleExportErrors}
              size="small"
            >
              Export Errors
            </Button>
          </Box>
          <TableContainer sx={{ maxHeight: 400 }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell width={50}></TableCell>
                  <TableCell>Row #</TableCell>
                  <TableCell>Column</TableCell>
                  <TableCell>Error Type</TableCell>
                  <TableCell>Error Message</TableCell>
                  <TableCell>Invalid Value</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedErrors.map((err) => (
                  <>
                    <TableRow key={`${err.row_number}-${err.column_name}`} hover>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => toggleRowExpansion(err.row_number)}
                        >
                          {expandedRows.has(err.row_number) ? <ArrowUpIcon /> : <ArrowDownIcon />}
                        </IconButton>
                      </TableCell>
                      <TableCell>{err.row_number}</TableCell>
                      <TableCell>
                        <Chip label={err.column_name} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={err.error_type}
                          size="small"
                          sx={{
                            backgroundColor: ERROR_TYPE_COLORS[err.error_type] || '#607d8b',
                            color: 'white',
                          }}
                        />
                      </TableCell>
                      <TableCell>{err.error_message}</TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            fontFamily: 'monospace',
                            color: 'error.main',
                            maxWidth: 200,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {err.invalid_value || 'N/A'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                        <Collapse in={expandedRows.has(err.row_number)} timeout="auto" unmountOnExit>
                          <Box sx={{ margin: 2 }}>
                            {err.suggested_fix && (
                              <Alert severity="info" sx={{ mb: 1 }}>
                                <strong>Suggested Fix:</strong> {err.suggested_fix}
                              </Alert>
                            )}
                            {err.row_data && (
                              <Paper variant="outlined" sx={{ p: 2 }}>
                                <Typography variant="subtitle2" gutterBottom>
                                  Row Data:
                                </Typography>
                                <Box sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                                  {JSON.stringify(err.row_data, null, 2)}
                                </Box>
                              </Paper>
                            )}
                          </Box>
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  </>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={validationResult.errors.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
          />
        </Paper>
      )}

      {/* Proceed Options */}
      {validationResult.invalid_rows > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            How would you like to proceed?
          </Typography>
          <RadioGroup value={proceedOption} onChange={(e) => setProceedOption(e.target.value as any)}>
            <FormControlLabel
              value="valid_only"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body1">
                    Import only valid rows ({validationResult.valid_rows.toLocaleString()} rows)
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Skip rows with errors and import the rest
                  </Typography>
                </Box>
              }
              disabled={!validationResult.can_proceed}
            />
            <FormControlLabel
              value="fix_reupload"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body1">
                    Fix errors and re-upload
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Download error report, fix your data, and start over
                  </Typography>
                </Box>
              }
            />
          </RadioGroup>
        </Paper>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button startIcon={<BackIcon />} onClick={onBack}>
          Back to Mapping
        </Button>
        {proceedOption === 'fix_reupload' ? (
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExportErrors}
          >
            Download Errors & Start Over
          </Button>
        ) : (
          <Button
            variant="contained"
            endIcon={<ForwardIcon />}
            onClick={handleContinue}
            disabled={!validationResult.can_proceed && proceedOption === 'valid_only'}
          >
            {validationResult.invalid_rows === 0
              ? 'Continue to Import'
              : `Import ${validationResult.valid_rows.toLocaleString()} Valid Rows`}
          </Button>
        )}
      </Box>
    </Box>
  );
}

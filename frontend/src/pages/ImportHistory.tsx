import { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Tooltip,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import importService from '../services/importService';
import {
  ImportJob,
  ImportStatus,
  DataType,
  DATA_TYPE_LABELS,
  STATUS_LABELS,
  STATUS_COLORS,
  ImportError,
} from '../types/import';

export default function ImportHistory() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [jobs, setJobs] = useState<ImportJob[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [statusFilter, setStatusFilter] = useState<ImportStatus | ''>('');
  const [dataTypeFilter, setDataTypeFilter] = useState<DataType | ''>('');

  // Error dialog state
  const [selectedJob, setSelectedJob] = useState<ImportJob | null>(null);
  const [jobErrors, setJobErrors] = useState<ImportError[]>([]);
  const [loadingErrors, setLoadingErrors] = useState(false);
  const [showErrorDialog, setShowErrorDialog] = useState(false);

  // Delete confirmation
  const [deleteJobId, setDeleteJobId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadHistory();
  }, [page, rowsPerPage, statusFilter, dataTypeFilter]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await importService.getImportHistory(
        page + 1, // API uses 1-based pagination
        rowsPerPage,
        {
          status: statusFilter || undefined,
          data_type: dataTypeFilter || undefined,
        }
      );
      setJobs(response.jobs);
      setTotal(response.total);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load import history');
    } finally {
      setLoading(false);
    }
  };

  const handleViewErrors = async (job: ImportJob) => {
    setSelectedJob(job);
    setShowErrorDialog(true);
    setLoadingErrors(true);

    try {
      const errors = await importService.getImportErrors(job.id);
      setJobErrors(errors);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load errors');
    } finally {
      setLoadingErrors(false);
    }
  };

  const handleDownloadErrors = async (jobId: string) => {
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
      setError('Failed to download errors');
    }
  };

  const handleDeleteJob = async () => {
    if (!deleteJobId) return;

    try {
      setDeleting(true);
      await importService.deleteImportJob(deleteJobId);
      setDeleteJobId(null);
      loadHistory(); // Reload the list
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to delete import job');
    } finally {
      setDeleting(false);
    }
  };

  const formatDate = (dateString: string): string => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
    } catch {
      return dateString;
    }
  };

  const calculateDuration = (job: ImportJob): string => {
    if (!job.completed_at) return 'In Progress';

    try {
      const start = new Date(job.started_at).getTime();
      const end = new Date(job.completed_at).getTime();
      const durationMs = end - start;
      const seconds = Math.floor(durationMs / 1000);

      if (seconds < 60) return `${seconds}s`;
      const minutes = Math.floor(seconds / 60);
      if (minutes < 60) return `${minutes}m ${seconds % 60}s`;
      const hours = Math.floor(minutes / 60);
      return `${hours}h ${minutes % 60}m`;
    } catch {
      return 'N/A';
    }
  };

  const getSuccessRate = (job: ImportJob): number => {
    if (job.total_rows === 0) return 0;
    return ((job.processed_rows / job.total_rows) * 100);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Import History
            </Typography>
            <Typography variant="body1" color="text.secondary">
              View and manage all data import jobs
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadHistory}
            >
              Refresh
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/import')}
            >
              New Import
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                label="Status"
                onChange={(e) => {
                  setStatusFilter(e.target.value as ImportStatus | '');
                  setPage(0);
                }}
              >
                <MenuItem value="">All Statuses</MenuItem>
                {Object.entries(STATUS_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Data Type</InputLabel>
              <Select
                value={dataTypeFilter}
                label="Data Type"
                onChange={(e) => {
                  setDataTypeFilter(e.target.value as DataType | '');
                  setPage(0);
                }}
              >
                <MenuItem value="">All Types</MenuItem>
                {Object.entries(DATA_TYPE_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Table */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : jobs.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No import history found
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Start your first import to see it here
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/import')}
              sx={{ mt: 2 }}
            >
              Start Import
            </Button>
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Filename</TableCell>
                    <TableCell>Data Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Rows</TableCell>
                    <TableCell align="right">Errors</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.id} hover>
                      <TableCell>{formatDate(job.started_at)}</TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {job.filename}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {job.file_type.toUpperCase()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={DATA_TYPE_LABELS[job.data_type] || job.data_type}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={STATUS_LABELS[job.status]}
                          color={STATUS_COLORS[job.status]}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Box>
                          <Typography variant="body2">
                            {job.processed_rows.toLocaleString()} / {job.total_rows.toLocaleString()}
                          </Typography>
                          {job.status === 'completed' && (
                            <Typography variant="caption" color="text.secondary">
                              {getSuccessRate(job).toFixed(1)}%
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        {job.error_count > 0 ? (
                          <Chip
                            label={job.error_count.toLocaleString()}
                            color="error"
                            size="small"
                          />
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            0
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {calculateDuration(job)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                          {job.error_count > 0 && (
                            <>
                              <Tooltip title="View Errors">
                                <IconButton
                                  size="small"
                                  onClick={() => handleViewErrors(job)}
                                >
                                  <ViewIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Download Errors">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDownloadErrors(job.id)}
                                >
                                  <DownloadIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </>
                          )}
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => setDeleteJobId(job.id)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              rowsPerPageOptions={[10, 20, 50, 100]}
              component="div"
              count={total}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
            />
          </>
        )}
      </Paper>

      {/* Error Details Dialog */}
      <Dialog
        open={showErrorDialog}
        onClose={() => setShowErrorDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h6">Import Errors</Typography>
              {selectedJob && (
                <Typography variant="body2" color="text.secondary">
                  {selectedJob.filename} - {selectedJob.error_count} errors
                </Typography>
              )}
            </Box>
            <IconButton onClick={() => handleDownloadErrors(selectedJob?.id || '')}>
              <DownloadIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {loadingErrors ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : jobErrors.length === 0 ? (
            <Typography>No errors found</Typography>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Row #</TableCell>
                    <TableCell>Column</TableCell>
                    <TableCell>Error Type</TableCell>
                    <TableCell>Message</TableCell>
                    <TableCell>Invalid Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobErrors.map((err, index) => (
                    <TableRow key={index}>
                      <TableCell>{err.row_number}</TableCell>
                      <TableCell>
                        <Chip label={err.column_name} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip label={err.error_type} size="small" color="error" />
                      </TableCell>
                      <TableCell>{err.error_message}</TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {err.invalid_value || 'N/A'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowErrorDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteJobId !== null} onClose={() => setDeleteJobId(null)}>
        <DialogTitle>Delete Import Job?</DialogTitle>
        <DialogContent>
          <Alert severity="warning" icon={<ErrorIcon />}>
            Are you sure you want to delete this import job? This will only remove the history record.
            Any imported data will remain in the database.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteJobId(null)} disabled={deleting}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteJob}
            color="error"
            variant="contained"
            disabled={deleting}
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

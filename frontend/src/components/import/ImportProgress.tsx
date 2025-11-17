import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  LinearProgress,
  Paper,
  Card,
  CardContent,
  Chip,
  CircularProgress as MuiCircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import importService from '../../services/importService';
import { ColumnMapping, ImportProgress as ImportProgressType, ImportStatus } from '../../types/import';

interface ImportProgressProps {
  jobId: string;
  columnMappings: ColumnMapping[];
  skipInvalidRows: boolean;
  onComplete: () => void;
  onReset: () => void;
}

const POLL_INTERVAL = 2000; // 2 seconds

export default function ImportProgress({
  jobId,
  columnMappings,
  skipInvalidRows,
  onComplete,
  onReset,
}: ImportProgressProps) {
  const navigate = useNavigate();
  const [progress, setProgress] = useState<ImportProgressType | null>(null);
  const [error, setError] = useState<string>('');
  const [importStarted, setImportStarted] = useState(false);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  const startImport = useCallback(async () => {
    try {
      setError('');
      await importService.processImport({
        job_id: jobId,
        skip_invalid_rows: skipInvalidRows,
        column_mapping: columnMappings,
      });
      setImportStarted(true);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to start import');
    }
  }, [jobId, columnMappings, skipInvalidRows]);

  const pollProgress = useCallback(async () => {
    try {
      const progressData = await importService.getImportStatus(jobId);
      setProgress(progressData);

      // Check if import is complete
      if (progressData.status === 'completed' || progressData.status === 'failed' || progressData.status === 'cancelled') {
        if (progressData.status === 'completed') {
          onComplete();
        }
        return true; // Stop polling
      }
      return false; // Continue polling
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch import status');
      return true; // Stop polling on error
    }
  }, [jobId, onComplete]);

  useEffect(() => {
    startImport();
  }, [startImport]);

  useEffect(() => {
    if (!importStarted) return;

    // Start polling
    const interval = setInterval(async () => {
      const shouldStop = await pollProgress();
      if (shouldStop) {
        clearInterval(interval);
      }
    }, POLL_INTERVAL);

    // Initial poll
    pollProgress();

    return () => clearInterval(interval);
  }, [importStarted, pollProgress]);

  const handleCancelImport = async () => {
    try {
      setCancelling(true);
      await importService.cancelImport(jobId);
      setShowCancelDialog(false);
      await pollProgress(); // Update status
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to cancel import');
    } finally {
      setCancelling(false);
    }
  };

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStatusColor = (status: ImportStatus): 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'warning';
      case 'processing':
        return 'primary';
      default:
        return 'info';
    }
  };

  const isInProgress = progress?.status && ['pending', 'uploading', 'parsing', 'validating', 'processing'].includes(progress.status);
  const isCompleted = progress?.status === 'completed';
  const isFailed = progress?.status === 'failed';
  const isCancelled = progress?.status === 'cancelled';

  if (!progress && !error) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: 400, justifyContent: 'center' }}>
        <MuiCircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 3 }}>
          Starting import...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h6" gutterBottom>
          {isCompleted && 'Import Completed Successfully!'}
          {isFailed && 'Import Failed'}
          {isCancelled && 'Import Cancelled'}
          {isInProgress && 'Import in Progress'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {progress?.current_step || 'Initializing...'}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Progress Card */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Progress
              </Typography>
              <Chip
                label={progress?.status.toUpperCase()}
                color={getStatusColor(progress?.status || 'pending')}
                size="small"
              />
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress?.progress_percentage || 0}
              sx={{ height: 10, borderRadius: 5 }}
              color={isCompleted ? 'success' : isFailed ? 'error' : 'primary'}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              {progress?.progress_percentage.toFixed(1)}% Complete
            </Typography>
          </Box>

          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Processed Rows
              </Typography>
              <Typography variant="h6">
                {progress?.processed_rows.toLocaleString() || 0} / {progress?.total_rows.toLocaleString() || 0}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Elapsed Time
              </Typography>
              <Typography variant="h6">
                {formatDuration(progress?.elapsed_time || 0)}
              </Typography>
            </Box>
            {progress?.estimated_time_remaining !== undefined && isInProgress && (
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Estimated Time Remaining
                </Typography>
                <Typography variant="h6">
                  {formatDuration(progress.estimated_time_remaining)}
                </Typography>
              </Box>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Success Message */}
      {isCompleted && (
        <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: 'success.light', mb: 3 }}>
          <SuccessIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom color="success.dark">
            Import Completed Successfully!
          </Typography>
          <Typography variant="body1" color="success.dark">
            Successfully imported {progress?.processed_rows.toLocaleString()} rows in{' '}
            {formatDuration(progress?.elapsed_time || 0)}
          </Typography>
        </Paper>
      )}

      {/* Error Message */}
      {isFailed && (
        <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: 'error.light', mb: 3 }}>
          <ErrorIcon sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom color="error.dark">
            Import Failed
          </Typography>
          <Typography variant="body1" color="error.dark">
            {progress?.error_message || 'An error occurred during import'}
          </Typography>
        </Paper>
      )}

      {/* Cancelled Message */}
      {isCancelled && (
        <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: 'warning.light', mb: 3 }}>
          <CancelIcon sx={{ fontSize: 80, color: 'warning.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom color="warning.dark">
            Import Cancelled
          </Typography>
          <Typography variant="body1" color="warning.dark">
            The import was cancelled by user request
          </Typography>
        </Paper>
      )}

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 4 }}>
        {isInProgress && (
          <Button
            variant="outlined"
            color="error"
            startIcon={<CancelIcon />}
            onClick={() => setShowCancelDialog(true)}
          >
            Cancel Import
          </Button>
        )}

        {(isCompleted || isFailed || isCancelled) && (
          <>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={onReset}
            >
              Start New Import
            </Button>
            <Button
              variant="contained"
              startIcon={<HomeIcon />}
              onClick={() => navigate('/import-history')}
            >
              View Import History
            </Button>
          </>
        )}
      </Box>

      {/* Cancel Confirmation Dialog */}
      <Dialog open={showCancelDialog} onClose={() => setShowCancelDialog(false)}>
        <DialogTitle>Cancel Import?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to cancel this import? This action cannot be undone.
            Any data that has already been imported will be rolled back.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCancelDialog(false)} disabled={cancelling}>
            No, Continue Import
          </Button>
          <Button
            onClick={handleCancelImport}
            color="error"
            variant="contained"
            disabled={cancelling}
            autoFocus
          >
            {cancelling ? 'Cancelling...' : 'Yes, Cancel Import'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

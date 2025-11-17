import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  FormControl,
  Select,
  MenuItem,
  Chip,
  Grid,
  Divider,
  TextField,
  Switch,
  FormControlLabel,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  ArrowForward as ForwardIcon,
  ArrowRightAlt as ArrowIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Help as HelpIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import importService from '../../services/importService';
import { DataType, ColumnMapping } from '../../types/import';

interface ColumnMapperProps {
  jobId: string;
  dataType: DataType;
  onNext: (mappings: ColumnMapping[]) => void;
  onBack: () => void;
}

// Mock target fields for each data type (in real app, these would come from backend)
const TARGET_FIELDS: Record<DataType, Array<{ field: string; label: string; required: boolean; description: string }>> = {
  farms_plots: [
    { field: 'farm_name', label: 'Farm Name', required: true, description: 'Name of the farm' },
    { field: 'plot_name', label: 'Plot Name', required: true, description: 'Name or identifier of the plot' },
    { field: 'area_hectares', label: 'Area (Hectares)', required: true, description: 'Plot area in hectares' },
    { field: 'latitude', label: 'Latitude', required: false, description: 'GPS latitude coordinate' },
    { field: 'longitude', label: 'Longitude', required: false, description: 'GPS longitude coordinate' },
    { field: 'soil_type', label: 'Soil Type', required: false, description: 'Type of soil' },
    { field: 'crop_type', label: 'Crop Type', required: false, description: 'Type of crop planted' },
  ],
  irrigation: [
    { field: 'farm_name', label: 'Farm Name', required: true, description: 'Name of the farm' },
    { field: 'plot_name', label: 'Plot Name', required: true, description: 'Name of the plot' },
    { field: 'date', label: 'Date', required: true, description: 'Date of irrigation event' },
    { field: 'water_amount_liters', label: 'Water Amount (Liters)', required: true, description: 'Amount of water used' },
    { field: 'duration_minutes', label: 'Duration (Minutes)', required: false, description: 'Duration of irrigation' },
    { field: 'method', label: 'Method', required: false, description: 'Irrigation method (drip, sprinkler, etc.)' },
  ],
  nutrients: [
    { field: 'farm_name', label: 'Farm Name', required: true, description: 'Name of the farm' },
    { field: 'plot_name', label: 'Plot Name', required: true, description: 'Name of the plot' },
    { field: 'date', label: 'Date', required: true, description: 'Date of application' },
    { field: 'nutrient_type', label: 'Nutrient Type', required: true, description: 'Type of nutrient/fertilizer' },
    { field: 'amount_kg', label: 'Amount (kg)', required: true, description: 'Amount applied in kilograms' },
    { field: 'application_method', label: 'Application Method', required: false, description: 'How it was applied' },
  ],
  phenology: [
    { field: 'farm_name', label: 'Farm Name', required: true, description: 'Name of the farm' },
    { field: 'plot_name', label: 'Plot Name', required: true, description: 'Name of the plot' },
    { field: 'date', label: 'Date', required: true, description: 'Date of observation' },
    { field: 'growth_stage', label: 'Growth Stage', required: true, description: 'Current growth stage' },
    { field: 'notes', label: 'Notes', required: false, description: 'Observation notes' },
  ],
  financial: [
    { field: 'farm_name', label: 'Farm Name', required: true, description: 'Name of the farm' },
    { field: 'date', label: 'Date', required: true, description: 'Date of transaction' },
    { field: 'category', label: 'Category', required: true, description: 'Income or expense category' },
    { field: 'amount', label: 'Amount', required: true, description: 'Transaction amount' },
    { field: 'description', label: 'Description', required: false, description: 'Transaction description' },
  ],
};

export default function ColumnMapper({ jobId, dataType, onNext, onBack }: ColumnMapperProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [sourceColumns, setSourceColumns] = useState<string[]>([]);
  const [mappings, setMappings] = useState<ColumnMapping[]>([]);
  const [saveAsTemplate, setSaveAsTemplate] = useState(false);
  const [templateName, setTemplateName] = useState('');

  useEffect(() => {
    loadMappings();
  }, [jobId, dataType]);

  const loadMappings = async () => {
    try {
      setLoading(true);
      setError('');

      // Get preview to get column names
      const preview = await importService.getPreview(jobId);
      setSourceColumns(preview.columns);

      // Get auto-detected mappings
      try {
        const autoMappings = await importService.getColumnMappings(jobId, dataType);
        if (autoMappings && autoMappings.mappings) {
          setMappings(autoMappings.mappings);
        } else {
          // Create empty mappings if auto-detection fails
          initializeEmptyMappings(preview.columns);
        }
      } catch {
        // If auto-mapping fails, initialize empty mappings
        initializeEmptyMappings(preview.columns);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load column mappings');
    } finally {
      setLoading(false);
    }
  };

  const initializeEmptyMappings = (columns: string[]) => {
    const emptyMappings: ColumnMapping[] = columns.map((col) => ({
      source_column: col,
      target_field: '',
      confidence: 0,
      ignore: false,
    }));
    setMappings(emptyMappings);
  };

  const handleMappingChange = (sourceColumn: string, targetField: string) => {
    setMappings((prev) =>
      prev.map((m) =>
        m.source_column === sourceColumn
          ? { ...m, target_field: targetField, confidence: targetField ? 100 : 0, ignore: false }
          : m
      )
    );
  };

  const handleIgnoreToggle = (sourceColumn: string) => {
    setMappings((prev) =>
      prev.map((m) =>
        m.source_column === sourceColumn
          ? { ...m, ignore: !m.ignore, target_field: m.ignore ? m.target_field : '' }
          : m
      )
    );
  };

  const getConfidenceColor = (confidence: number): 'success' | 'warning' | 'error' => {
    if (confidence >= 80) return 'success';
    if (confidence >= 50) return 'warning';
    return 'error';
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 80) return <CheckIcon fontSize="small" />;
    if (confidence >= 50) return <WarningIcon fontSize="small" />;
    return <ErrorIcon fontSize="small" />;
  };

  const isValidMapping = (): boolean => {
    const targetFields = TARGET_FIELDS[dataType];
    const requiredFields = targetFields.filter((f) => f.required);

    // Check if all required fields are mapped
    for (const required of requiredFields) {
      const isMapped = mappings.some(
        (m) => m.target_field === required.field && !m.ignore
      );
      if (!isMapped) {
        return false;
      }
    }

    return true;
  };

  const getMissingRequiredFields = (): string[] => {
    const targetFields = TARGET_FIELDS[dataType];
    const requiredFields = targetFields.filter((f) => f.required);
    const missing: string[] = [];

    for (const required of requiredFields) {
      const isMapped = mappings.some(
        (m) => m.target_field === required.field && !m.ignore
      );
      if (!isMapped) {
        missing.push(required.label);
      }
    }

    return missing;
  };

  const handleContinue = () => {
    if (!isValidMapping()) {
      setError(`Missing required field mappings: ${getMissingRequiredFields().join(', ')}`);
      return;
    }
    onNext(mappings.filter((m) => !m.ignore && m.target_field));
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  const targetFields = TARGET_FIELDS[dataType];
  const missingRequired = getMissingRequiredFields();

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Map Columns
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Map your CSV columns to the database fields. Required fields are marked with *
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Mapping Summary */}
      <Paper sx={{ p: 2, mb: 3, backgroundColor: 'grey.50' }}>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <Typography variant="body2" color="text.secondary">
              Total Columns
            </Typography>
            <Typography variant="h6">{sourceColumns.length}</Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="body2" color="text.secondary">
              Mapped
            </Typography>
            <Typography variant="h6" color="success.main">
              {mappings.filter((m) => m.target_field && !m.ignore).length}
            </Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="body2" color="text.secondary">
              Ignored
            </Typography>
            <Typography variant="h6" color="text.disabled">
              {mappings.filter((m) => m.ignore).length}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Column Mappings */}
      <Paper sx={{ mb: 3 }}>
        {mappings.map((mapping, index) => (
          <Box key={mapping.source_column}>
            <Box sx={{ p: 2 }}>
              <Grid container spacing={2} alignItems="center">
                {/* Source Column */}
                <Grid item xs={12} md={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={mapping.source_column}
                      color="primary"
                      variant="outlined"
                      sx={{ fontFamily: 'monospace' }}
                    />
                  </Box>
                </Grid>

                {/* Arrow */}
                <Grid item xs={12} md={1} sx={{ textAlign: 'center' }}>
                  <ArrowIcon color="action" />
                </Grid>

                {/* Target Field */}
                <Grid item xs={12} md={5}>
                  <FormControl fullWidth size="small" disabled={mapping.ignore}>
                    <Select
                      value={mapping.target_field || ''}
                      onChange={(e) => handleMappingChange(mapping.source_column, e.target.value)}
                      displayEmpty
                    >
                      <MenuItem value="">
                        <em>Select target field...</em>
                      </MenuItem>
                      {targetFields.map((field) => (
                        <MenuItem key={field.field} value={field.field}>
                          {field.label}
                          {field.required && ' *'}
                          <Tooltip title={field.description}>
                            <IconButton size="small" sx={{ ml: 1 }}>
                              <HelpIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                {/* Confidence & Ignore */}
                <Grid item xs={12} md={2}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'flex-end' }}>
                    {mapping.target_field && !mapping.ignore && (
                      <Chip
                        icon={getConfidenceIcon(mapping.confidence)}
                        label={`${mapping.confidence}%`}
                        color={getConfidenceColor(mapping.confidence)}
                        size="small"
                      />
                    )}
                    <FormControlLabel
                      control={
                        <Switch
                          checked={mapping.ignore}
                          onChange={() => handleIgnoreToggle(mapping.source_column)}
                          size="small"
                        />
                      }
                      label="Ignore"
                    />
                  </Box>
                </Grid>
              </Grid>
            </Box>
            {index < mappings.length - 1 && <Divider />}
          </Box>
        ))}
      </Paper>

      {/* Required Fields Warning */}
      {missingRequired.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Missing required fields: {missingRequired.join(', ')}
        </Alert>
      )}

      {/* Save as Template */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <FormControlLabel
          control={
            <Switch
              checked={saveAsTemplate}
              onChange={(e) => setSaveAsTemplate(e.target.checked)}
            />
          }
          label="Save this mapping as a template"
        />
        {saveAsTemplate && (
          <TextField
            fullWidth
            size="small"
            label="Template Name"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            placeholder="e.g., My Farm Import Template"
            sx={{ mt: 2 }}
          />
        )}
      </Paper>

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button startIcon={<BackIcon />} onClick={onBack}>
          Back
        </Button>
        <Button
          variant="contained"
          endIcon={<ForwardIcon />}
          onClick={handleContinue}
          disabled={!isValidMapping()}
        >
          Continue to Validation
        </Button>
      </Box>
    </Box>
  );
}

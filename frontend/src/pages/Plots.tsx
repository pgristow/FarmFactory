import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import plotService from '../services/plotService';
import farmService from '../services/farmService';
import type { Plot } from '../types/farm';
import type { CreatePlotRequest } from '../types/api';
import Loading from '../components/common/Loading';

function Plots() {
  const queryClient = useQueryClient();
  const [openDialog, setOpenDialog] = useState(false);
  const [editingPlot, setEditingPlot] = useState<Plot | null>(null);
  const [formData, setFormData] = useState<CreatePlotRequest>({
    farm_id: '',
    name: '',
    plot_number: '',
    area_hectares: undefined,
    elevation_meters: undefined,
    slope_degrees: undefined,
  });

  // Fetch plots
  const {
    data: plots,
    isLoading: plotsLoading,
    error: plotsError,
  } = useQuery({
    queryKey: ['plots'],
    queryFn: plotService.getPlots,
  });

  // Fetch farms for dropdown
  const { data: farms } = useQuery({
    queryKey: ['farms'],
    queryFn: farmService.getFarms,
  });

  // Create plot mutation
  const createMutation = useMutation({
    mutationFn: plotService.createPlot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plots'] });
      handleCloseDialog();
    },
  });

  // Update plot mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreatePlotRequest> }) =>
      plotService.updatePlot(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plots'] });
      handleCloseDialog();
    },
  });

  // Delete plot mutation
  const deleteMutation = useMutation({
    mutationFn: plotService.deletePlot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plots'] });
    },
  });

  const handleOpenDialog = (plot?: Plot) => {
    if (plot) {
      setEditingPlot(plot);
      setFormData({
        farm_id: plot.farm_id,
        name: plot.name,
        plot_number: plot.plot_number || '',
        area_hectares: plot.area_hectares,
        elevation_meters: plot.elevation_meters,
        slope_degrees: plot.slope_degrees,
      });
    } else {
      setEditingPlot(null);
      setFormData({
        farm_id: '',
        name: '',
        plot_number: '',
        area_hectares: undefined,
        elevation_meters: undefined,
        slope_degrees: undefined,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingPlot(null);
    setFormData({
      farm_id: '',
      name: '',
      plot_number: '',
      area_hectares: undefined,
      elevation_meters: undefined,
      slope_degrees: undefined,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingPlot) {
      const { farm_id, ...updateData } = formData;
      updateMutation.mutate({ id: editingPlot.id, data: updateData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this plot?')) {
      deleteMutation.mutate(id);
    }
  };

  const getFarmName = (farmId: string) => {
    const farm = farms?.find((f) => f.id === farmId);
    return farm?.name || 'Unknown Farm';
  };

  if (plotsLoading) return <Loading message="Loading plots..." />;
  if (plotsError) return <Alert severity="error">Error loading plots: {(plotsError as Error).message}</Alert>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Plots</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          disabled={!farms || farms.length === 0}
        >
          Add Plot
        </Button>
      </Box>

      {!farms || farms.length === 0 ? (
        <Alert severity="info">Please create a farm first before adding plots.</Alert>
      ) : plots && plots.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            No plots yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Get started by creating your first plot
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>
            Create First Plot
          </Button>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Plot Name</TableCell>
                <TableCell>Farm</TableCell>
                <TableCell>Plot Number</TableCell>
                <TableCell>Area (ha)</TableCell>
                <TableCell>Elevation (m)</TableCell>
                <TableCell>Slope (°)</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {plots?.map((plot) => (
                <TableRow key={plot.id}>
                  <TableCell>{plot.name}</TableCell>
                  <TableCell>{getFarmName(plot.farm_id)}</TableCell>
                  <TableCell>{plot.plot_number || 'N/A'}</TableCell>
                  <TableCell>{plot.area_hectares?.toFixed(2) || 'N/A'}</TableCell>
                  <TableCell>{plot.elevation_meters?.toFixed(1) || 'N/A'}</TableCell>
                  <TableCell>{plot.slope_degrees?.toFixed(1) || 'N/A'}</TableCell>
                  <TableCell>{format(new Date(plot.created_at), 'MMM d, yyyy')}</TableCell>
                  <TableCell align="right">
                    <IconButton onClick={() => handleOpenDialog(plot)} size="small">
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(plot.id)} size="small" color="error">
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>{editingPlot ? 'Edit Plot' : 'Create New Plot'}</DialogTitle>
          <DialogContent>
            <FormControl fullWidth margin="dense" sx={{ mb: 2 }} required>
              <InputLabel>Farm</InputLabel>
              <Select
                value={formData.farm_id}
                label="Farm"
                onChange={(e) => setFormData({ ...formData, farm_id: e.target.value })}
                disabled={!!editingPlot}
              >
                {farms?.map((farm) => (
                  <MenuItem key={farm.id} value={farm.id}>
                    {farm.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              autoFocus
              margin="dense"
              label="Plot Name"
              type="text"
              fullWidth
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Plot Number"
              type="text"
              fullWidth
              value={formData.plot_number}
              onChange={(e) => setFormData({ ...formData, plot_number: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Area (hectares)"
              type="number"
              fullWidth
              inputProps={{ step: '0.01', min: '0' }}
              value={formData.area_hectares || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  area_hectares: e.target.value ? parseFloat(e.target.value) : undefined,
                })
              }
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Elevation (meters)"
              type="number"
              fullWidth
              inputProps={{ step: '0.1', min: '0' }}
              value={formData.elevation_meters || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  elevation_meters: e.target.value ? parseFloat(e.target.value) : undefined,
                })
              }
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Slope (degrees)"
              type="number"
              fullWidth
              inputProps={{ step: '0.1', min: '0', max: '90' }}
              value={formData.slope_degrees || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  slope_degrees: e.target.value ? parseFloat(e.target.value) : undefined,
                })
              }
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {editingPlot ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}

export default Plots;

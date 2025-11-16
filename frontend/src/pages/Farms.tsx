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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import farmService from '../services/farmService';
import type { Farm } from '../types/farm';
import type { CreateFarmRequest } from '../types/api';
import Loading from '../components/common/Loading';

function Farms() {
  const queryClient = useQueryClient();
  const [openDialog, setOpenDialog] = useState(false);
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null);
  const [formData, setFormData] = useState<CreateFarmRequest>({
    name: '',
    address: '',
    total_area_hectares: undefined,
  });

  // Fetch farms
  const {
    data: farms,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['farms'],
    queryFn: farmService.getFarms,
  });

  // Create farm mutation
  const createMutation = useMutation({
    mutationFn: farmService.createFarm,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farms'] });
      handleCloseDialog();
    },
  });

  // Update farm mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: CreateFarmRequest }) =>
      farmService.updateFarm(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farms'] });
      handleCloseDialog();
    },
  });

  // Delete farm mutation
  const deleteMutation = useMutation({
    mutationFn: farmService.deleteFarm,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farms'] });
    },
  });

  const handleOpenDialog = (farm?: Farm) => {
    if (farm) {
      setEditingFarm(farm);
      setFormData({
        name: farm.name,
        address: farm.address || '',
        total_area_hectares: farm.total_area_hectares,
      });
    } else {
      setEditingFarm(null);
      setFormData({
        name: '',
        address: '',
        total_area_hectares: undefined,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingFarm(null);
    setFormData({
      name: '',
      address: '',
      total_area_hectares: undefined,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingFarm) {
      updateMutation.mutate({ id: editingFarm.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this farm?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <Loading message="Loading farms..." />;
  if (error) return <Alert severity="error">Error loading farms: {(error as Error).message}</Alert>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Farms</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Farm
        </Button>
      </Box>

      {farms && farms.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            No farms yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Get started by creating your first farm
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>
            Create First Farm
          </Button>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Address</TableCell>
                <TableCell>Area (ha)</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {farms?.map((farm) => (
                <TableRow key={farm.id}>
                  <TableCell>{farm.name}</TableCell>
                  <TableCell>{farm.address || 'N/A'}</TableCell>
                  <TableCell>{farm.total_area_hectares?.toFixed(2) || 'N/A'}</TableCell>
                  <TableCell>{format(new Date(farm.created_at), 'MMM d, yyyy')}</TableCell>
                  <TableCell align="right">
                    <IconButton onClick={() => handleOpenDialog(farm)} size="small">
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(farm.id)} size="small" color="error">
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
          <DialogTitle>{editingFarm ? 'Edit Farm' : 'Create New Farm'}</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Farm Name"
              type="text"
              fullWidth
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Address"
              type="text"
              fullWidth
              multiline
              rows={2}
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Total Area (hectares)"
              type="number"
              fullWidth
              inputProps={{ step: '0.01', min: '0' }}
              value={formData.total_area_hectares || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  total_area_hectares: e.target.value ? parseFloat(e.target.value) : undefined,
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
              {editingFarm ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}

export default Farms;

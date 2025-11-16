// API calls for plots

import apiClient from './api';
import type { Plot } from '../types/farm';
import type { CreatePlotRequest, UpdatePlotRequest } from '../types/api';

export const plotService = {
  // Get all plots
  getPlots: async (): Promise<Plot[]> => {
    const response = await apiClient.get<Plot[]>('/plots');
    return response.data;
  },

  // Get plots by farm ID
  getPlotsByFarmId: async (farmId: string): Promise<Plot[]> => {
    const response = await apiClient.get<Plot[]>(`/farms/${farmId}/plots`);
    return response.data;
  },

  // Get plot by ID
  getPlotById: async (id: string): Promise<Plot> => {
    const response = await apiClient.get<Plot>(`/plots/${id}`);
    return response.data;
  },

  // Create new plot
  createPlot: async (data: CreatePlotRequest): Promise<Plot> => {
    const response = await apiClient.post<Plot>('/plots', data);
    return response.data;
  },

  // Update plot
  updatePlot: async (id: string, data: UpdatePlotRequest): Promise<Plot> => {
    const response = await apiClient.put<Plot>(`/plots/${id}`, data);
    return response.data;
  },

  // Delete plot
  deletePlot: async (id: string): Promise<void> => {
    await apiClient.delete(`/plots/${id}`);
  },
};

export default plotService;

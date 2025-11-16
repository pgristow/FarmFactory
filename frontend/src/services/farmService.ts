// API calls for farms

import apiClient from './api';
import type { Farm } from '../types/farm';
import type { CreateFarmRequest, UpdateFarmRequest } from '../types/api';

export const farmService = {
  // Get all farms
  getFarms: async (): Promise<Farm[]> => {
    const response = await apiClient.get<Farm[]>('/farms');
    return response.data;
  },

  // Get farm by ID
  getFarmById: async (id: string): Promise<Farm> => {
    const response = await apiClient.get<Farm>(`/farms/${id}`);
    return response.data;
  },

  // Create new farm
  createFarm: async (data: CreateFarmRequest): Promise<Farm> => {
    const response = await apiClient.post<Farm>('/farms', data);
    return response.data;
  },

  // Update farm
  updateFarm: async (id: string, data: UpdateFarmRequest): Promise<Farm> => {
    const response = await apiClient.put<Farm>(`/farms/${id}`, data);
    return response.data;
  },

  // Delete farm
  deleteFarm: async (id: string): Promise<void> => {
    await apiClient.delete(`/farms/${id}`);
  },
};

export default farmService;

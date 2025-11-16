// API response types

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface CreateFarmRequest {
  name: string;
  address?: string;
  total_area_hectares?: number;
  timezone?: string;
  location?: {
    latitude: number;
    longitude: number;
  };
}

export interface UpdateFarmRequest {
  name?: string;
  address?: string;
  total_area_hectares?: number;
  timezone?: string;
  location?: {
    latitude: number;
    longitude: number;
  };
}

export interface CreatePlotRequest {
  farm_id: string;
  name: string;
  plot_number?: string;
  area_hectares?: number;
  elevation_meters?: number;
  slope_degrees?: number;
}

export interface UpdatePlotRequest {
  name?: string;
  plot_number?: string;
  area_hectares?: number;
  elevation_meters?: number;
  slope_degrees?: number;
}

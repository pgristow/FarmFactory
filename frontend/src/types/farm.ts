// Farm and Plot types matching backend models

export interface Farm {
  id: string;
  name: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  address?: string;
  total_area_hectares?: number;
  timezone?: string;
  created_at: string;
  updated_at: string;
}

export interface Plot {
  id: string;
  farm_id: string;
  name: string;
  plot_number?: string;
  area_hectares?: number;
  elevation_meters?: number;
  slope_degrees?: number;
  created_at: string;
  updated_at: string;
}

export interface SoilProfile {
  id: string;
  plot_id: string;
  soil_type?: string;
  ph_level?: number;
  organic_matter_percent?: number;
  texture?: string;
  drainage_class?: string;
  test_date?: string;
  notes?: string;
}

export interface Crop {
  id: string;
  name: string;
  scientific_name?: string;
  variety?: string;
  optimal_temp_min_celsius?: number;
  optimal_temp_max_celsius?: number;
  optimal_ph_min?: number;
  optimal_ph_max?: number;
  days_to_maturity?: number;
}

export interface Planting {
  id: string;
  plot_id: string;
  crop_id: string;
  planting_date: string;
  expected_harvest_date?: string;
  actual_harvest_date?: string;
  plant_population?: number;
  row_spacing_cm?: number;
  plant_spacing_cm?: number;
  status: 'planted' | 'growing' | 'harvested' | 'failed';
}

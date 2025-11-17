// Import system types

export type ImportStatus = 'pending' | 'uploading' | 'parsing' | 'validating' | 'processing' | 'completed' | 'failed' | 'cancelled';

export type DataType = 'farms_plots' | 'irrigation' | 'nutrients' | 'phenology' | 'financial';

export interface ImportJob {
  id: string;
  user_id: string;
  filename: string;
  file_type: string;
  data_type: DataType;
  status: ImportStatus;
  total_rows: number;
  processed_rows: number;
  error_count: number;
  started_at: string;
  completed_at?: string;
  metadata?: Record<string, any>;
}

export interface ImportError {
  id: string;
  import_job_id: string;
  row_number: number;
  column_name: string;
  error_type: string;
  error_message: string;
  invalid_value?: string;
  suggested_fix?: string;
  row_data?: Record<string, any>;
}

export interface ColumnMapping {
  source_column: string;
  target_field: string;
  confidence: number;
  data_type?: string;
  is_required?: boolean;
  ignore?: boolean;
}

export interface FileUploadResponse {
  job_id: string;
  filename: string;
  file_size: number;
  file_type: string;
  message: string;
}

export interface DataPreview {
  job_id: string;
  columns: string[];
  data_types: Record<string, string>;
  rows: Record<string, any>[];
  total_rows: number;
  preview_rows: number;
}

export interface ValidationResult {
  job_id: string;
  valid_rows: number;
  invalid_rows: number;
  total_rows: number;
  errors: ImportError[];
  error_summary: Record<string, number>;
  can_proceed: boolean;
}

export interface ImportProgress {
  job_id: string;
  status: ImportStatus;
  processed_rows: number;
  total_rows: number;
  progress_percentage: number;
  current_step: string;
  elapsed_time: number;
  estimated_time_remaining?: number;
  error_message?: string;
}

export interface ImportHistoryFilter {
  status?: ImportStatus;
  data_type?: DataType;
  start_date?: string;
  end_date?: string;
}

export interface ImportHistoryResponse {
  jobs: ImportJob[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ImportTemplate {
  id: string;
  name: string;
  data_type: DataType;
  description: string;
  column_mapping: ColumnMapping[];
  is_default: boolean;
}

export interface ColumnMappingRequest {
  job_id: string;
  data_type: DataType;
  mappings: ColumnMapping[];
  save_as_template?: boolean;
  template_name?: string;
}

export interface ProcessImportRequest {
  job_id: string;
  skip_invalid_rows: boolean;
  column_mapping: ColumnMapping[];
}

export interface ErrorExport {
  row_number: number;
  column_name: string;
  error_type: string;
  error_message: string;
  invalid_value: string;
}

export const DATA_TYPE_LABELS: Record<DataType, string> = {
  farms_plots: 'Farms & Plots',
  irrigation: 'Irrigation Events',
  nutrients: 'Nutrient Applications',
  phenology: 'Phenology Observations',
  financial: 'Financial Data',
};

export const STATUS_LABELS: Record<ImportStatus, string> = {
  pending: 'Pending',
  uploading: 'Uploading',
  parsing: 'Parsing',
  validating: 'Validating',
  processing: 'Processing',
  completed: 'Completed',
  failed: 'Failed',
  cancelled: 'Cancelled',
};

export const STATUS_COLORS: Record<ImportStatus, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
  pending: 'default',
  uploading: 'info',
  parsing: 'info',
  validating: 'info',
  processing: 'primary',
  completed: 'success',
  failed: 'error',
  cancelled: 'warning',
};

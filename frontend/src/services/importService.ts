import api from './api';
import {
  FileUploadResponse,
  DataPreview,
  ValidationResult,
  ImportProgress,
  ImportHistoryResponse,
  ImportHistoryFilter,
  ImportJob,
  ImportError,
  ImportTemplate,
  ColumnMappingRequest,
  ProcessImportRequest,
  DataType,
} from '../types/import';

/**
 * Upload a file for import
 */
export const uploadFile = async (file: File, dataType: DataType): Promise<FileUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('data_type', dataType);

  const response = await api.post<FileUploadResponse>('/api/v1/import/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Get data preview with column information
 */
export const getPreview = async (jobId: string): Promise<DataPreview> => {
  const response = await api.get<DataPreview>(`/api/v1/import/preview/${jobId}`);
  return response.data;
};

/**
 * Get auto-detected column mappings
 */
export const getColumnMappings = async (jobId: string, dataType: DataType) => {
  const response = await api.post('/api/v1/import/map-columns', {
    job_id: jobId,
    data_type: dataType,
  });
  return response.data;
};

/**
 * Validate import with column mappings
 */
export const validateImport = async (data: ColumnMappingRequest): Promise<ValidationResult> => {
  const response = await api.post<ValidationResult>('/api/v1/import/validate', data);
  return response.data;
};

/**
 * Process the import
 */
export const processImport = async (data: ProcessImportRequest): Promise<{ job_id: string; message: string }> => {
  const response = await api.post('/api/v1/import/process', data);
  return response.data;
};

/**
 * Get import status and progress
 */
export const getImportStatus = async (jobId: string): Promise<ImportProgress> => {
  const response = await api.get<ImportProgress>(`/api/v1/import/status/${jobId}`);
  return response.data;
};

/**
 * Get import history with filters and pagination
 */
export const getImportHistory = async (
  page: number = 1,
  pageSize: number = 20,
  filters?: ImportHistoryFilter
): Promise<ImportHistoryResponse> => {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  if (filters?.status) {
    params.append('status', filters.status);
  }
  if (filters?.data_type) {
    params.append('data_type', filters.data_type);
  }
  if (filters?.start_date) {
    params.append('start_date', filters.start_date);
  }
  if (filters?.end_date) {
    params.append('end_date', filters.end_date);
  }

  const response = await api.get<ImportHistoryResponse>(`/api/v1/import/history?${params.toString()}`);
  return response.data;
};

/**
 * Get errors for a specific import job
 */
export const getImportErrors = async (jobId: string): Promise<ImportError[]> => {
  const response = await api.get<ImportError[]>(`/api/v1/import/${jobId}/errors`);
  return response.data;
};

/**
 * Get a specific import job details
 */
export const getImportJob = async (jobId: string): Promise<ImportJob> => {
  const response = await api.get<ImportJob>(`/api/v1/import/${jobId}`);
  return response.data;
};

/**
 * Cancel an ongoing import
 */
export const cancelImport = async (jobId: string): Promise<{ message: string }> => {
  const response = await api.delete(`/api/v1/import/${jobId}`);
  return response.data;
};

/**
 * Get available import templates
 */
export const getTemplates = async (dataType?: DataType): Promise<ImportTemplate[]> => {
  const params = dataType ? `?data_type=${dataType}` : '';
  const response = await api.get<ImportTemplate[]>(`/api/v1/import/templates${params}`);
  return response.data;
};

/**
 * Download CSV template for a data type
 */
export const downloadTemplate = async (dataType: DataType): Promise<Blob> => {
  const response = await api.get(`/api/v1/import/templates/${dataType}/download`, {
    responseType: 'blob',
  });
  return response.data;
};

/**
 * Export errors as CSV
 */
export const exportErrors = async (jobId: string): Promise<Blob> => {
  const response = await api.get(`/api/v1/import/${jobId}/errors/export`, {
    responseType: 'blob',
  });
  return response.data;
};

/**
 * Save column mapping as template
 */
export const saveTemplate = async (
  name: string,
  dataType: DataType,
  mappings: any[]
): Promise<ImportTemplate> => {
  const response = await api.post<ImportTemplate>('/api/v1/import/templates', {
    name,
    data_type: dataType,
    column_mapping: mappings,
  });
  return response.data;
};

/**
 * Delete import history
 */
export const deleteImportJob = async (jobId: string): Promise<void> => {
  await api.delete(`/api/v1/import/${jobId}`);
};

const importService = {
  uploadFile,
  getPreview,
  getColumnMappings,
  validateImport,
  processImport,
  getImportStatus,
  getImportHistory,
  getImportErrors,
  getImportJob,
  cancelImport,
  getTemplates,
  downloadTemplate,
  exportErrors,
  saveTemplate,
  deleteImportJob,
};

export default importService;

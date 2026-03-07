/**
 * API 服务层 - Axios 实例与后端接口封装
 * 腐蚀与应力在线监测平台 V2.0
 */

import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios';
import type {
  ApiResponse,
  Waveform,
  SpectrumData,
  Defect,
  ModelMetrics,
  TrainingStatus,
  TrainingConfig,
  InferenceEngineStatus,
  LatencyRecord,
  DataImportResult,
  AuditLogEntry,
  AuditLogFilter,
  PaginatedResponse,
  LoginRequest,
  LoginResponse,
} from '@/types/api';

const API_BASE = '/api';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加 JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ 数据可视化 ============
export const dataVisualizationApi = {
  getWaveform: (id: string) =>
    api.get<ApiResponse<Waveform>>(`/data/waveform/${id}`),

  getSpectrum: (id: string) =>
    api.get<ApiResponse<SpectrumData>>(`/data/spectrum/${id}`),

  computeSpectrum: (waveformId: string) =>
    api.post<ApiResponse<SpectrumData>>(`/data/spectrum/compute`, { waveformId }),

  listWaveforms: (params?: { page?: number; pageSize?: number }) =>
    api.get<ApiResponse<PaginatedResponse<Waveform>>>(`/data/waveforms`, { params }),
};

// ============ 数据导入 ============
export const dataImportApi = {
  uploadFile: (file: File, config?: AxiosRequestConfig) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<ApiResponse<DataImportResult>>(`/data/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      ...config,
    });
  },
};

// ============ 模型训练 ============
export const trainingApi = {
  startTraining: (config: TrainingConfig) =>
    api.post<ApiResponse<{ jobId: string }>>(`/training/start`, config),

  stopTraining: (jobId: string) =>
    api.post<ApiResponse<void>>(`/training/stop`, { jobId }),

  getTrainingStatus: (jobId: string) =>
    api.get<ApiResponse<TrainingStatus>>(`/training/status/${jobId}`),

  getMetrics: (runId?: string) =>
    api.get<ApiResponse<ModelMetrics[]>>(`/training/metrics`, { params: { runId } }),

  listRuns: (params?: { limit?: number }) =>
    api.get<ApiResponse<{ runId: string; name: string; createdAt: string }[]>>(
      `/training/runs`,
      { params }
    ),
};

// ============ 推理监控 ============
export const inferenceApi = {
  getEngineStatus: () =>
    api.get<ApiResponse<InferenceEngineStatus[]>>(`/inference/status`),

  getLatencyHistory: (params?: { limit?: number; engine?: string }) =>
    api.get<ApiResponse<LatencyRecord[]>>(`/inference/latency`, { params }),

  healthCheck: () => api.get<ApiResponse<{ status: string }>>(`/inference/health`),
};

// ============ 缺陷分析 ============
export const defectAnalysisApi = {
  uploadCScan: (file: File, config?: AxiosRequestConfig) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<ApiResponse<{ imageId: string; defects: Defect[] }>>(
      `/defect/analyze`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
        ...config,
      }
    );
  },

  getDefects: (imageId: string) =>
    api.get<ApiResponse<Defect[]>>(`/defect/list/${imageId}`),

  getOverlayImage: (imageId: string) =>
    api.get<Blob>(`/defect/overlay/${imageId}`, { responseType: 'blob' }),
};

// ============ 认证 ============
export const authApi = {
  login: (data: LoginRequest) =>
    api.post<ApiResponse<LoginResponse>>(`/auth/login`, data),

  logout: () => api.post<ApiResponse<void>>(`/auth/logout`),

  refreshToken: () =>
    api.post<ApiResponse<{ accessToken: string; expiresIn: number }>>(`/auth/refresh`),

  getCurrentUser: () =>
    api.get<ApiResponse<LoginResponse['user']>>(`/auth/me`),
};

// ============ 审计日志 ============
export const auditApi = {
  getLogs: (filter: AuditLogFilter) =>
    api.get<ApiResponse<PaginatedResponse<AuditLogEntry>>>(`/audit/logs`, {
      params: filter,
    }),

  exportLogs: (filter: AuditLogFilter) =>
    api.get<Blob>(`/audit/export`, {
      params: filter,
      responseType: 'blob',
    }),
};

export default api;

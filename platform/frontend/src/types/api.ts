/**
 * API 响应与业务数据类型定义
 * 腐蚀与应力在线监测平台 V2.0
 */

// ============ 通用 ============
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// ============ 波形与信号 ============
export interface Waveform {
  id: string;
  time: number[];
  amplitude: number[];
  samplingRate: number;
  channel?: string;
  metadata?: Record<string, unknown>;
}

export interface SpectrumData {
  id: string;
  frequency: number[];
  magnitude: number[];
  phase?: number[];
  samplingRate: number;
}

// ============ 缺陷 ============
export type DefectType = 'bubble' | 'weak_bond' | 'disbond' | 'normal';

export type DefectSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface Defect {
  id: string;
  area: number;
  centroid: { x: number; y: number };
  type: DefectType;
  severity: DefectSeverity;
  confidence: number;
  boundingBox?: { x: number; y: number; width: number; height: number };
  mask?: number[][];
}

// ============ 模型训练 ============
export type ModelType = 'linear_regression' | 'svr' | 'random_forest' | 'xgboost' | 'lightgbm' | 'cnn_1d';

export interface ModelMetrics {
  modelName: string;
  modelType: ModelType;
  mae: number;
  rmse: number;
  r2: number;
  mape: number;
  trainingTime?: number;
}

export interface TrainingStatus {
  jobId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  currentEpoch?: number;
  totalEpochs?: number;
  message?: string;
  startedAt?: string;
  completedAt?: string;
}

export interface TrainingConfig {
  modelType: ModelType;
  trainTestSplit?: number;
  epochs?: number;
  batchSize?: number;
  learningRate?: number;
}

// ============ 推理 ============
export type InferenceEngineType = 'onnx' | 'torchserve';

export interface InferenceEngineStatus {
  engine: InferenceEngineType;
  status: 'online' | 'offline' | 'degraded';
  latencyMs?: number;
  throughput?: number;
  modelLoaded?: string;
  lastHealthCheck?: string;
}

export interface LatencyRecord {
  timestamp: string;
  latencyMs: number;
  engine: InferenceEngineType;
}

// ============ 数据导入 ============
export interface DataImportResult {
  success: boolean;
  fileId: string;
  recordCount: number;
  format: 'csv' | 'hdf5' | 'mat';
  errors?: string[];
}

// ============ 审计 ============
export interface AuditLogEntry {
  id: string;
  userId: string;
  username: string;
  action: string;
  resource: string;
  details?: string;
  ipAddress?: string;
  timestamp: string;
  success: boolean;
}

export interface AuditLogFilter {
  userId?: string;
  action?: string;
  resource?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
}

// ============ 认证 ============
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken?: string;
  expiresIn: number;
  user: {
    id: string;
    username: string;
    role: string;
    displayName?: string;
  };
}

export interface UserInfo {
  id: string;
  username: string;
  role: string;
  displayName?: string;
  email?: string;
}

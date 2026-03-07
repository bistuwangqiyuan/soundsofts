import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import Loading from '@/components/common/Loading';
import { Suspense, lazy } from 'react';

// 懒加载各模块
const WaveformViewer = lazy(() => import('@/modules/data-visualization/WaveformViewer'));
const SpectrumViewer = lazy(() => import('@/modules/data-visualization/SpectrumViewer'));
const DataImporter = lazy(() => import('@/modules/data-visualization/DataImporter'));
const TrainingDashboard = lazy(() => import('@/modules/model-training/TrainingDashboard'));
const InferenceStatus = lazy(() => import('@/modules/inference-monitor/InferenceStatus'));
const CScanUploader = lazy(() => import('@/modules/defect-analysis/CScanUploader'));
const DefectTable = lazy(() => import('@/modules/defect-analysis/DefectTable'));
const LoginPage = lazy(() => import('@/modules/admin/LoginPage'));
const AuditLog = lazy(() => import('@/modules/admin/AuditLog'));

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={
        <Suspense fallback={<Loading fullScreen />}>
          <LoginPage />
        </Suspense>
      } />
      <Route path="/" element={
        <ProtectedRoute>
          <AppLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/data/waveform" replace />} />
        <Route path="data">
          <Route path="waveform" element={
            <Suspense fallback={<Loading />}>
              <WaveformViewer />
            </Suspense>
          } />
          <Route path="spectrum" element={
            <Suspense fallback={<Loading />}>
              <SpectrumViewer />
            </Suspense>
          } />
          <Route path="import" element={
            <Suspense fallback={<Loading />}>
              <DataImporter />
            </Suspense>
          } />
        </Route>
        <Route path="training" element={
          <Suspense fallback={<Loading />}>
            <TrainingDashboard />
          </Suspense>
        } />
        <Route path="inference" element={
          <Suspense fallback={<Loading />}>
            <InferenceStatus />
          </Suspense>
        } />
        <Route path="defect">
          <Route path="cscan" element={
            <Suspense fallback={<Loading />}>
              <CScanUploader />
            </Suspense>
          } />
          <Route path="list" element={
            <Suspense fallback={<Loading />}>
              <DefectTable />
            </Suspense>
          } />
        </Route>
        <Route path="admin">
          <Route path="audit" element={
            <Suspense fallback={<Loading />}>
              <AuditLog />
            </Suspense>
          } />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;

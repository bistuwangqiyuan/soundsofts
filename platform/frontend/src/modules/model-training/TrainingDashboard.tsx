import { useState, useEffect } from 'react';
import { Card, Button, Space, Select, Progress, message, Row, Col } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import { trainingApi } from '@/services/api';
import RadarChart from '@/components/charts/RadarChart';
import MetricsChart from './MetricsChart';
import type { ModelMetrics, ModelType, TrainingStatus } from '@/types/api';

const MODEL_OPTIONS: { value: ModelType; label: string }[] = [
  { value: 'linear_regression', label: '线性回归' },
  { value: 'svr', label: 'SVR' },
  { value: 'random_forest', label: '随机森林' },
  { value: 'xgboost', label: 'XGBoost' },
  { value: 'lightgbm', label: 'LightGBM' },
  { value: 'cnn_1d', label: '1D-CNN' },
];

function TrainingDashboard() {
  const [selectedModel, setSelectedModel] = useState<ModelType>('random_forest');
  const [status, setStatus] = useState<TrainingStatus | null>(null);
  const [metrics, setMetrics] = useState<ModelMetrics[]>([]);
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);

  const fetchMetrics = () => {
    trainingApi
      .getMetrics()
      .then((res) => setMetrics(res.data.data ?? []))
      .catch(() => setMetrics([]));
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  useEffect(() => {
    if (!polling || !status?.jobId) return;
    const timer = setInterval(() => {
      trainingApi
        .getTrainingStatus(status.jobId)
        .then((res) => {
          const s = res.data.data as TrainingStatus | undefined;
          setStatus(s ?? null);
          if (s?.status === 'completed' || s?.status === 'failed') {
            setPolling(false);
            fetchMetrics();
          }
        })
        .catch(() => setPolling(false));
    }, 2000);
    return () => clearInterval(timer);
  }, [polling, status?.jobId]);

  const handleStart = () => {
    setLoading(true);
    trainingApi
      .startTraining({ modelType: selectedModel })
      .then((res) => {
        const jobId = res.data.data?.jobId;
        if (jobId) {
          setStatus({
            jobId,
            status: 'running',
            progress: 0,
          });
          setPolling(true);
          message.success('训练已启动');
        }
      })
      .catch(() => message.error('启动训练失败'))
      .finally(() => setLoading(false));
  };

  const handleStop = () => {
    if (!status?.jobId) return;
    trainingApi
      .stopTraining(status.jobId)
      .then(() => {
        setPolling(false);
        setStatus((s) => (s ? { ...s, status: 'failed', message: '已停止' } : null));
        message.info('训练已停止');
      })
      .catch(() => message.error('停止失败'));
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card title="训练控制台">
        <Row gutter={24} align="middle">
          <Col>
            <Space>
              <span>模型类型：</span>
              <Select
                value={selectedModel}
                onChange={setSelectedModel}
                options={MODEL_OPTIONS}
                style={{ width: 160 }}
                disabled={polling}
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleStart}
                loading={loading}
                disabled={polling}
              >
                启动训练
              </Button>
              <Button
                danger
                icon={<PauseCircleOutlined />}
                onClick={handleStop}
                disabled={!polling}
              >
                停止训练
              </Button>
            </Space>
          </Col>
        </Row>
        {status && (
          <div style={{ marginTop: 16 }}>
            <Progress
              percent={status.progress}
              status={status.status === 'failed' ? 'exception' : status.status === 'completed' ? 'success' : 'active'}
            />
            <div style={{ marginTop: 8, color: '#666', fontSize: 12 }}>
              {status.message ?? `状态: ${status.status}`}
              {status.currentEpoch != null && status.totalEpochs != null && (
                <> | Epoch {status.currentEpoch}/{status.totalEpochs}</>
              )}
            </div>
          </div>
        )}
      </Card>

      <Row gutter={24}>
        <Col span={12}>
          <Card title="MAE / RMSE 对比">
            {metrics.length > 0 ? (
              <MetricsChart data={metrics} />
            ) : (
              <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
                暂无训练指标，请先完成训练
              </div>
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="模型综合性能雷达图">
            {metrics.length > 0 ? (
              <RadarChart data={metrics} height={300} />
            ) : (
              <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
                暂无数据
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </Space>
  );
}

export default TrainingDashboard;

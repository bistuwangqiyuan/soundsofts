import { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Tag, Space, message } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, WarningOutlined } from '@ant-design/icons';
import { inferenceApi } from '@/services/api';
import LatencyChart from './LatencyChart';
import Loading from '@/components/common/Loading';
import type { InferenceEngineStatus } from '@/types/api';

const STATUS_MAP = {
  online: { color: 'success', icon: <CheckCircleOutlined />, text: '在线' },
  offline: { color: 'error', icon: <CloseCircleOutlined />, text: '离线' },
  degraded: { color: 'warning', icon: <WarningOutlined />, text: '降级' },
};

function InferenceStatus() {
  const [engines, setEngines] = useState<InferenceEngineStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    inferenceApi
      .getEngineStatus()
      .then((res) => setEngines(res.data.data ?? []))
      .catch(() => {
        message.error('获取推理引擎状态失败');
        setEngines([]);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card title="推理引擎状态">
        <Row gutter={24}>
          {engines.length > 0 ? (
            engines.map((e: InferenceEngineStatus) => {
              const s = STATUS_MAP[e.status as keyof typeof STATUS_MAP] ?? STATUS_MAP.offline;
              return (
                <Col key={e.engine} span={12}>
                  <Card size="small">
                    <Statistic
                      title={
                        <Space>
                          <Tag color={s.color} icon={s.icon}>
                            {s.text}
                          </Tag>
                          <span>{e.engine === 'onnx' ? 'ONNX Runtime' : 'TorchServe'}</span>
                        </Space>
                      }
                      value={e.latencyMs != null ? `${e.latencyMs.toFixed(2)} ms` : '-'}
                      suffix={e.throughput != null ? `(${e.throughput} req/s)` : ''}
                    />
                    {e.modelLoaded && (
                      <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                        已加载: {e.modelLoaded}
                      </div>
                    )}
                  </Card>
                </Col>
              );
            })
          ) : (
            <Col span={24}>
              <div style={{ padding: 24, textAlign: 'center', color: '#999' }}>
                暂无推理引擎状态数据
              </div>
            </Col>
          )}
        </Row>
      </Card>

      <Card title="实时延迟监控">
        <LatencyChart height={320} />
      </Card>
    </Space>
  );
}

export default InferenceStatus;

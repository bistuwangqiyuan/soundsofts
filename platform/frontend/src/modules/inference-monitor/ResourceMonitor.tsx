import { Card, Row, Col, Progress, Statistic, Typography, Space } from 'antd';
import { CpuOutlined, DatabaseOutlined, ThunderboltOutlined } from '@ant-design/icons';

const { Text } = Typography;

export interface ResourceUsage {
  gpu?: {
    utilization: number;
    memoryUsed: number;
    memoryTotal: number;
    temperature?: number;
  };
  cpu: number;
  memory: {
    used: number;
    total: number;
  };
}

interface ResourceMonitorProps {
  usage: ResourceUsage;
  loading?: boolean;
}

function ResourceMonitor({ usage, loading = false }: ResourceMonitorProps) {
  const gpuMemPercent =
    usage.gpu && usage.gpu.memoryTotal > 0
      ? (usage.gpu.memoryUsed / usage.gpu.memoryTotal) * 100
      : 0;
  const memPercent =
    usage.memory.total > 0
      ? (usage.memory.used / usage.memory.total) * 100
      : 0;

  return (
    <Card title="资源监控" loading={loading}>
      <Row gutter={[24, 24]}>
        {usage.gpu && (
          <Col xs={24} sm={12} md={8}>
            <Card size="small">
              <Statistic
                title={
                  <Space>
                    <ThunderboltOutlined />
                    <Text>GPU 利用率</Text>
                  </Space>
                }
                value={usage.gpu.utilization}
                suffix="%"
              />
              <Progress
                percent={usage.gpu.utilization}
                strokeColor={{
                  '0%': '#52c41a',
                  '70%': '#faad14',
                  '100%': '#ff4d4f',
                }}
                showInfo={false}
                style={{ marginTop: 8 }}
              />
              <Text type="secondary" style={{ fontSize: 12 }}>
                显存: {(usage.gpu.memoryUsed / 1024).toFixed(1)} / {(usage.gpu.memoryTotal / 1024).toFixed(1)} GB
              </Text>
              {usage.gpu.temperature != null && (
                <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>
                  {usage.gpu.temperature}°C
                </Text>
              )}
            </Card>
          </Col>
        )}
        <Col xs={24} sm={12} md={8}>
          <Card size="small">
            <Statistic
              title={
                <Space>
                  <CpuOutlined />
                  <Text>CPU 利用率</Text>
                </Space>
              }
              value={usage.cpu}
              suffix="%"
            />
            <Progress
              percent={usage.cpu}
              strokeColor={{
                '0%': '#52c41a',
                '70%': '#faad14',
                '100%': '#ff4d4f',
              }}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card size="small">
            <Statistic
              title={
                <Space>
                  <DatabaseOutlined />
                  <Text>内存使用</Text>
                </Space>
              }
              value={memPercent.toFixed(1)}
              suffix="%"
            />
            <Progress
              percent={memPercent}
              strokeColor={{
                '0%': '#52c41a',
                '70%': '#faad14',
                '100%': '#ff4d4f',
              }}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {(usage.memory.used / 1024 / 1024 / 1024).toFixed(2)} / {(usage.memory.total / 1024 / 1024 / 1024).toFixed(2)} GB
            </Text>
          </Card>
        </Col>
      </Row>
    </Card>
  );
}

export default ResourceMonitor;

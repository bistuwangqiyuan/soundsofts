import { Card, Progress, Row, Col, Statistic, Space, Typography } from 'antd';
import {
  SoundOutlined,
  LineChartOutlined,
  CheckCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

export interface QualityMetrics {
  snr: number;
  baselineDrift: number;
  signalIntegrity?: number;
  noiseFloor?: number;
  overallScore?: number;
}

interface QualityScoringProps {
  metrics: QualityMetrics;
  loading?: boolean;
}

const SNR_THRESHOLD_GOOD = 20;
const SNR_THRESHOLD_WARN = 10;
const DRIFT_THRESHOLD_GOOD = 0.05;
const DRIFT_THRESHOLD_WARN = 0.15;

function getScoreColor(score: number, inverse = false): string {
  if (inverse) {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    return '#ff4d4f';
  }
  if (score >= 80) return '#52c41a';
  if (score >= 60) return '#faad14';
  return '#ff4d4f';
}

function QualityScoring({ metrics, loading = false }: QualityScoringProps) {
  const snrScore = Math.min(100, (metrics.snr / SNR_THRESHOLD_GOOD) * 50);
  const driftScore = Math.max(
    0,
    100 - (metrics.baselineDrift / DRIFT_THRESHOLD_WARN) * 100
  );
  const overall =
    metrics.overallScore ??
    Math.round((snrScore * 0.5 + driftScore * 0.5));

  return (
    <Card title="数据质量评分" loading={loading}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Row gutter={[24, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Statistic
              title="综合评分"
              value={overall}
              suffix="/ 100"
              valueStyle={{
                color: getScoreColor(overall),
                fontSize: 28,
              }}
            />
          </Col>
        </Row>

        <div>
          <Space style={{ marginBottom: 8 }}>
            <SoundOutlined />
            <Text strong>信噪比 (SNR)</Text>
            <Text type="secondary">
              {metrics.snr >= SNR_THRESHOLD_GOOD ? (
                <><CheckCircleOutlined style={{ color: '#52c41a' }} /> 良好</>
              ) : metrics.snr >= SNR_THRESHOLD_WARN ? (
                <><WarningOutlined style={{ color: '#faad14' }} /> 一般</>
              ) : (
                <><WarningOutlined style={{ color: '#ff4d4f' }} /> 较差</>
              )}
            </Text>
          </Space>
          <Progress
            percent={snrScore}
            strokeColor={getScoreColor(snrScore)}
            showInfo
            format={(p) => `${metrics.snr.toFixed(1)} dB`}
          />
        </div>

        <div>
          <Space style={{ marginBottom: 8 }}>
            <LineChartOutlined />
            <Text strong>基线漂移</Text>
            <Text type="secondary">
              {metrics.baselineDrift <= DRIFT_THRESHOLD_GOOD ? (
                <><CheckCircleOutlined style={{ color: '#52c41a' }} /> 良好</>
              ) : metrics.baselineDrift <= DRIFT_THRESHOLD_WARN ? (
                <><WarningOutlined style={{ color: '#faad14' }} /> 一般</>
              ) : (
                <><WarningOutlined style={{ color: '#ff4d4f' }} /> 较差</>
              )}
            </Text>
          </Space>
          <Progress
            percent={driftScore}
            strokeColor={getScoreColor(driftScore)}
            showInfo
            format={(p) => `${(metrics.baselineDrift * 100).toFixed(2)}%`}
          />
        </div>

        {(metrics.signalIntegrity != null || metrics.noiseFloor != null) && (
          <Row gutter={[16, 16]}>
            {metrics.signalIntegrity != null && (
              <Col span={12}>
                <Statistic
                  title="信号完整性"
                  value={metrics.signalIntegrity}
                  precision={2}
                  suffix="%"
                />
              </Col>
            )}
            {metrics.noiseFloor != null && (
              <Col span={12}>
                <Statistic
                  title="噪声底"
                  value={metrics.noiseFloor}
                  precision={2}
                  suffix="dB"
                />
              </Col>
            )}
          </Row>
        )}
      </Space>
    </Card>
  );
}

export default QualityScoring;

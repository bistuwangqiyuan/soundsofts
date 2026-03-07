import { Card, Row, Col, Statistic, Typography, Descriptions } from 'antd';
import { LineChartOutlined } from '@ant-design/icons';

const { Text } = Typography;

export interface CorrelationResult {
  pearson: number;
  spearman: number;
  pValuePearson?: number;
  pValueSpearman?: number;
  sampleCount?: number;
}

interface CorrelationAnalysisProps {
  result: CorrelationResult;
  loading?: boolean;
}

function CorrelationAnalysis({ result, loading = false }: CorrelationAnalysisProps) {
  const getStrength = (r: number): { text: string; color: string } => {
    const abs = Math.abs(r);
    if (abs >= 0.9) return { text: '极强', color: '#52c41a' };
    if (abs >= 0.7) return { text: '强', color: '#73d13d' };
    if (abs >= 0.5) return { text: '中等', color: '#faad14' };
    if (abs >= 0.3) return { text: '弱', color: '#fa8c16' };
    return { text: '极弱', color: '#ff4d4f' };
  };

  const pearsonStrength = getStrength(result.pearson);
  const spearmanStrength = getStrength(result.spearman);

  return (
    <Card
      title={
        <span>
          <LineChartOutlined style={{ marginRight: 8 }} />
          相关性分析
        </span>
      }
      loading={loading}
    >
      <Row gutter={[24, 24]}>
        <Col xs={24} sm={12}>
          <Card size="small">
            <Statistic
              title="Pearson 相关系数"
              value={result.pearson}
              precision={4}
              valueStyle={{ color: pearsonStrength.color }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              线性相关强度: {pearsonStrength.text}
            </Text>
            {result.pValuePearson != null && (
              <div style={{ marginTop: 4 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  p-value: {result.pValuePearson.toExponential(2)}
                </Text>
              </div>
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card size="small">
            <Statistic
              title="Spearman 相关系数"
              value={result.spearman}
              precision={4}
              valueStyle={{ color: spearmanStrength.color }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              秩相关强度: {spearmanStrength.text}
            </Text>
            {result.pValueSpearman != null && (
              <div style={{ marginTop: 4 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  p-value: {result.pValueSpearman.toExponential(2)}
                </Text>
              </div>
            )}
          </Card>
        </Col>
      </Row>
      {result.sampleCount != null && (
        <Descriptions size="small" column={1} style={{ marginTop: 16 }}>
          <Descriptions.Item label="样本数">{result.sampleCount}</Descriptions.Item>
        </Descriptions>
      )}
    </Card>
  );
}

export default CorrelationAnalysis;

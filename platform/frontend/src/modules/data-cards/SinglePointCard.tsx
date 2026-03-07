import { Card, Tag, Typography, Space } from 'antd';
import type { DefectType } from '@/types/api';

const { Text } = Typography;

export interface SinglePointData {
  id: string;
  specimenId: string;
  coordinates: { x: number; y: number };
  defectLabel: DefectType;
  predictedForce: number;
  waveformThumbnail?: number[];
  actualForce?: number;
  error?: number;
}

interface SinglePointCardProps {
  data: SinglePointData;
  onClick?: () => void;
}

const DEFECT_LABELS: Record<DefectType, string> = {
  bubble: '气泡',
  weak_bond: '弱粘接',
  disbond: '脱粘',
  normal: '正常',
};

const DEFECT_COLORS: Record<DefectType, string> = {
  bubble: 'red',
  weak_bond: 'orange',
  disbond: 'volcano',
  normal: 'green',
};

function SinglePointCard({ data, onClick }: SinglePointCardProps) {
  const WaveformThumbnail = () => {
    if (!data.waveformThumbnail || data.waveformThumbnail.length === 0) {
      return (
        <div
          style={{
            height: 60,
            background: '#f5f5f5',
            borderRadius: 4,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#999',
            fontSize: 12,
          }}
        >
          无波形
        </div>
      );
    }
    const max = Math.max(...data.waveformThumbnail);
    const min = Math.min(...data.waveformThumbnail);
    const range = max - min || 1;
    const points = data.waveformThumbnail
      .map((v, i) => {
        const x = (i / (data.waveformThumbnail!.length - 1 || 1)) * 100;
        const y = 100 - ((v - min) / range) * 100;
        return `${x},${y}`;
      })
      .join(' ');

    return (
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        style={{ height: 60, width: '100%', display: 'block' }}
      >
        <polyline
          points={points}
          fill="none"
          stroke="#1677ff"
          strokeWidth="0.5"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
    );
  };

  return (
    <Card
      size="small"
      hoverable
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <WaveformThumbnail />
        <Space wrap>
          <Text type="secondary">试样:</Text>
          <Text strong>{data.specimenId}</Text>
        </Space>
        <Space wrap>
          <Text type="secondary">坐标:</Text>
          <Text>
            ({data.coordinates.x.toFixed(2)}, {data.coordinates.y.toFixed(2)})
          </Text>
        </Space>
        <Space wrap>
          <Text type="secondary">缺陷:</Text>
          <Tag color={DEFECT_COLORS[data.defectLabel]}>
            {DEFECT_LABELS[data.defectLabel]}
          </Tag>
        </Space>
        <Space wrap>
          <Text type="secondary">预测力:</Text>
          <Text strong>{data.predictedForce.toFixed(3)} N</Text>
        </Space>
        {data.actualForce != null && (
          <Space wrap>
            <Text type="secondary">实际力:</Text>
            <Text>{data.actualForce.toFixed(3)} N</Text>
          </Space>
        )}
        {data.error != null && (
          <Space wrap>
            <Text type="secondary">误差:</Text>
            <Tag color={Math.abs(data.error) > 0.5 ? 'red' : 'default'}>
              {data.error > 0 ? '+' : ''}
              {data.error.toFixed(3)} N
            </Tag>
          </Space>
        )}
      </Space>
    </Card>
  );
}

export default SinglePointCard;

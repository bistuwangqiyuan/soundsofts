import { Card, List, Tag, Typography, Space, Button } from 'antd';
import { BellOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';

const { Text } = Typography;

export interface AlertItem {
  id: string;
  type: 'latency' | 'memory' | 'error_rate' | 'throughput';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  value?: number;
  threshold?: number;
  timestamp: string;
  acknowledged?: boolean;
}

interface AlertPanelProps {
  alerts: AlertItem[];
  onAcknowledge?: (id: string) => void;
  onDismiss?: (id: string) => void;
  onAcknowledgeAll?: () => void;
}

const SEVERITY_MAP = {
  info: { color: 'blue', text: '信息' },
  warning: { color: 'orange', text: '警告' },
  critical: { color: 'red', text: '严重' },
};

const TYPE_MAP = {
  latency: '延迟',
  memory: '内存',
  error_rate: '错误率',
  throughput: '吞吐量',
};

function AlertPanel({
  alerts,
  onAcknowledge,
  onDismiss,
  onAcknowledgeAll,
}: AlertPanelProps) {
  const unackCount = alerts.filter((a) => !a.acknowledged).length;

  return (
    <Card
      title={
        <Space>
          <BellOutlined />
          <span>阈值告警</span>
          {unackCount > 0 && (
            <Tag color="red">{unackCount} 条未读</Tag>
          )}
        </Space>
      }
      extra={
        unackCount > 0 && (
          <Button type="link" size="small" onClick={onAcknowledgeAll}>
            全部已读
          </Button>
        )
      }
    >
      <List
        size="small"
        dataSource={alerts}
        locale={{ emptyText: '暂无告警' }}
        renderItem={(item) => (
          <List.Item
            actions={
              !item.acknowledged
                ? [
                    <Button
                      type="link"
                      size="small"
                      icon={<CheckOutlined />}
                      onClick={() => onAcknowledge?.(item.id)}
                    >
                      已读
                    </Button>,
                    <Button
                      type="link"
                      size="small"
                      danger
                      icon={<CloseOutlined />}
                      onClick={() => onDismiss?.(item.id)}
                    >
                      忽略
                    </Button>,
                  ]
                : undefined
            }
          >
            <List.Item.Meta
              avatar={
                <Tag color={SEVERITY_MAP[item.severity]?.color ?? 'default'}>
                  {SEVERITY_MAP[item.severity]?.text ?? item.severity}
                </Tag>
              }
              title={
                <Space>
                  <Text strong={!item.acknowledged}>
                    {TYPE_MAP[item.type] ?? item.type}
                  </Text>
                  {item.value != null && item.threshold != null && (
                    <Text type="secondary">
                      {item.value.toFixed(2)} / {item.threshold}
                    </Text>
                  )}
                </Space>
              }
              description={
                <Space direction="vertical" size={0}>
                  <Text type={item.acknowledged ? 'secondary' : undefined}>
                    {item.message}
                  </Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {item.timestamp}
                  </Text>
                </Space>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
}

export default AlertPanel;

import { Table, Tag, Button, Space, Typography } from 'antd';
import { DeleteOutlined, PauseCircleOutlined, PlayCircleOutlined } from '@ant-design/icons';

export interface InferenceTask {
  id: string;
  specimenId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: number;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  result?: number;
  error?: string;
}

interface TaskQueueProps {
  data: InferenceTask[];
  loading?: boolean;
  onCancel?: (task: InferenceTask) => void;
  onRetry?: (task: InferenceTask) => void;
  onClearCompleted?: () => void;
}

const STATUS_MAP = {
  pending: { color: 'default', text: '等待中' },
  running: { color: 'processing', text: '运行中' },
  completed: { color: 'success', text: '已完成' },
  failed: { color: 'error', text: '失败' },
};

function TaskQueue({
  data,
  loading = false,
  onCancel,
  onRetry,
  onClearCompleted,
}: TaskQueueProps) {
  const columns = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      ellipsis: true,
      render: (id: string) => (
        <Typography.Text copyable={{ text: id }}>{id.slice(0, 8)}...</Typography.Text>
      ),
    },
    {
      title: '试样ID',
      dataIndex: 'specimenId',
      key: 'specimenId',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (s: keyof typeof STATUS_MAP) => (
        <Tag color={STATUS_MAP[s]?.color ?? 'default'}>{STATUS_MAP[s]?.text ?? s}</Tag>
      ),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
    },
    {
      title: '结果',
      dataIndex: 'result',
      key: 'result',
      width: 100,
      render: (v: number | undefined) => (v != null ? `${v.toFixed(4)} N` : '-'),
    },
    {
      title: '错误',
      dataIndex: 'error',
      key: 'error',
      ellipsis: true,
      render: (e: string | undefined) => (e ? <Typography.Text type="danger">{e}</Typography.Text> : '-'),
    },
    {
      title: '操作',
      key: 'action',
      width: 140,
      render: (_: unknown, record: InferenceTask) => (
        <Space>
          {(record.status === 'pending' || record.status === 'running') && (
            <Button
              type="link"
              size="small"
              danger
              icon={<PauseCircleOutlined />}
              onClick={() => onCancel?.(record)}
            >
              取消
            </Button>
          )}
          {record.status === 'failed' && (
            <Button
              type="link"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => onRetry?.(record)}
            >
              重试
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const hasCompleted = data.some((t) => t.status === 'completed' || t.status === 'failed');

  return (
    <div>
      {hasCompleted && (
        <div style={{ marginBottom: 12, textAlign: 'right' }}>
          <Button
            size="small"
            icon={<DeleteOutlined />}
            onClick={onClearCompleted}
          >
            清除已完成
          </Button>
        </div>
      )}
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
        }}
        size="small"
      />
    </div>
  );
}

export default TaskQueue;

import { Table, Tag, Space, Button, Typography } from 'antd';
import { EyeOutlined } from '@ant-design/icons';

export interface VersionRecord {
  runId: string;
  version: string;
  modelType: string;
  mae: number;
  rmse: number;
  r2: number;
  createdAt: string;
  status: 'active' | 'archived';
}

interface VersionHistoryProps {
  data: VersionRecord[];
  loading?: boolean;
  onView?: (record: VersionRecord) => void;
}

function VersionHistory({
  data,
  loading = false,
  onView,
}: VersionHistoryProps) {
  const columns = [
    {
      title: 'Run ID',
      dataIndex: 'runId',
      key: 'runId',
      ellipsis: true,
      render: (id: string) => (
        <Typography.Text copyable={{ text: id }}>{id.slice(0, 8)}...</Typography.Text>
      ),
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 100,
    },
    {
      title: '模型类型',
      dataIndex: 'modelType',
      key: 'modelType',
      width: 120,
    },
    {
      title: 'MAE',
      dataIndex: 'mae',
      key: 'mae',
      width: 90,
      render: (v: number) => v.toFixed(4),
    },
    {
      title: 'RMSE',
      dataIndex: 'rmse',
      key: 'rmse',
      width: 90,
      render: (v: number) => v.toFixed(4),
    },
    {
      title: 'R²',
      dataIndex: 'r2',
      key: 'r2',
      width: 90,
      render: (v: number) => v.toFixed(4),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      render: (s: string) => (
        <Tag color={s === 'active' ? 'green' : 'default'}>{s === 'active' ? '活跃' : '归档'}</Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: unknown, record: VersionRecord) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => onView?.(record)}
          >
            查看
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      rowKey="runId"
      loading={loading}
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        showTotal: (t) => `共 ${t} 条`,
      }}
      size="small"
    />
  );
}

export default VersionHistory;

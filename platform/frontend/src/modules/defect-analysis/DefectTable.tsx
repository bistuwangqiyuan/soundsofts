import { Card, Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { Defect, DefectType, DefectSeverity } from '@/types/api';

const DEFECT_TYPE_MAP: Record<DefectType, string> = {
  bubble: '气泡',
  weak_bond: '弱粘',
  disbond: '脱粘',
  normal: '正常粘接',
};

const SEVERITY_MAP: Record<DefectSeverity, { color: string; text: string }> = {
  low: { color: 'default', text: '低' },
  medium: { color: 'processing', text: '中' },
  high: { color: 'warning', text: '高' },
  critical: { color: 'error', text: '严重' },
};

interface DefectTableProps {
  defects?: Defect[];
}

function DefectTable({ defects = [] }: DefectTableProps) {
  const columns: ColumnsType<Defect> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      ellipsis: true,
    },
    {
      title: '面积 (px²)',
      dataIndex: 'area',
      key: 'area',
      width: 100,
      render: (v: number) => v.toFixed(2),
    },
    {
      title: '质心 X',
      key: 'centroidX',
      width: 90,
      render: (_, r) => r.centroid.x.toFixed(2),
    },
    {
      title: '质心 Y',
      key: 'centroidY',
      width: 90,
      render: (_, r) => r.centroid.y.toFixed(2),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (t: DefectType) => DEFECT_TYPE_MAP[t] ?? t,
    },
    {
      title: '等级',
      dataIndex: 'severity',
      key: 'severity',
      width: 80,
      render: (s: DefectSeverity) => {
        const m = SEVERITY_MAP[s];
        return m ? <Tag color={m.color}>{m.text}</Tag> : s;
      },
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 90,
      render: (v: number) => `${(v * 100).toFixed(1)}%`,
    },
  ];

  return (
    <Card title="缺陷列表">
      {defects.length === 0 && (
        <div style={{ padding: 24, textAlign: 'center', color: '#999' }}>
          暂无缺陷数据，请从 C 扫上传页面上传图像进行分析
        </div>
      )}
      {defects.length > 0 && (
      <Table
        columns={columns}
        dataSource={defects}
        rowKey="id"
        size="small"
        pagination={{ pageSize: 10, showSizeChanger: true }}
      />
      )}
    </Card>
  );
}

export default DefectTable;

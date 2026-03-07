import { useState, useEffect } from 'react';
import { Card, Table, Form, Select, DatePicker, Button, Space, Tag, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { SearchOutlined, DownloadOutlined } from '@ant-design/icons';
import { auditApi } from '@/services/api';
import type { AuditLogEntry, AuditLogFilter } from '@/types/api';

const { RangePicker } = DatePicker;

function AuditLog() {
  const [form] = Form.useForm<AuditLogFilter>();
  const [data, setData] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const fetchLogs = () => {
    const values = form.getFieldsValue() as {
      userId?: string;
      action?: string;
      resource?: string;
      dateRange?: [unknown, unknown];
    };
    const filter: AuditLogFilter = {
      userId: values.userId,
      action: values.action,
      resource: values.resource,
      page,
      pageSize,
    };
    if (values.dateRange?.length === 2) {
      const [start, end] = values.dateRange as [{ format: (s: string) => string }, { format: (s: string) => string }];
      filter.startDate = start?.format('YYYY-MM-DD');
      filter.endDate = end?.format('YYYY-MM-DD');
    }
    setLoading(true);
    auditApi
      .getLogs(filter)
      .then((res) => {
        const d = res.data.data;
        setData(d?.items ?? []);
        setTotal(d?.total ?? 0);
      })
      .catch(() => {
        message.error('加载审计日志失败');
        setData([]);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLogs();
  }, [page, pageSize]);

  const onSearch = () => {
    setPage(1);
    fetchLogs();
  };

  const onExport = () => {
    const values = form.getFieldsValue();
    const filter: AuditLogFilter = { ...values, pageSize: 10000 };
    auditApi
      .exportLogs(filter)
      .then((res) => {
        const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `audit_log_${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        message.success('导出成功');
      })
      .catch(() => message.error('导出失败'));
  };

  const columns: ColumnsType<AuditLogEntry> = [
    { title: '时间', dataIndex: 'timestamp', key: 'timestamp', width: 180 },
    { title: '用户', dataIndex: 'username', key: 'username', width: 120 },
    { title: '操作', dataIndex: 'action', key: 'action', width: 120 },
    { title: '资源', dataIndex: 'resource', key: 'resource', width: 150 },
    {
      title: '状态',
      dataIndex: 'success',
      key: 'success',
      width: 80,
      render: (v: boolean) => (v ? <Tag color="success">成功</Tag> : <Tag color="error">失败</Tag>),
    },
    { title: '详情', dataIndex: 'details', key: 'details', ellipsis: true },
  ];

  return (
    <Card title="审计日志">
      <Form form={form} layout="inline" onFinish={onSearch} style={{ marginBottom: 16 }}>
        <Form.Item name="userId">
          <Select placeholder="用户" allowClear style={{ width: 120 }} />
        </Form.Item>
        <Form.Item name="action">
          <Select placeholder="操作" allowClear style={{ width: 120 }} />
        </Form.Item>
        <Form.Item name="resource">
          <Select placeholder="资源" allowClear style={{ width: 120 }} />
        </Form.Item>
        <Form.Item name="dateRange">
          <RangePicker />
        </Form.Item>
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
              查询
            </Button>
            <Button icon={<DownloadOutlined />} onClick={onExport}>
              导出
            </Button>
          </Space>
        </Form.Item>
      </Form>
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          pageSize,
          total,
          showSizeChanger: true,
          showTotal: (t: number) => `共 ${t} 条`,
          onChange: (p: number, ps?: number) => {
            setPage(p);
            setPageSize(ps ?? 20);
          },
        }}
      />
    </Card>
  );
}

export default AuditLog;

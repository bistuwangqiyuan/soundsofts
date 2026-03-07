import { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  Tag,
  Typography,
  message,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';

const { Text } = Typography;

export interface Role {
  id: string;
  name: string;
  description?: string;
  permissions: string[];
  createdAt?: string;
}

const PERMISSION_OPTIONS = [
  { label: '数据导入', value: 'data:import' },
  { label: '数据查看', value: 'data:view' },
  { label: '模型训练', value: 'model:train' },
  { label: '模型部署', value: 'model:deploy' },
  { label: '推理执行', value: 'inference:run' },
  { label: '缺陷分析', value: 'defect:analyze' },
  { label: '报告导出', value: 'report:export' },
  { label: '用户管理', value: 'admin:users' },
  { label: '角色管理', value: 'admin:roles' },
  { label: '审计日志', value: 'admin:audit' },
];

interface RoleManagerProps {
  roles?: Role[];
  onAdd?: (role: Omit<Role, 'id'>) => Promise<void>;
  onEdit?: (id: string, role: Partial<Role>) => Promise<void>;
  onDelete?: (id: string) => Promise<void>;
}

function RoleManager({
  roles = [],
  onAdd,
  onEdit,
  onDelete,
}: RoleManagerProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    setModalOpen(true);
  };

  const handleEdit = (record: Role) => {
    setEditingId(record.id);
    form.setFieldsValue({
      name: record.name,
      description: record.description,
      permissions: record.permissions,
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await onEdit?.(editingId, values);
        message.success('角色已更新');
      } else {
        await onAdd?.({ ...values, id: '' });
        message.success('角色已创建');
      }
      setModalOpen(false);
      form.resetFields();
    } catch (e) {
      // validation or API error
    }
  };

  const handleDelete = (record: Role) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除角色「${record.name}」吗？`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        await onDelete?.(record.id);
        message.success('角色已删除');
      },
    });
  };

  const columns = [
    {
      title: '角色名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => <Text strong>{name}</Text>,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '权限',
      dataIndex: 'permissions',
      key: 'permissions',
      render: (perms: string[]) => (
        <Space wrap size={[4, 4]}>
          {perms.slice(0, 3).map((p) => (
            <Tag key={p} color="blue">
              {PERMISSION_OPTIONS.find((o) => o.value === p)?.label ?? p}
            </Tag>
          ))}
          {perms.length > 3 && (
            <Tag>+{perms.length - 3}</Tag>
          )}
        </Space>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: unknown, record: Role) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="角色管理 (RBAC)"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新建角色
        </Button>
      }
    >
      <Table
        columns={columns}
        dataSource={roles}
        rowKey="id"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
        }}
      />
      <Modal
        title={editingId ? '编辑角色' : '新建角色'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setModalOpen(false);
          form.resetFields();
        }}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          >
            <Input placeholder="如：数据分析师" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea placeholder="角色描述" rows={2} />
          </Form.Item>
          <Form.Item
            name="permissions"
            label="权限"
            rules={[{ required: true, message: '请选择至少一项权限' }]}
          >
            <Select
              mode="multiple"
              placeholder="选择权限"
              options={PERMISSION_OPTIONS}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}

export default RoleManager;

import { Card, Select, InputNumber, Space, Button, Form, Row, Col } from 'antd';
import { FilterOutlined, ReloadOutlined } from '@ant-design/icons';
import type { DefectType } from '@/types/api';

const DEFECT_OPTIONS: { label: string; value: DefectType }[] = [
  { label: '气泡', value: 'bubble' },
  { label: '弱粘接', value: 'weak_bond' },
  { label: '脱粘', value: 'disbond' },
  { label: '正常', value: 'normal' },
];

export interface CardFilterValues {
  defectTypes?: DefectType[];
  specimenIds?: string[];
  errorMin?: number;
  errorMax?: number;
  forceMin?: number;
  forceMax?: number;
}

interface CardFilterProps {
  specimenOptions?: string[];
  onFilter?: (values: CardFilterValues) => void;
  onReset?: () => void;
}

function CardFilter({
  specimenOptions = [],
  onFilter,
  onReset,
}: CardFilterProps) {
  const [form] = Form.useForm();

  const handleFilter = () => {
    const values = form.getFieldsValue();
    const payload: CardFilterValues = {};
    if (values.defectTypes?.length) payload.defectTypes = values.defectTypes;
    if (values.specimenIds?.length) payload.specimenIds = values.specimenIds;
    if (values.errorMin != null) payload.errorMin = values.errorMin;
    if (values.errorMax != null) payload.errorMax = values.errorMax;
    if (values.forceMin != null) payload.forceMin = values.forceMin;
    if (values.forceMax != null) payload.forceMax = values.forceMax;
    onFilter?.(payload);
  };

  const handleReset = () => {
    form.resetFields();
    onReset?.();
  };

  return (
    <Card
      size="small"
      title={
        <Space>
          <FilterOutlined />
          数据筛选
        </Space>
      }
    >
      <Form form={form} layout="vertical" onFinish={handleFilter}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Form.Item name="defectTypes" label="缺陷类型">
              <Select
                mode="multiple"
                placeholder="选择缺陷类型"
                options={DEFECT_OPTIONS}
                allowClear
                maxTagCount="responsive"
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item name="specimenIds" label="试样ID">
              <Select
                mode="multiple"
                placeholder="选择试样"
                options={specimenOptions.map((id) => ({ label: id, value: id }))}
                allowClear
                maxTagCount="responsive"
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item name="errorMin" label="误差范围 (N) 最小">
              <InputNumber placeholder="≥" style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item name="errorMax" label="误差范围 (N) 最大">
              <InputNumber placeholder="≤" style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item name="forceMin" label="预测力 (N) 最小">
              <InputNumber placeholder="≥" style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item name="forceMax" label="预测力 (N) 最大">
              <InputNumber placeholder="≤" style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" icon={<FilterOutlined />}>
              筛选
            </Button>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
}

export default CardFilter;

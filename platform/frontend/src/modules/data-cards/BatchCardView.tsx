import { useState } from 'react';
import { Row, Col, Pagination, Radio, Space, Typography } from 'antd';
import { AppstoreOutlined, UnorderedListOutlined } from '@ant-design/icons';
import SinglePointCard, { type SinglePointData } from './SinglePointCard';

const { Text } = Typography;

type ViewMode = 'grid' | 'list';

interface BatchCardViewProps {
  data: SinglePointData[];
  pageSize?: number;
  onCardClick?: (item: SinglePointData) => void;
}

function BatchCardView({
  data,
  pageSize = 12,
  onCardClick,
}: BatchCardViewProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [currentPage, setCurrentPage] = useState(1);

  const total = data.length;
  const start = (currentPage - 1) * pageSize;
  const pageData = data.slice(start, start + pageSize);

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      <Space style={{ width: '100%', justifyContent: 'space-between' }}>
        <Radio.Group
          value={viewMode}
          onChange={(e) => setViewMode(e.target.value)}
          optionType="button"
          size="small"
        >
          <Radio.Button value="grid">
            <AppstoreOutlined /> 网格
          </Radio.Button>
          <Radio.Button value="list">
            <UnorderedListOutlined /> 列表
          </Radio.Button>
        </Radio.Group>
        <Text type="secondary">
          共 {total} 条记录
        </Text>
      </Space>

      <Row
        gutter={[16, 16]}
        style={{
          flexDirection: viewMode === 'list' ? 'column' : 'row',
          alignItems: viewMode === 'list' ? 'stretch' : undefined,
        }}
      >
        {pageData.map((item) => (
          <Col
            key={item.id}
            xs={24}
            sm={viewMode === 'list' ? 24 : 12}
            md={viewMode === 'list' ? 24 : 8}
            lg={viewMode === 'list' ? 24 : 6}
          >
            <SinglePointCard
              data={item}
              onClick={onCardClick ? () => onCardClick(item) : undefined}
            />
          </Col>
        ))}
      </Row>

      {total > pageSize && (
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: 16 }}>
          <Pagination
            current={currentPage}
            total={total}
            pageSize={pageSize}
            onChange={setCurrentPage}
            showSizeChanger
            showQuickJumper
            showTotal={(t) => `共 ${t} 条`}
          />
        </div>
      )}
    </Space>
  );
}

export default BatchCardView;

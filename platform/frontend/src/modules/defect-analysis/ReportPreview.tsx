import { Card, Button, Typography, Space } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

export interface ReportContent {
  title?: string;
  summary?: string;
  sections?: { heading: string; content: string }[];
  defects?: { type: string; count: number }[];
  generatedAt?: string;
}

interface ReportPreviewProps {
  content: ReportContent;
  onExportWord?: () => void;
  loading?: boolean;
}

function ReportPreview({ content, onExportWord, loading = false }: ReportPreviewProps) {
  return (
    <Card
      title="报告预览"
      extra={
        <Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={onExportWord}
          loading={loading}
        >
          导出 Word
        </Button>
      }
    >
      <div style={{ maxHeight: 500, overflow: 'auto' }}>
        {content.title && (
          <Title level={4} style={{ marginTop: 0 }}>
            {content.title}
          </Title>
        )}
        {content.generatedAt && (
          <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
            生成时间: {content.generatedAt}
          </Text>
        )}
        {content.summary && (
          <Paragraph>{content.summary}</Paragraph>
        )}
        {content.defects && content.defects.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>缺陷统计</Title>
            <Space wrap>
              {content.defects.map((d) => (
                <Text key={d.type}>
                  {d.type}: <Text strong>{d.count}</Text> 处
                </Text>
              ))}
            </Space>
          </div>
        )}
        {content.sections?.map((section, i) => (
          <div key={i} style={{ marginBottom: 16 }}>
            <Title level={5}>{section.heading}</Title>
            <Paragraph>{section.content}</Paragraph>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default ReportPreview;

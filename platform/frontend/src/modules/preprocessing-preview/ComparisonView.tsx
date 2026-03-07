import { useMemo } from 'react';
import { Card, Row, Col, Typography } from 'antd';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

const { Text } = Typography;

interface ComparisonViewProps {
  rawData: number[];
  processedData: number[];
  samplingRate?: number;
  height?: number;
}

function ComparisonView({
  rawData,
  processedData,
  samplingRate = 1e6,
  height = 300,
}: ComparisonViewProps) {
  const rawOption = useMemo<EChartsOption>(() => {
    const time = rawData.map((_, i) => (i / samplingRate) * 1000);
    return {
      grid: { left: '8%', right: '4%', top: '10%', bottom: '15%', containLabel: true },
      xAxis: {
        type: 'value',
        name: '时间 (ms)',
        nameLocation: 'middle',
        nameGap: 25,
      },
      yAxis: { type: 'value', name: '幅值' },
      tooltip: { trigger: 'axis' },
      series: [
        {
          type: 'line',
          data: time.map((t, i) => [t, rawData[i]]),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: '#8c8c8c' },
        },
      ],
    };
  }, [rawData, samplingRate]);

  const processedOption = useMemo<EChartsOption>(() => {
    const time = processedData.map((_, i) => (i / samplingRate) * 1000);
    return {
      grid: { left: '8%', right: '4%', top: '10%', bottom: '15%', containLabel: true },
      xAxis: {
        type: 'value',
        name: '时间 (ms)',
        nameLocation: 'middle',
        nameGap: 25,
      },
      yAxis: { type: 'value', name: '幅值' },
      tooltip: { trigger: 'axis' },
      series: [
        {
          type: 'line',
          data: time.map((t, i) => [t, processedData[i]]),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: '#1677ff' },
        },
      ],
    };
  }, [processedData, samplingRate]);

  return (
    <Card title="波形对比">
      <Row gutter={[24, 16]}>
        <Col xs={24} lg={12}>
          <div style={{ marginBottom: 8 }}>
            <Text type="secondary">原始波形</Text>
          </div>
          <ReactECharts
            option={rawOption}
            style={{ height }}
            opts={{ renderer: 'canvas' }}
            notMerge
          />
        </Col>
        <Col xs={24} lg={12}>
          <div style={{ marginBottom: 8 }}>
            <Text type="secondary">预处理后</Text>
          </div>
          <ReactECharts
            option={processedOption}
            style={{ height }}
            opts={{ renderer: 'canvas' }}
            notMerge
          />
        </Col>
      </Row>
    </Card>
  );
}

export default ComparisonView;

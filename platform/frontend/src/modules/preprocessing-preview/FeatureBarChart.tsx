import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

export interface FeatureItem {
  name: string;
  value: number;
}

interface FeatureBarChartProps {
  features: FeatureItem[];
  title?: string;
  height?: number;
}

function FeatureBarChart({
  features,
  title = '特征提取结果',
  height = 350,
}: FeatureBarChartProps) {
  const option = useMemo<EChartsOption>(() => {
    const names = features.map((f) => f.name);
    const values = features.map((f) => f.value);

    return {
      title: {
        text: title,
        left: 'center',
        textStyle: { fontSize: 14 },
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
      },
      grid: { left: '3%', right: '4%', bottom: '10%', top: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: names,
        axisLabel: {
          rotate: names.some((n) => n.length > 6) ? 45 : 0,
          interval: 0,
        },
      },
      yAxis: {
        type: 'value',
        name: '特征值',
      },
      series: [
        {
          type: 'bar',
          data: values,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: '#1677ff' },
                { offset: 1, color: '#69b1ff' },
              ],
            },
          },
          barWidth: '60%',
        },
      ],
    };
  }, [features, title]);

  return (
    <ReactECharts
      option={option}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
      notMerge
    />
  );
}

export default FeatureBarChart;

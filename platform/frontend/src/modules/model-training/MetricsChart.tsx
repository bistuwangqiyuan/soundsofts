import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import type { ModelMetrics } from '@/types/api';

interface MetricsChartProps {
  data: ModelMetrics[];
  height?: number;
}

function MetricsChart({ data, height = 300 }: MetricsChartProps) {
  const models = data.map((m) => m.modelName);
  const maeData = data.map((m) => m.mae);
  const rmseData = data.map((m) => m.rmse);

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: {
      data: ['MAE', 'RMSE'],
      bottom: 0,
    },
    grid: { left: 60, right: 40, top: 30, bottom: 50 },
    xAxis: {
      type: 'category',
      data: models,
      axisLabel: {
        rotate: 30,
        fontSize: 10,
      },
    },
    yAxis: {
      type: 'value',
      name: '误差',
    },
    series: [
      {
        name: 'MAE',
        type: 'bar',
        data: maeData,
        itemStyle: { color: '#1677ff' },
      },
      {
        name: 'RMSE',
        type: 'bar',
        data: rmseData,
        itemStyle: { color: '#52c41a' },
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
      notMerge
    />
  );
}

export default MetricsChart;

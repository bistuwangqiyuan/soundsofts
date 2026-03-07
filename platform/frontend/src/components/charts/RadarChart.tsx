import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import type { ModelMetrics } from '@/types/api';

interface RadarChartProps {
  data: ModelMetrics[];
  height?: number;
}

const INDICATORS = [
  { name: 'MAE', max: 5, inverse: true },
  { name: 'RMSE', max: 5, inverse: true },
  { name: 'R²', max: 1, inverse: false },
  { name: 'MAPE(%)', max: 10, inverse: true },
];

function RadarChart({ data, height = 400 }: RadarChartProps) {
  const indicator = INDICATORS.map((i) => ({
    name: i.name,
    max: i.max,
  }));

  const seriesData = data.map((m) => ({
    name: m.modelName,
    value: [
      Math.min(m.mae, INDICATORS[0]!.max),
      Math.min(m.rmse, INDICATORS[1]!.max),
      Math.min(m.r2, INDICATORS[2]!.max),
      Math.min(m.mape, INDICATORS[3]!.max),
    ],
  }));

  const colors = ['#1677ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2'];

  const option: EChartsOption = {
    title: {
      text: '模型综合性能雷达图',
      left: 'center',
      textStyle: { fontSize: 14 },
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: unknown) => {
        const p = params as { name: string; value: number[] };
        const lines = [`<strong>${p.name}</strong>`];
        INDICATORS.forEach((ind, i) => {
          lines.push(`${ind.name}: ${(p.value[i] ?? 0).toFixed(4)}`);
        });
        return lines.join('<br/>');
      },
    },
    legend: {
      data: data.map((m) => m.modelName),
      bottom: 0,
      type: 'scroll',
    },
    radar: {
      indicator,
      radius: '60%',
      center: ['50%', '50%'],
      splitNumber: 4,
      axisName: {
        color: '#333',
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(22, 119, 255, 0.05)', 'rgba(22, 119, 255, 0.1)'],
        },
      },
      splitLine: {
        lineStyle: { color: 'rgba(22, 119, 255, 0.3)' },
      },
      axisLine: {
        lineStyle: { color: 'rgba(22, 119, 255, 0.5)' },
      },
    },
    series: [
      {
        type: 'radar',
        data: seriesData.map((s, i) => ({
          ...s,
          lineStyle: { color: colors[i % colors.length] },
          areaStyle: { color: colors[i % colors.length], opacity: 0.2 },
          symbol: 'circle',
          symbolSize: 4,
        })),
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

export default RadarChart;

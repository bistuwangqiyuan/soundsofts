import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import type { ModelMetrics } from '@/types/api';

const INDICATORS = [
  { name: 'MAE', max: 5 },
  { name: 'RMSE', max: 5 },
  { name: 'R²', max: 1 },
  { name: 'MAPE(%)', max: 10 },
  { name: '训练时间(s)', max: 60 },
];

interface RadarComparisonProps {
  data: ModelMetrics[];
  height?: number;
}

function RadarComparison({ data, height = 450 }: RadarComparisonProps) {
  const option = useMemo<EChartsOption>(() => {
    const indicator = INDICATORS.map((i) => ({ name: i.name, max: i.max }));

    const colors = ['#1677ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2'];

    const seriesData = data.map((m, idx) => ({
      name: m.modelName,
      value: [
        Math.min(m.mae, INDICATORS[0]!.max),
        Math.min(m.rmse, INDICATORS[1]!.max),
        Math.min(m.r2, INDICATORS[2]!.max),
        Math.min(m.mape, INDICATORS[3]!.max),
        Math.min((m.trainingTime ?? 0) / 1000, INDICATORS[4]!.max),
      ],
      lineStyle: { color: colors[idx % colors.length] },
      areaStyle: { color: colors[idx % colors.length], opacity: 0.2 },
      symbol: 'circle',
      symbolSize: 4,
    }));

    return {
      title: {
        text: '六模型雷达对比',
        left: 'center',
        textStyle: { fontSize: 16 },
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
        radius: '55%',
        center: ['50%', '48%'],
        splitNumber: 4,
        axisName: { color: '#333' },
        splitArea: {
          areaStyle: {
            color: ['rgba(22, 119, 255, 0.05)', 'rgba(22, 119, 255, 0.1)'],
          },
        },
        splitLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.3)' } },
        axisLine: { lineStyle: { color: 'rgba(22, 119, 255, 0.5)' } },
      },
      series: [
        {
          type: 'radar',
          data: seriesData,
        },
      ],
    };
  }, [data]);

  return (
    <ReactECharts
      option={option}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
      notMerge
    />
  );
}

export default RadarComparison;

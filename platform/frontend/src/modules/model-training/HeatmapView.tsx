import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

export interface HeatmapDataItem {
  model: string;
  metric: string;
  value: number;
}

interface HeatmapViewProps {
  data: HeatmapDataItem[];
  models: string[];
  metrics: string[];
  title?: string;
  height?: number;
}

function HeatmapView({
  data,
  models,
  metrics,
  title = '模型指标热力图',
  height = 400,
}: HeatmapViewProps) {
  const option = useMemo<EChartsOption>(() => {
    const matrix: number[][] = models.map(() =>
      metrics.map(() => 0)
    );
    const valueMap = new Map<string, number>();
    data.forEach((d) => {
      valueMap.set(`${d.model}-${d.metric}`, d.value);
    });
    models.forEach((m, i) => {
      metrics.forEach((met, j) => {
        matrix[i]![j] = valueMap.get(`${m}-${met}`) ?? 0;
      });
    });

    const heatmapData: [number, number, number][] = [];
    matrix.forEach((row, i) => {
      row.forEach((val, j) => {
        heatmapData.push([j, i, val]);
      });
    });

    return {
      title: {
        text: title,
        left: 'center',
        textStyle: { fontSize: 14 },
      },
      tooltip: {
        position: 'top',
        formatter: (params: unknown) => {
          const p = params as { value: [number, number, number] };
          const [j, i, val] = p.value;
          return `${models[i]} - ${metrics[j]}: ${val.toFixed(4)}`;
        },
      },
      grid: { left: '15%', right: '5%', top: '15%', bottom: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: metrics,
        splitArea: { show: false },
        axisLabel: { rotate: 30 },
      },
      yAxis: {
        type: 'category',
        data: models,
        splitArea: { show: false },
      },
      visualMap: {
        min: Math.min(...data.map((d) => d.value), 0),
        max: Math.max(...data.map((d) => d.value), 1),
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        inRange: {
          color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'],
        },
      },
      series: [
        {
          type: 'heatmap',
          data: heatmapData,
          label: {
            show: true,
            formatter: (params: { value: [number, number, number] }) =>
              params.value[2].toFixed(2),
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        },
      ],
    };
  }, [data, models, metrics, title]);

  return (
    <ReactECharts
      option={option}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
      notMerge
    />
  );
}

export default HeatmapView;

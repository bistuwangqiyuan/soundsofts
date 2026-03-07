import { useMemo } from 'react';
import { Card, Typography } from 'antd';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

const { Text } = Typography;

export interface AlignmentPoint {
  x: number;
  y: number;
  ultrasonicValue?: number;
  forceValue?: number;
  label?: string;
}

interface SpatialAlignmentProps {
  ultrasonicGrid: number[][];
  forceGrid: number[][];
  markers?: AlignmentPoint[];
  title?: string;
  height?: number;
}

function SpatialAlignment({
  ultrasonicGrid,
  forceGrid,
  markers = [],
  title = '空间对齐可视化',
  height = 400,
}: SpatialAlignmentProps) {
  const option = useMemo<EChartsOption>(() => {
    const scatterData = markers.map((m) => [m.x, m.y, m.label ?? '']);
    const grid = ultrasonicGrid.length > 0 ? ultrasonicGrid : forceGrid;
    const heatmapData: [number, number, number][] = [];
    grid.forEach((row, i) => {
      row.forEach((v, j) => {
        heatmapData.push([j, i, v]);
      });
    });

    const allValues = [...ultrasonicGrid.flat(), ...forceGrid.flat()].filter((v) => !Number.isNaN(v));
    const vMin = allValues.length ? Math.min(...allValues) : 0;
    const vMax = allValues.length ? Math.max(...allValues) : 1;

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
          return `(${p.value[0]}, ${p.value[1]}): ${p.value[2].toFixed(4)}`;
        },
      },
      grid: { left: '10%', right: '10%', top: '15%', bottom: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: grid[0]?.map((_, i) => i.toString()) ?? [],
        splitArea: { show: false },
      },
      yAxis: {
        type: 'category',
        data: grid.map((_, i) => i.toString()),
        splitArea: { show: false },
      },
      visualMap: {
        min: vMin,
        max: vMax,
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
          itemStyle: { borderWidth: 1, borderColor: '#fff' },
        },
        ...(scatterData.length > 0
          ? [
              {
                type: 'scatter' as const,
                data: scatterData,
                symbolSize: 8,
                itemStyle: { color: '#ff4d4f', borderColor: '#fff', borderWidth: 2 },
                label: {
                  show: true,
                  formatter: (params: { value: [number, number, string] }) => params.value[2] || '',
                  position: 'top' as const,
                },
              },
            ]
          : []),
      ],
    };
  }, [ultrasonicGrid, forceGrid, markers, title]);

  return (
    <Card>
      <ReactECharts
        option={option}
        style={{ height }}
        opts={{ renderer: 'canvas' }}
        notMerge
      />
    </Card>
  );
}

export default SpatialAlignment;

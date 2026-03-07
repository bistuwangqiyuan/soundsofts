import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

export interface ForceDataPoint {
  displacement: number;
  force: number;
  time?: number;
}

interface ForceViewerProps {
  data: ForceDataPoint[];
  title?: string;
  height?: number;
  showTimeAxis?: boolean;
}

function ForceViewer({
  data,
  title = '剥离力曲线',
  height = 400,
  showTimeAxis = true,
}: ForceViewerProps) {
  const option = useMemo<EChartsOption>(() => {
    const displacement = data.map((d) => d.displacement);
    const force = data.map((d) => d.force);
    const time = data.map((d) => d.time ?? d.displacement);

    return {
      title: {
        text: title,
        left: 'center',
        textStyle: { fontSize: 14 },
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
      },
      legend: {
        data: ['剥离力 (N)', showTimeAxis ? '位移 (mm)' : '位移 (mm)'],
        bottom: 0,
      },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '15%', containLabel: true },
      xAxis: {
        type: 'value',
        name: showTimeAxis ? '时间 (s)' : '位移 (mm)',
        nameLocation: 'middle',
        nameGap: 30,
        axisLine: { show: true },
        splitLine: { lineStyle: { type: 'dashed', opacity: 0.3 } },
      },
      yAxis: [
        {
          type: 'value',
          name: '剥离力 (N)',
          position: 'left',
          axisLine: { show: true },
          splitLine: { lineStyle: { type: 'dashed', opacity: 0.3 } },
        },
        {
          type: 'value',
          name: '位移 (mm)',
          position: 'right',
          axisLine: { show: true },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: '剥离力 (N)',
          type: 'line',
          data: showTimeAxis ? time.map((t, i) => [t, force[i]]) : displacement.map((d, i) => [d, force[i]]),
          xAxisIndex: 0,
          yAxisIndex: 0,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: '#1677ff' },
          areaStyle: { opacity: 0.1, color: '#1677ff' },
        },
        {
          name: '位移 (mm)',
          type: 'line',
          data: showTimeAxis ? time.map((t, i) => [t, displacement[i]]) : displacement.map((d, i) => [d, displacement[i]]),
          xAxisIndex: 0,
          yAxisIndex: 1,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: '#52c41a' },
        },
      ],
    };
  }, [data, title, showTimeAxis]);

  return (
    <ReactECharts
      option={option}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
      notMerge
    />
  );
}

export default ForceViewer;

import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

export interface DualAxisPoint {
  x: number;
  ultrasonic: number;
  peelForce: number;
}

interface DualAxisOverlayProps {
  data: DualAxisPoint[];
  title?: string;
  height?: number;
}

function DualAxisOverlay({
  data,
  title = '超声-剥离力双轴叠加',
  height = 400,
}: DualAxisOverlayProps) {
  const option = useMemo<EChartsOption>(() => {
    const xData = data.map((d) => d.x);
    const ultrasonicData = data.map((d) => d.ultrasonic);
    const peelForceData = data.map((d) => d.peelForce);

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
        data: ['超声信号', '剥离力'],
        bottom: 0,
      },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: xData,
        name: '位置/时间',
        nameLocation: 'middle',
        nameGap: 30,
      },
      yAxis: [
        {
          type: 'value',
          name: '超声幅值',
          position: 'left',
          axisLine: { show: true },
          splitLine: { lineStyle: { type: 'dashed', opacity: 0.3 } },
        },
        {
          type: 'value',
          name: '剥离力 (N)',
          position: 'right',
          axisLine: { show: true },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: '超声信号',
          type: 'line',
          data: ultrasonicData,
          yAxisIndex: 0,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: '#1677ff' },
          areaStyle: { opacity: 0.15, color: '#1677ff' },
        },
        {
          name: '剥离力',
          type: 'line',
          data: peelForceData,
          yAxisIndex: 1,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: '#52c41a' },
        },
      ],
    };
  }, [data, title]);

  return (
    <ReactECharts
      option={option}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
      notMerge
    />
  );
}

export default DualAxisOverlay;

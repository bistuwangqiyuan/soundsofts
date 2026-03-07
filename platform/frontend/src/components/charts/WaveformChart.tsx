import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

interface WaveformChartProps {
  time: number[];
  amplitude: number[];
  title?: string;
  height?: number;
  samplingRate?: number;
}

function WaveformChart({ time, amplitude, title = 'A扫时域波形', height = 320, samplingRate }: WaveformChartProps) {
  const option: EChartsOption = {
    title: {
      text: title,
      left: 'center',
      textStyle: { fontSize: 14 },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = Array.isArray(params) ? params[0] : params;
        const idx = p?.dataIndex ?? 0;
        const t = time[idx] ?? 0;
        const a = amplitude[idx] ?? 0;
        const freqInfo = samplingRate ? `\n采样率: ${(samplingRate / 1e6).toFixed(2)} MHz` : '';
        return `时间: ${t.toFixed(6)} s<br/>幅值: ${a.toFixed(4)}${freqInfo}`;
      },
    },
    grid: { left: 60, right: 40, top: 50, bottom: 50 },
    xAxis: {
      type: 'value',
      name: '时间 (s)',
      nameLocation: 'middle',
      nameGap: 30,
      axisLine: { show: true },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      name: '幅值',
      nameLocation: 'middle',
      nameGap: 45,
      axisLine: { show: true },
      splitLine: { show: true, lineStyle: { type: 'dashed', opacity: 0.3 } },
    },
    series: [
      {
        name: '波形',
        type: 'line',
        data: time.map((t, i) => [t, amplitude[i] ?? 0]),
        smooth: false,
        symbol: 'none',
        lineStyle: { color: '#1677ff', width: 1.5 },
        areaStyle: { color: 'rgba(22, 119, 255, 0.1)' },
        connectNulls: true,
      },
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: 0, start: 0, end: 100 },
      { type: 'slider', xAxisIndex: 0, start: 0, end: 100, height: 20, bottom: 10 },
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

export default WaveformChart;

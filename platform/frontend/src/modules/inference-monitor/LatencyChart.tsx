import { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import { inferenceApi } from '@/services/api';
import type { LatencyRecord } from '@/types/api';

interface LatencyChartProps {
  height?: number;
}

function LatencyChart({ height = 320 }: LatencyChartProps) {
  const [data, setData] = useState<LatencyRecord[]>([]);

  useEffect(() => {
    inferenceApi
      .getLatencyHistory({ limit: 100 })
      .then((res) => setData(res.data.data ?? []))
      .catch(() => setData([]));
  }, []);

  const timestamps = data.map((d: LatencyRecord) => new Date(d.timestamp).toLocaleTimeString());
  const latencyValues = data.map((d: LatencyRecord) => d.latencyMs);

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = Array.isArray(params) ? params[0] : params;
        const idx = p?.dataIndex ?? 0;
        const r = data[idx];
        return r
          ? `时间: ${r.timestamp}<br/>延迟: ${r.latencyMs.toFixed(2)} ms<br/>引擎: ${r.engine}`
          : '';
      },
    },
    grid: { left: 60, right: 40, top: 30, bottom: 50 },
    xAxis: {
      type: 'category',
      data: timestamps,
      boundaryGap: false,
      axisLabel: { fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      name: '延迟 (ms)',
      min: (v) => Math.max(0, (v.min ?? 0) - 5),
    },
    series: [
      {
        name: '延迟',
        type: 'line',
        data: latencyValues,
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
        lineStyle: { color: '#1677ff', width: 2 },
        areaStyle: { color: 'rgba(22, 119, 255, 0.2)' },
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

export default LatencyChart;

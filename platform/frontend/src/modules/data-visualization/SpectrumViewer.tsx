import { useState, useEffect } from 'react';
import { Card, Select, Space, Radio, message } from 'antd';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import { dataVisualizationApi } from '@/services/api';
import Loading from '@/components/common/Loading';
import type { SpectrumData, Waveform } from '@/types/api';

function SpectrumViewer() {
  const [waveforms, setWaveforms] = useState<Waveform[]>([]);
  const [spectrum, setSpectrum] = useState<SpectrumData | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [scale, setScale] = useState<'linear' | 'log'>('linear');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    dataVisualizationApi
      .listWaveforms({ pageSize: 50 })
      .then((res) => {
        const items = res.data.data?.items ?? [];
        setWaveforms(items);
        if (items.length > 0 && !selectedId) {
          setSelectedId(items[0]!.id);
        }
      })
      .catch(() => message.error('加载波形列表失败'));
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setSpectrum(null);
      return;
    }
    setLoading(true);
    dataVisualizationApi
      .computeSpectrum(selectedId)
      .then((res) => {
        setSpectrum(res.data.data ?? null);
      })
      .catch(() => {
        message.error('计算频谱失败');
        setSpectrum(null);
      })
      .finally(() => setLoading(false));
  }, [selectedId]);

  const option: EChartsOption = spectrum
    ? {
        title: {
          text: 'FFT 频谱',
          left: 'center',
          textStyle: { fontSize: 14 },
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const p = Array.isArray(params) ? params[0] : params;
            const idx = p?.dataIndex ?? 0;
            const f = spectrum.frequency[idx] ?? 0;
            const m = spectrum.magnitude[idx] ?? 0;
            return `频率: ${(f / 1e6).toFixed(2)} MHz<br/>幅值: ${m.toFixed(4)}`;
          },
        },
        grid: { left: 60, right: 40, top: 50, bottom: 50 },
        xAxis: {
          type: 'value',
          name: '频率 (Hz)',
          nameLocation: 'middle',
          nameGap: 30,
          axisLabel: {
            formatter: (v: number) => `${(v / 1e6).toFixed(2)}`,
          },
        },
        yAxis: {
          type: 'value',
          name: scale === 'log' ? '幅值 (dB)' : '幅值',
          scale: scale === 'log',
        },
        series: [
          {
            name: '频谱',
            type: 'line',
            data: spectrum.frequency.map((f, i) => [f, spectrum.magnitude[i] ?? 0]),
            smooth: false,
            symbol: 'none',
            lineStyle: { color: '#52c41a', width: 1.5 },
            areaStyle: { color: 'rgba(82, 196, 26, 0.2)' },
          },
        ],
        dataZoom: [
          { type: 'inside', xAxisIndex: 0 },
          { type: 'slider', xAxisIndex: 0, height: 20, bottom: 10 },
        ],
      }
    : {};

  return (
    <Card title="FFT 频谱展示">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Space wrap>
          <span>选择波形：</span>
          <Select
            value={selectedId ?? undefined}
            onChange={setSelectedId}
            style={{ width: 280 }}
            placeholder="请选择波形"
            options={waveforms.map((w) => ({
              label: w.id,
              value: w.id,
            }))}
          />
          <Radio.Group value={scale} onChange={(e) => setScale(e.target.value)}>
            <Radio.Button value="linear">线性</Radio.Button>
            <Radio.Button value="log">对数</Radio.Button>
          </Radio.Group>
        </Space>
        {loading ? (
          <Loading />
        ) : spectrum ? (
          <ReactECharts option={option} style={{ height: 400 }} opts={{ renderer: 'canvas' }} notMerge />
        ) : (
          <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
            请选择波形以计算频谱
          </div>
        )}
      </Space>
    </Card>
  );
}

export default SpectrumViewer;

import { useState, useEffect } from 'react';
import { Card, Select, Space, message } from 'antd';
import { dataVisualizationApi } from '@/services/api';
import WaveformChart from '@/components/charts/WaveformChart';
import Loading from '@/components/common/Loading';
import type { Waveform } from '@/types/api';

function WaveformViewer() {
  const [waveforms, setWaveforms] = useState<Waveform[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

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
      .catch(() => {
        message.error('加载波形列表失败');
        setWaveforms([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const selected = waveforms.find((w) => w.id === selectedId);

  if (loading) return <Loading />;

  return (
    <Card title="A扫时域波形展示">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Space>
          <span>选择波形：</span>
          <Select
            value={selectedId ?? undefined}
            onChange={setSelectedId}
            style={{ width: 280 }}
            placeholder="请选择波形"
            options={waveforms.map((w) => ({
              label: `${w.id} (${w.time.length} 点, ${(w.samplingRate / 1e6).toFixed(2)} MHz)`,
              value: w.id,
            }))}
          />
        </Space>
        {selected ? (
          <WaveformChart
            time={selected.time}
            amplitude={selected.amplitude}
            title={`波形 ${selected.id}`}
            height={400}
            samplingRate={selected.samplingRate}
          />
        ) : (
          <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
            暂无波形数据，请先导入数据
          </div>
        )}
      </Space>
    </Card>
  );
}

export default WaveformViewer;

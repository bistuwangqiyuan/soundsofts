import { Card, Slider, Space, Typography, InputNumber } from 'antd';

const { Text } = Typography;

export interface PreprocessingParams {
  highpassCutoff?: number;
  lowpassCutoff?: number;
  baselineWindow?: number;
  noiseThreshold?: number;
  smoothingWindow?: number;
}

interface ParameterPanelProps {
  params: PreprocessingParams;
  onChange: (params: PreprocessingParams) => void;
}

const DEFAULT_PARAMS: PreprocessingParams = {
  highpassCutoff: 0.1,
  lowpassCutoff: 5,
  baselineWindow: 100,
  noiseThreshold: 0.01,
  smoothingWindow: 5,
};

function ParameterPanel({ params, onChange }: ParameterPanelProps) {
  const merged = { ...DEFAULT_PARAMS, ...params };

  const update = (key: keyof PreprocessingParams, value: number) => {
    onChange({ ...merged, [key]: value });
  };

  return (
    <Card title="实时参数调节" size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <div>
          <Space style={{ width: '100%', justifyContent: 'space-between', marginBottom: 4 }}>
            <Text>高通截止 (kHz)</Text>
            <InputNumber
              size="small"
              min={0.01}
              max={10}
              step={0.1}
              value={merged.highpassCutoff}
              onChange={(v) => update('highpassCutoff', v ?? 0.1)}
              style={{ width: 80 }}
            />
          </Space>
          <Slider
            min={0.01}
            max={10}
            step={0.1}
            value={merged.highpassCutoff}
            onChange={(v) => update('highpassCutoff', v)}
          />
        </div>

        <div>
          <Space style={{ width: '100%', justifyContent: 'space-between', marginBottom: 4 }}>
            <Text>低通截止 (MHz)</Text>
            <InputNumber
              size="small"
              min={0.5}
              max={20}
              step={0.5}
              value={merged.lowpassCutoff}
              onChange={(v) => update('lowpassCutoff', v ?? 5)}
              style={{ width: 80 }}
            />
          </Space>
          <Slider
            min={0.5}
            max={20}
            step={0.5}
            value={merged.lowpassCutoff}
            onChange={(v) => update('lowpassCutoff', v)}
          />
        </div>

        <div>
          <Space style={{ width: '100%', justifyContent: 'space-between', marginBottom: 4 }}>
            <Text>基线窗口</Text>
            <InputNumber
              size="small"
              min={10}
              max={500}
              step={10}
              value={merged.baselineWindow}
              onChange={(v) => update('baselineWindow', v ?? 100)}
              style={{ width: 80 }}
            />
          </Space>
          <Slider
            min={10}
            max={500}
            step={10}
            value={merged.baselineWindow}
            onChange={(v) => update('baselineWindow', v)}
          />
        </div>

        <div>
          <Space style={{ width: '100%', justifyContent: 'space-between', marginBottom: 4 }}>
            <Text>噪声阈值</Text>
            <InputNumber
              size="small"
              min={0.001}
              max={0.1}
              step={0.001}
              value={merged.noiseThreshold}
              onChange={(v) => update('noiseThreshold', v ?? 0.01)}
              style={{ width: 80 }}
            />
          </Space>
          <Slider
            min={0.001}
            max={0.1}
            step={0.001}
            value={merged.noiseThreshold}
            onChange={(v) => update('noiseThreshold', v)}
          />
        </div>

        <div>
          <Space style={{ width: '100%', justifyContent: 'space-between', marginBottom: 4 }}>
            <Text>平滑窗口</Text>
            <InputNumber
              size="small"
              min={1}
              max={31}
              step={2}
              value={merged.smoothingWindow}
              onChange={(v) => update('smoothingWindow', v ?? 5)}
              style={{ width: 80 }}
            />
          </Space>
          <Slider
            min={1}
            max={31}
            step={2}
            value={merged.smoothingWindow}
            onChange={(v) => update('smoothingWindow', v)}
          />
        </div>
      </Space>
    </Card>
  );
}

export default ParameterPanel;

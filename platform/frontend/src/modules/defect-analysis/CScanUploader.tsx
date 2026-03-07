import { useState } from 'react';
import { Card, Upload, Image, message, Row, Col } from 'antd';
import type { UploadProps } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { defectAnalysisApi } from '@/services/api';
import DefectTable from './DefectTable';
import type { Defect } from '@/types/api';

function CScanUploader() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [overlayUrl, setOverlayUrl] = useState<string | null>(null);
  const [defects, setDefects] = useState<Defect[]>([]);
  const [imageId, setImageId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const uploadProps: UploadProps = {
    name: 'file',
    accept: 'image/*',
    showUploadList: false,
    beforeUpload: (file) => {
      setImageUrl(URL.createObjectURL(file));
      setDefects([]);
      setOverlayUrl(null);
      setImageId(null);
      return true;
    },
    customRequest: async ({ file, onSuccess, onError }) => {
      setLoading(true);
      try {
        const res = await defectAnalysisApi.uploadCScan(file as File);
        const { imageId: id, defects: d } = res.data.data ?? { imageId: '', defects: [] };
        setImageId(id);
        setDefects(d);
        try {
          const overlayRes = await defectAnalysisApi.getOverlayImage(id);
          const blobUrl = URL.createObjectURL(overlayRes.data);
          setOverlayUrl(blobUrl);
        } catch {
          setOverlayUrl(null);
        }
        message.success(`分析完成，检测到 ${d.length} 个缺陷`);
      } catch (err) {
        message.error(`分析失败: ${(err as Error).message}`);
      } finally {
        setLoading(false);
      }
    },
  };

  return (
    <Card title="C扫图像上传与 U-Net 结果叠加">
      <Row gutter={24}>
        <Col span={12}>
          <Upload.Dragger {...uploadProps} disabled={loading}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined style={{ fontSize: 48, color: '#1677ff' }} />
            </p>
            <p className="ant-upload-text">点击或拖拽 C 扫图像到此区域</p>
            <p className="ant-upload-hint">支持 PNG、JPG、BMP、TIFF 格式</p>
          </Upload.Dragger>
          {imageUrl && (
            <div style={{ marginTop: 16 }}>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>原始图像</div>
              <Image src={imageUrl} alt="C扫" style={{ maxHeight: 400 }} />
            </div>
          )}
        </Col>
        <Col span={12}>
          {overlayUrl ? (
            <>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>U-Net 分割叠加结果</div>
              <Image src={overlayUrl} alt="叠加" style={{ maxHeight: 400 }} />
            </>
          ) : (
            <div
              style={{
                height: 200,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#fafafa',
                borderRadius: 8,
                color: '#999',
              }}
            >
              {loading ? '分析中...' : '上传图像后将显示 U-Net 分割叠加结果'}
            </div>
          )}
        </Col>
      </Row>
      {defects.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <DefectTable defects={defects} />
        </div>
      )}
    </Card>
  );
}

export default CScanUploader;

import { useMemo, useRef, useEffect } from 'react';
import { Card } from 'antd';
import type { Defect } from '@/types/api';

interface DefectOverlayProps {
  cScanImage: number[][] | string;
  defects: Defect[];
  width?: number;
  height?: number;
}

const DEFECT_COLORS: Record<string, string> = {
  bubble: 'rgba(255, 77, 79, 0.6)',
  weak_bond: 'rgba(250, 173, 20, 0.6)',
  disbond: 'rgba(245, 34, 45, 0.6)',
  normal: 'rgba(82, 196, 26, 0.4)',
};

function DefectOverlay({
  cScanImage,
  defects,
  width = 600,
  height = 400,
}: DefectOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const imageData = useMemo(() => {
    if (typeof cScanImage === 'string') return null;
    return cScanImage;
  }, [cScanImage]);

  const isImageUrl = typeof cScanImage === 'string';

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = width;
    canvas.height = height;

    if (imageData) {
      const rows = imageData.length;
      const cols = imageData[0]?.length ?? 0;
      const values = imageData.flat().filter((v) => !Number.isNaN(v));
      const min = values.length ? Math.min(...values) : 0;
      const max = values.length ? Math.max(...values) : 1;
      const range = max - min || 1;
      const scaleX = cols > 0 ? width / cols : 1;
      const scaleY = rows > 0 ? height / rows : 1;

      const imgData = ctx.createImageData(width, height);
      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          const col = Math.floor(x / scaleX);
          const row = Math.floor(y / scaleY);
          const val = imageData[row]?.[col] ?? 0;
          const norm = ((val - min) / range) * 255;
          const idx = (y * width + x) * 4;
          imgData.data[idx] = norm;
          imgData.data[idx + 1] = norm;
          imgData.data[idx + 2] = norm;
          imgData.data[idx + 3] = 255;
        }
      }
      ctx.putImageData(imgData, 0, 0);
    } else if (isImageUrl) {
      ctx.clearRect(0, 0, width, height);
    }

    const scaleX = imageData
      ? (imageData[0]?.length ?? 1) > 0
        ? width / (imageData[0]?.length ?? 1)
        : width
      : width;
    const scaleY = imageData
      ? imageData.length > 0
        ? height / imageData.length
        : height
      : height;

    defects.forEach((defect) => {
      const color = DEFECT_COLORS[defect.type] ?? 'rgba(22, 119, 255, 0.5)';
      ctx.fillStyle = color;
      ctx.strokeStyle = color.replace('0.6', '1').replace('0.4', '1');
      ctx.lineWidth = 2;

      if (defect.boundingBox) {
        const { x, y, width: w, height: h } = defect.boundingBox;
        ctx.strokeRect(x * scaleX, y * scaleY, w * scaleX, h * scaleY);
        ctx.fillRect(x * scaleX, y * scaleY, w * scaleX, h * scaleY);
      } else {
        const r = Math.sqrt(defect.area / Math.PI) * 2;
        const cx = defect.centroid.x * scaleX;
        const cy = defect.centroid.y * scaleY;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fill();
      }
    });
  }, [cScanImage, defects, imageData, isImageUrl, width, height]);

  if (isImageUrl) {
    return (
      <Card title="缺陷分割叠加">
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <img
            src={cScanImage}
            alt="C扫图像"
            style={{ width, height, objectFit: 'contain', display: 'block' }}
          />
          <canvas
            ref={canvasRef}
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width,
              height,
              pointerEvents: 'none',
            }}
            width={width}
            height={height}
          />
        </div>
      </Card>
    );
  }

  return (
    <Card title="缺陷分割叠加">
      <canvas
        ref={canvasRef}
        style={{ display: 'block', maxWidth: '100%' }}
        width={width}
        height={height}
      />
    </Card>
  );
}

export default DefectOverlay;

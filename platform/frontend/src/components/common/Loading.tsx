import { Spin } from 'antd';

interface LoadingProps {
  fullScreen?: boolean;
  tip?: string;
}

function Loading({ fullScreen = false, tip = '加载中...' }: LoadingProps) {
  const style: React.CSSProperties = fullScreen
    ? {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(255,255,255,0.8)',
        zIndex: 9999,
      }
    : {
        padding: 48,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      };

  return (
    <div style={style}>
      <Spin size="large" tip={tip} />
    </div>
  );
}

export default Loading;

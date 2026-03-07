import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import type { MenuProps } from 'antd';
import {
  LineChartOutlined,
  ThunderboltOutlined,
  DashboardOutlined,
  PictureOutlined,
  SafetyOutlined,
} from '@ant-design/icons';
import AppHeader from './AppHeader';

const { Sider, Content } = Layout;

const menuItems: MenuProps['items'] = [
  {
    key: '/data',
    icon: <LineChartOutlined />,
    label: '数据可视化',
    children: [
      { key: '/data/waveform', label: 'A扫波形' },
      { key: '/data/spectrum', label: 'FFT频谱' },
      { key: '/data/import', label: '数据导入' },
    ],
  },
  {
    key: '/training',
    icon: <ThunderboltOutlined />,
    label: '模型训练',
  },
  {
    key: '/inference',
    icon: <DashboardOutlined />,
    label: '推理监控',
  },
  {
    key: '/defect',
    icon: <PictureOutlined />,
    label: '缺陷分析',
    children: [
      { key: '/defect/cscan', label: 'C扫上传' },
      { key: '/defect/list', label: '缺陷列表' },
    ],
  },
  {
    key: '/admin',
    icon: <SafetyOutlined />,
    label: '系统管理',
    children: [
      { key: '/admin/audit', label: '审计日志' },
    ],
  },
];

function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const onMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
  };

  const getSelectedKeys = () => {
    const path = location.pathname;
    const keys: string[] = [path];
    const parent = menuItems?.find((item) =>
      item && typeof item === 'object' && 'children' in item &&
      (item.children as { key: string }[])?.some((c: { key: string }) => c.key === path)
    );
    if (parent && typeof parent === 'object' && 'key' in parent) {
      keys.push(parent.key as string);
    }
    return keys;
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={220}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
        }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'flex-start',
            padding: collapsed ? 0 : '0 24px',
            color: 'rgba(255,255,255,0.85)',
            fontSize: collapsed ? 14 : 16,
            fontWeight: 600,
            borderBottom: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          {collapsed ? '监测平台' : '腐蚀与应力在线监测平台 V2.0'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={getSelectedKeys()}
          defaultOpenKeys={['/data', '/defect', '/admin']}
          items={menuItems}
          onClick={onMenuClick}
          style={{ marginTop: 8 }}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 220, transition: 'margin-left 0.2s' }}>
        <AppHeader
          collapsed={collapsed}
          onToggle={() => setCollapsed(!collapsed)}
        />
        <Content
          style={{
            margin: '24px',
            padding: 24,
            minHeight: 280,
            background: '#fff',
            borderRadius: 8,
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

export default AppLayout;

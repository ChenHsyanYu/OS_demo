import React from 'react';
import { Layout, Menu, Breadcrumb } from 'antd';
import { DesktopOutlined, FileOutlined, TeamOutlined, UserOutlined, MessageOutlined } from '@ant-design/icons';
import { useLocation, Link } from 'react-router-dom';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DesktopOutlined />,
      label: <Link to="/">儀表板</Link>,
    },
    {
      key: 'upload',
      icon: <FileOutlined />,
      label: <Link to="/upload">日誌上傳</Link>,
    },
    {
      key: 'alerts',
      icon: <TeamOutlined />,
      label: <Link to="/alerts">警訊中心</Link>,
    },
    {
      key: 'chat',
      icon: <MessageOutlined />,
      label: <Link to="/chat">智能對話</Link>,
    },
  ];

  const getBreadcrumbTitle = () => {
    const pathMap: Record<string, string> = {
      '/': '儀表板',
      '/upload': '日誌上傳',
      '/alerts': '警訊中心',
      '/chat': '智能對話',
      '/alert': '警訊詳情',
    };
    return pathMap[location.pathname] || '首頁';
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Layout.Sider
        breakpoint="lg"
        collapsedWidth={0}
        style={{ background: '#fff' }}
      >
        <div style={{ padding: '16px', textAlign: 'center', fontSize: '18px', fontWeight: 'bold' }}>
          OS 掃毒系統
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname === '/' ? 'dashboard' : location.pathname.substring(1)]}
          items={menuItems}
        />
      </Layout.Sider>

      <Layout>
        <Layout.Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
          <h2 style={{ margin: 0 }}>{getBreadcrumbTitle()}</h2>
        </Layout.Header>

        <Layout.Content style={{ margin: '24px 16px' }}>
          <Breadcrumb style={{ marginBottom: '16px' }}>
            <Breadcrumb.Item>
              <Link to="/">首頁</Link>
            </Breadcrumb.Item>
            <Breadcrumb.Item>{getBreadcrumbTitle()}</Breadcrumb.Item>
          </Breadcrumb>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '2px' }}>
            {children}
          </div>
        </Layout.Content>

        <Layout.Footer style={{ textAlign: 'center', borderTop: '1px solid #f0f0f0' }}>
          OS 掃毒系統 v1.1.0 ©2026
        </Layout.Footer>
      </Layout>
    </Layout>
  );
};

export default AppLayout;

import React from 'react';
import { Layout, Menu, Breadcrumb } from 'antd';
import { DesktopOutlined, FileOutlined, TeamOutlined, MessageOutlined } from '@ant-design/icons';
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
      label: <Link to="/">Dashboard</Link>,
    },
    {
      key: 'upload',
      icon: <FileOutlined />,
      label: <Link to="/upload">Log Upload</Link>,
    },
    {
      key: 'alerts',
      icon: <TeamOutlined />,
      label: <Link to="/alerts">Alert Center</Link>,
    },
    {
      key: 'chat',
      icon: <MessageOutlined />,
      label: <Link to="/chat">AI Chat</Link>,
    },
  ];

  const getBreadcrumbTitle = () => {
    const pathMap: Record<string, string> = {
      '/': 'Dashboard',
      '/upload': 'Log Upload',
      '/alerts': 'Alert Center',
      '/chat': 'AI Chat',
      '/alert': 'Alert Details',
    };
    return pathMap[location.pathname] || 'Home';
  };

  return (
    <Layout style={{ height: '100vh', overflow: 'hidden' }}>
      <Layout.Sider
        breakpoint="lg"
        collapsedWidth={0}
        style={{ background: '#fff' }}
      >
        <div style={{ padding: '16px', textAlign: 'center', fontSize: '18px', fontWeight: 'bold' }}>
          OS Security Scanner
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname === '/' ? 'dashboard' : location.pathname.substring(1)]}
          items={menuItems}
        />
      </Layout.Sider>

      <Layout style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Layout.Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0', flexShrink: 0 }}>
          <h2 style={{ margin: 0 }}>{getBreadcrumbTitle()}</h2>
        </Layout.Header>

        <Layout.Content style={{ margin: '24px 16px', flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Breadcrumb style={{ marginBottom: '16px', flexShrink: 0 }}>
            <Breadcrumb.Item>
              <Link to="/">Home</Link>
            </Breadcrumb.Item>
            <Breadcrumb.Item>{getBreadcrumbTitle()}</Breadcrumb.Item>
          </Breadcrumb>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '2px', flex: 1, overflow: 'auto' }}>
            {children}
          </div>
        </Layout.Content>

        <Layout.Footer style={{ textAlign: 'center', borderTop: '1px solid #f0f0f0', flexShrink: 0 }}>
          OS 掃毒系統 v1.1.0 ©2026
        </Layout.Footer>
      </Layout>
    </Layout>
  );
};

export default AppLayout;

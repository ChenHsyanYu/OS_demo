import React from 'react';
import { Card, Row, Col, Button, Spin, Alert, Empty, Tabs, Table, Drawer } from 'antd';
import { FilterOutlined, DeleteOutlined, FileOutlined } from '@ant-design/icons';
import apiService from '../services/api';
import { Alert as AlertType, LogEvent, SeverityLevel } from '../types';
import { getSeverityColor, formatDate, formatEventType } from '../utils/helpers';

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = React.useState<AlertType[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [selectedAlert, setSelectedAlert] = React.useState<AlertType | null>(null);
  const [drawerVisible, setDrawerVisible] = React.useState(false);
  const [filterSeverity, setFilterSeverity] = React.useState<string | null>(null);

  const fetchAlerts = async (severity?: string) => {
    setLoading(true);
    try {
      const response = await apiService.getAlerts(severity, 100);
      setAlerts(response.data.alerts);
      setError(null);
    } catch (err) {
      setError('無法獲取警訊數據');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchAlerts();
  }, []);

  const handleDeleteAlert = async (alertId: string) => {
    try {
      await apiService.deleteAlert(alertId);
      setAlerts(alerts.filter(a => a.id !== alertId));
    } catch (err) {
      console.error('刪除失敗:', err);
    }
  };

  const handleFilterChange = (severity: string) => {
    setFilterSeverity(severity === 'all' ? null : severity);
    fetchAlerts(severity === 'all' ? undefined : severity);
  };

  const columns = [
    {
      title: '標題',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '嚴重程度',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: SeverityLevel) => (
        <span style={{ color: getSeverityColor(severity), fontWeight: 'bold' }}>
          {severity}
        </span>
      ),
    },
    {
      title: '風險評分',
      dataIndex: 'risk_score',
      key: 'risk_score',
      render: (score: number) => (
        <span style={{ color: score > 70 ? '#ff4d4f' : '#1890ff' }}>
          {score}
        </span>
      ),
    },
    {
      title: '事件數',
      dataIndex: 'event_count',
      key: 'event_count',
    },
    {
      title: '時間',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => formatDate(timestamp),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: AlertType) => (
        <Button.Group>
          <Button
            type="primary"
            size="small"
            onClick={() => {
              setSelectedAlert(record);
              setDrawerVisible(true);
            }}
          >
            詳情
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteAlert(record.id)}
          />
        </Button.Group>
      ),
    },
  ];

  return (
    <Spin spinning={loading}>
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: '16px' }} />}

      <Card
        title="警訊中心"
        extra={
          <Button.Group>
            <Button
              type={filterSeverity === null ? 'primary' : 'default'}
              onClick={() => handleFilterChange('all')}
            >
              全部
            </Button>
            <Button
              type={filterSeverity === 'Critical' ? 'primary' : 'default'}
              danger
              onClick={() => handleFilterChange('Critical')}
            >
              危機
            </Button>
            <Button
              type={filterSeverity === 'High' ? 'primary' : 'default'}
              onClick={() => handleFilterChange('High')}
            >
              高危
            </Button>
            <Button
              type={filterSeverity === 'Medium' ? 'primary' : 'default'}
              onClick={() => handleFilterChange('Medium')}
            >
              中危
            </Button>
          </Button.Group>
        }
      >
        {alerts.length === 0 ? (
          <Empty description="暫無警訊" />
        ) : (
          <Table
            dataSource={alerts}
            columns={columns}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            scroll={{ x: 1200 }}
          />
        )}
      </Card>

      {/* 警訊詳情抽屜 */}
      <Drawer
        title="警訊詳情"
        placement="right"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={600}
      >
        {selectedAlert && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <strong>標題:</strong> {selectedAlert.title}
            </div>
            <div style={{ marginBottom: '16px' }}>
              <strong>嚴重程度:</strong>
              <span
                style={{
                  marginLeft: '8px',
                  color: getSeverityColor(selectedAlert.severity),
                  fontWeight: 'bold',
                }}
              >
                {selectedAlert.severity}
              </span>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <strong>風險評分:</strong> {selectedAlert.risk_score}
            </div>
            <div style={{ marginBottom: '16px' }}>
              <strong>事件數:</strong> {selectedAlert.event_count}
            </div>
            <div style={{ marginBottom: '16px' }}>
              <strong>時間:</strong> {formatDate(selectedAlert.timestamp)}
            </div>

            <Tabs
              items={[
                {
                  key: 'events',
                  label: '相關事件',
                  children: (
                    <div>
                      {selectedAlert.events.map((event, idx) => (
                        <Card key={idx} size="small" style={{ marginBottom: '8px' }}>
                          <div>
                            <strong>類型:</strong> {formatEventType(event.type)}
                          </div>
                          <div>
                            <strong>時間:</strong> {formatDate(event.timestamp)}
                          </div>
                          <div>
                            <strong>來源:</strong> {event.source_file}
                          </div>
                          <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                            {event.raw_log.substring(0, 200)}...
                          </div>
                        </Card>
                      ))}
                    </div>
                  ),
                },
                {
                  key: 'analysis',
                  label: '分析',
                  children: (
                    <div>
                      {selectedAlert.analysis ? (
                        <>
                          <div>
                            <strong>分析:</strong>
                            <p>{selectedAlert.analysis.analysis}</p>
                          </div>
                        </>
                      ) : (
                        <Empty description="暫無分析" />
                      )}
                    </div>
                  ),
                },
              ]}
            />
          </div>
        )}
      </Drawer>
    </Spin>
  );
};

export default AlertsPage;

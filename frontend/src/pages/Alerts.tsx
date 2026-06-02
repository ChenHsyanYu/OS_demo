import React from 'react';
import { Card, Button, Spin, Alert, Empty, Tabs, Table, Drawer } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import apiService from '../services/api';
import { Alert as AlertType, SeverityLevel } from '../types';
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
      setError('Unable to load alert data.');
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
      console.error('Delete failed:', err);
    }
  };

  const handleFilterChange = (severity: string) => {
    setFilterSeverity(severity === 'all' ? null : severity);
    fetchAlerts(severity === 'all' ? undefined : severity);
  };

  const columns = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: SeverityLevel) => (
        <span style={{ color: getSeverityColor(severity), fontWeight: 'bold' }}>
          {severity}
        </span>
      ),
    },
    {
      title: 'Risk Score',
      dataIndex: 'risk_score',
      key: 'risk_score',
      render: (score: number) => (
        <span style={{ color: score > 70 ? '#ff4d4f' : '#1890ff' }}>
          {score}
        </span>
      ),
    },
    {
      title: 'Events',
      dataIndex: 'event_count',
      key: 'event_count',
    },
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => formatDate(timestamp),
    },
    {
      title: 'Actions',
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
            Details
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
        title="Alert Center"
        extra={
          <Button.Group>
            <Button
              type={filterSeverity === null ? 'primary' : 'default'}
              onClick={() => handleFilterChange('all')}
            >
              All
            </Button>
            <Button
              type={filterSeverity === 'Critical' ? 'primary' : 'default'}
              danger
              onClick={() => handleFilterChange('Critical')}
            >
              Critical
            </Button>
            <Button
              type={filterSeverity === 'High' ? 'primary' : 'default'}
              onClick={() => handleFilterChange('High')}
            >
              High
            </Button>
            <Button
              type={filterSeverity === 'Medium' ? 'primary' : 'default'}
              onClick={() => handleFilterChange('Medium')}
            >
              Medium
            </Button>
          </Button.Group>
        }
      >
        {alerts.length === 0 ? (
          <Empty description="No alerts" />
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

      {/* Alert details drawer */}
      <Drawer
        title="Alert Details"
        placement="right"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={600}
      >
        {selectedAlert && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <strong>Title:</strong> {selectedAlert.title}
            </div>
            <div style={{ marginBottom: '16px' }}>
              <strong>Severity:</strong>
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
              <strong>Risk Score:</strong> {selectedAlert.risk_score}
            </div>
            <div style={{ marginBottom: '16px' }}>
              <strong>Events:</strong> {selectedAlert.event_count}
            </div>
            <div style={{ marginBottom: '16px' }}>
              <strong>Time:</strong> {formatDate(selectedAlert.timestamp)}
            </div>

            <Tabs
              items={[
                {
                  key: 'events',
                  label: 'Related Events',
                  children: (
                    <div>
                      {selectedAlert.events.map((event, idx) => (
                        <Card key={idx} size="small" style={{ marginBottom: '8px' }}>
                          <div>
                            <strong>Type:</strong> {formatEventType(event.type)}
                          </div>
                          <div>
                            <strong>Time:</strong> {formatDate(event.timestamp)}
                          </div>
                          <div>
                            <strong>Source:</strong> {event.source_file}
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
                  label: 'Analysis',
                  children: (
                    <div>
                      {selectedAlert.analysis ? (
                        <>
                          <div>
                            <strong>Analysis:</strong>
                            <p>{selectedAlert.analysis.analysis}</p>
                          </div>
                        </>
                      ) : (
                        <Empty description="No analysis yet" />
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

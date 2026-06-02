import React from 'react';
import { Card, Row, Col, Statistic, Button, Spin, Alert } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { ReloadOutlined, RadarChartOutlined } from '@ant-design/icons';
import apiService from '../services/api';
import { Alert as AlertType } from '../types';
import { getSeverityColor, formatDate } from '../utils/helpers';

const DashboardPage: React.FC = () => {
  const [alerts, setAlerts] = React.useState<AlertType[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await apiService.getAlerts(undefined, 20);
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

  // Summary metrics
  const criticalCount = alerts.filter(a => a.severity === 'Critical').length;
  const highCount = alerts.filter(a => a.severity === 'High').length;
  const mediumCount = alerts.filter(a => a.severity === 'Medium').length;
  const totalEvents = alerts.reduce((sum, a) => sum + a.event_count, 0);

  // Risk score distribution
  const riskData = [
    { name: 'Critical', value: criticalCount, color: '#ff4d4f' },
    { name: 'High', value: highCount, color: '#ff7875' },
    { name: 'Medium', value: mediumCount, color: '#ffa940' },
  ].filter(d => d.value > 0);

  // Timeline data
  const timelineData = alerts
    .slice(0, 10)
    .map((alert, idx) => ({
      time: new Date(alert.timestamp).toLocaleTimeString('en-US'),
      risk: alert.risk_score,
      name: alert.title.substring(0, 10),
    }));

  return (
    <Spin spinning={loading}>
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: '16px' }} />}

      {/* Summary cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Critical Alerts"
              value={criticalCount}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="High Alerts"
              value={highCount}
              valueStyle={{ color: '#ff7875' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Medium Alerts"
              value={mediumCount}
              valueStyle={{ color: '#ffa940' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Events"
              value={totalEvents}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="Risk Level Distribution"
            extra={
              <Button icon={<ReloadOutlined />} onClick={fetchAlerts} type="primary" />
            }
          >
            {riskData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p style={{ textAlign: 'center', color: '#999' }}>No data</p>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Risk Score Timeline">
            {timelineData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timelineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="risk"
                    stroke="#8884d8"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p style={{ textAlign: 'center', color: '#999' }}>No data</p>
            )}
          </Card>
        </Col>
      </Row>

      {/* Recent alerts */}
      <Card
        title="Recent Alerts"
        style={{ marginTop: '24px' }}
        extra={
          <Button
            icon={<RadarChartOutlined />}
            onClick={async () => {
              setLoading(true);
              try {
                await apiService.scanSystemLogs();
                await fetchAlerts();
              } catch (err) {
                setError('Scan failed.');
              } finally {
                setLoading(false);
              }
            }}
          >
            Scan System
          </Button>
        }
      >
        {alerts.slice(0, 5).map(alert => (
          <div
            key={alert.id}
            style={{
              padding: '12px',
              marginBottom: '12px',
              borderLeft: `4px solid ${getSeverityColor(alert.severity)}`,
              backgroundColor: '#fafafa',
              borderRadius: '2px',
            }}
          >
            <div style={{ fontWeight: 'bold' }}>{alert.title}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              {formatDate(alert.timestamp)} | Risk Score: {alert.risk_score}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              Events: {alert.event_count}
            </div>
          </div>
        ))}
      </Card>
    </Spin>
  );
};

export default DashboardPage;

import React from 'react';
import { Card, Row, Col, Statistic, Button, Space, Spin, Alert } from 'antd';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
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
      setError('無法獲取警訊數據');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchAlerts();
  }, []);

  // 統計數據
  const criticalCount = alerts.filter(a => a.severity === 'Critical').length;
  const highCount = alerts.filter(a => a.severity === 'High').length;
  const mediumCount = alerts.filter(a => a.severity === 'Medium').length;
  const totalEvents = alerts.reduce((sum, a) => sum + a.event_count, 0);

  // 風險評分分佈
  const riskData = [
    { name: 'Critical', value: criticalCount, color: '#ff4d4f' },
    { name: 'High', value: highCount, color: '#ff7875' },
    { name: 'Medium', value: mediumCount, color: '#ffa940' },
  ].filter(d => d.value > 0);

  // 時間軸數據
  const timelineData = alerts
    .slice(0, 10)
    .map((alert, idx) => ({
      time: new Date(alert.timestamp).toLocaleTimeString('zh-TW'),
      risk: alert.risk_score,
      name: alert.title.substring(0, 10),
    }));

  return (
    <Spin spinning={loading}>
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: '16px' }} />}

      {/* 統計卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="危機警訊"
              value={criticalCount}
              suffix="個"
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="高危警訊"
              value={highCount}
              suffix="個"
              valueStyle={{ color: '#ff7875' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="中危警訊"
              value={mediumCount}
              suffix="個"
              valueStyle={{ color: '#ffa940' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="總事件數"
              value={totalEvents}
              suffix="個"
            />
          </Card>
        </Col>
      </Row>

      {/* 圖表 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="風險級別分佈"
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
              <p style={{ textAlign: 'center', color: '#999' }}>暫無數據</p>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="風險評分時間軸">
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
              <p style={{ textAlign: 'center', color: '#999' }}>暫無數據</p>
            )}
          </Card>
        </Col>
      </Row>

      {/* 最近警訊列表 */}
      <Card
        title="最近警訊"
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
                setError('掃描失敗');
              } finally {
                setLoading(false);
              }
            }}
          >
            掃描系統
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
              {formatDate(alert.timestamp)} | 風險評分: {alert.risk_score}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              事件數: {alert.event_count}
            </div>
          </div>
        ))}
      </Card>
    </Spin>
  );
};

export default DashboardPage;

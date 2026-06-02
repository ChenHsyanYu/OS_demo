import React from 'react';
import {
  Card,
  Upload,
  Spin,
  Alert,
  Progress,
  Table,
  message,
} from 'antd';
import {
  UploadOutlined,
} from '@ant-design/icons';
import apiService from '../services/api';
import { LogEvent } from '../types';
import { formatEventType, formatDate } from '../utils/helpers';

const UploadPage: React.FC = () => {
  const [uploading, setUploading] = React.useState(false);
  const [uploadProgress, setUploadProgress] = React.useState(0);
  const [events, setEvents] = React.useState<LogEvent[]>([]);
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState(false);

  const handleUpload = async (file: File) => {
    setUploading(true);
    setError(null);
    setSuccess(false);
    setUploadProgress(0);

    try {
      // Simulate progress while the backend parses the file.
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await apiService.uploadLog(file);
      clearInterval(progressInterval);
      setUploadProgress(100);

      const data = response.data;
      if (data.status === 'success') {
        setEvents(data.events || []);
        setSuccess(true);
        message.success(`Parsed ${data.events?.length || 0} events successfully.`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please check the file format.');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const columns = [
    {
      title: 'Event ID',
      dataIndex: 'event_id',
      key: 'event_id',
      width: 120,
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => formatEventType(type),
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
    },
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => formatDate(timestamp),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text ? text.substring(0, 50) + (text.length > 50 ? '...' : '') : '-',
    },
  ];

  return (
    <Card title="Log Upload and Analysis">
      <Spin spinning={uploading}>
        {error && (
          <Alert
            message="Upload Failed"
            description={error}
            type="error"
            showIcon
            closable
            style={{ marginBottom: '16px' }}
            onClose={() => setError(null)}
          />
        )}

        {success && (
          <Alert
            message="Upload Successful"
            description={`Parsed ${events.length} security events successfully.`}
            type="success"
            showIcon
            closable
            style={{ marginBottom: '16px' }}
            onClose={() => setSuccess(false)}
          />
        )}

        <div style={{ marginBottom: '24px' }}>
          <Upload.Dragger
            name="file"
            accept=".log,.txt"
            maxCount={1}
            beforeUpload={(file) => {
              // Check file size.
              if (file.size > 50 * 1024 * 1024) {
                message.error('File size cannot exceed 50 MB.');
                return false;
              }
              handleUpload(file);
              return false;
            }}
            disabled={uploading}
          >
            <p style={{ fontSize: '16px', marginBottom: '8px' }}>
              <UploadOutlined />
            </p>
            <p>Drag a log file here, or click to select one.</p>
            <p style={{ fontSize: '12px', color: '#999' }}>
              Supports .log and .txt files up to 50 MB.
            </p>
          </Upload.Dragger>
        </div>

        {uploading && (
          <div style={{ marginBottom: '16px' }}>
            <p>Upload Progress</p>
            <Progress percent={uploadProgress} />
          </div>
        )}

        {events.length > 0 && (
          <div>
            <h3>Parse Results ({events.length} events)</h3>
            <Table
              dataSource={events}
              columns={columns}
              rowKey="event_id"
              pagination={{ pageSize: 10 }}
              size="small"
              scroll={{ x: 1000 }}
            />
          </div>
        )}
      </Spin>
    </Card>
  );
};

export default UploadPage;

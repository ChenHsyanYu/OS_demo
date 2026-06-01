import React from 'react';
import {
  Card,
  Button,
  Upload,
  Spin,
  Alert,
  Progress,
  Empty,
  Table,
  Space,
  message,
} from 'antd';
import {
  UploadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { UploadChangeParam, UploadFile } from 'antd/es/upload/interface';
import apiService from '../services/api';
import { LogEvent } from '../types';
import { formatEventType, formatDate } from '../utils/helpers';

const UploadPage: React.FC = () => {
  const [loading, setLoading] = React.useState(false);
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
      // 模擬進度
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
        message.success(`成功解析 ${data.events?.length || 0} 個事件`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '上傳失敗，請檢查檔案格式');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const columns = [
    {
      title: '事件 ID',
      dataIndex: 'event_id',
      key: 'event_id',
      width: 120,
    },
    {
      title: '類型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => formatEventType(type),
    },
    {
      title: '嚴重程度',
      dataIndex: 'severity',
      key: 'severity',
    },
    {
      title: '時間',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => formatDate(timestamp),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text?.substring(0, 50) + '...' || '-',
    },
  ];

  return (
    <Card title="日誌上傳與分析">
      <Spin spinning={uploading}>
        {error && (
          <Alert
            message="上傳失敗"
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
            message="上傳成功"
            description={`成功解析 ${events.length} 個安全事件`}
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
              // 檢查檔案大小
              if (file.size > 50 * 1024 * 1024) {
                message.error('檔案大小不能超過 50 MB');
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
            <p>拖拽日誌檔案到此，或點擊選擇</p>
            <p style={{ fontSize: '12px', color: '#999' }}>
              支援 .log 和 .txt 格式，最大 50 MB
            </p>
          </Upload.Dragger>
        </div>

        {uploading && (
          <div style={{ marginBottom: '16px' }}>
            <p>上傳進度</p>
            <Progress percent={uploadProgress} />
          </div>
        )}

        {events.length > 0 && (
          <div>
            <h3>解析結果（共 {events.length} 個事件）</h3>
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

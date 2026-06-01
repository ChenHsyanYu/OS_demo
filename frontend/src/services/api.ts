/**
 * API 服務客戶端
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // 掃描端點
  scanSystemLogs() {
    return this.client.post('/api/scan/log');
  }

  // 上傳日誌
  uploadLog(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.client.post('/api/upload/log', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // 獲取警報列表
  getAlerts(severity?: string, limit?: number) {
    return this.client.get('/api/alerts', {
      params: { severity, limit },
    });
  }

  // 獲取警報詳情
  getAlertDetail(alertId: string) {
    return this.client.get(`/api/alerts/${alertId}`);
  }

  // 刪除警報
  deleteAlert(alertId: string) {
    return this.client.delete(`/api/alerts/${alertId}`);
  }

  // 對話接口
  async *chatStream(
    message: string,
    sessionId?: string,
    alertId?: string
  ) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        alert_id: alertId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Chat request failed with status ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Unable to read chat response stream');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          yield JSON.parse(line);
        }
      }

      if (buffer.trim()) {
        yield JSON.parse(buffer);
      }
    } finally {
      reader.releaseLock();
    }
  }

  // 獲取對話會話
  getChatSession(sessionId: string) {
    return this.client.get(`/api/chat/sessions/${sessionId}`);
  }

  // 刪除對話會話
  deleteChatSession(sessionId: string) {
    return this.client.delete(`/api/chat/sessions/${sessionId}`);
  }

  // 健康檢查
  healthCheck() {
    return this.client.get('/api/health');
  }
}

export default new ApiService();

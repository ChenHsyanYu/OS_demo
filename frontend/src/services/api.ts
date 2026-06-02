/**
 * API service client
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

  // Scan endpoint
  scanSystemLogs() {
    return this.client.post('/api/scan/log');
  }

  // Upload log
  uploadLog(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.client.post('/api/upload/log', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // Get alerts
  getAlerts(severity?: string, limit?: number) {
    return this.client.get('/api/alerts', {
      params: { severity, limit },
    });
  }

  // Get alert details
  getAlertDetail(alertId: string) {
    return this.client.get(`/api/alerts/${alertId}`);
  }

  // Delete alert
  deleteAlert(alertId: string) {
    return this.client.delete(`/api/alerts/${alertId}`);
  }

  // Chat endpoint
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

  // Get chat session
  getChatSession(sessionId: string) {
    return this.client.get(`/api/chat/sessions/${sessionId}`);
  }

  // Delete chat session
  deleteChatSession(sessionId: string) {
    return this.client.delete(`/api/chat/sessions/${sessionId}`);
  }

  // Health check
  healthCheck() {
    return this.client.get('/api/health');
  }
}

const apiService = new ApiService();

export default apiService;

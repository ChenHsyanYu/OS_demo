/**
 * 工具函數
 */

import { SeverityLevel } from '../types';

export function getSeverityColor(severity: SeverityLevel): string {
  const colorMap: Record<SeverityLevel, string> = {
    [SeverityLevel.CRITICAL]: '#ff4d4f',
    [SeverityLevel.HIGH]: '#ff7875',
    [SeverityLevel.MEDIUM]: '#ffa940',
    [SeverityLevel.LOW]: '#faad14',
  };
  return colorMap[severity];
}

export function getSeverityLevel(score: number): SeverityLevel {
  if (score >= 90) return SeverityLevel.CRITICAL;
  if (score >= 70) return SeverityLevel.HIGH;
  if (score >= 50) return SeverityLevel.MEDIUM;
  return SeverityLevel.LOW;
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString('zh-TW');
}

export function formatEventType(type: string): string {
  const typeMap: Record<string, string> = {
    'privilege_escalation': '權限提升',
    'anomalous_login': '異常登入',
    'network_anomaly': '網路異常',
    'suspicious_execution': '可疑執行',
    'file_tampering': '檔案竄改',
    'rootkit_signature': 'Rootkit 特徵',
  };
  return typeMap[type] || type;
}

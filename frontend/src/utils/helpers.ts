/**
 * Utility functions
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
  return date.toLocaleString('en-US');
}

export function formatEventType(type: string): string {
  const typeMap: Record<string, string> = {
    'privilege_escalation': 'Privilege Escalation',
    'anomalous_login': 'Anomalous Login',
    'network_anomaly': 'Network Anomaly',
    'suspicious_execution': 'Suspicious Execution',
    'file_tampering': 'File Tampering',
    'rootkit_signature': 'Rootkit Signature',
  };
  return typeMap[type] || type;
}

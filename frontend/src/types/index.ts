/**
 * 類型定義
 */

export enum SeverityLevel {
  CRITICAL = 'Critical',
  HIGH = 'High',
  MEDIUM = 'Medium',
  LOW = 'Low',
}

export enum EventType {
  PRIVILEGE_ESCALATION = 'privilege_escalation',
  ANOMALOUS_LOGIN = 'anomalous_login',
  NETWORK_ANOMALY = 'network_anomaly',
  SUSPICIOUS_EXECUTION = 'suspicious_execution',
  FILE_TAMPERING = 'file_tampering',
  ROOTKIT_SIGNATURE = 'rootkit_signature',
}

export interface LogEvent {
  event_id: string;
  timestamp: string;
  source_file: string;
  type: EventType;
  severity: SeverityLevel;
  raw_log: string;
  description?: string;
}

export interface RiskAssessment {
  event_id: string;
  risk_score: number;
  mitre_tactic?: string;
  mitre_technique?: string;
  cve_references: string[];
  analysis?: string;
  remediation?: string;
  prevention?: string;
}

export interface Alert {
  id: string;
  timestamp: string;
  title: string;
  severity: SeverityLevel;
  risk_score: number;
  event_count: number;
  description?: string;
  events: LogEvent[];
  analysis?: RiskAssessment;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatSession {
  session_id: string;
  messages: ChatMessage[];
  related_alert_id?: string;
  created_at: string;
}

export interface UploadResponse {
  status: string;
  message: string;
  analysis_id?: string;
  events?: LogEvent[];
}

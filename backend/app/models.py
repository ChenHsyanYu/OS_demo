from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SeverityEnum(str, Enum):
    """Event severity"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class EventType(str, Enum):
    """Event type"""
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ANOMALOUS_LOGIN = "anomalous_login"
    NETWORK_ANOMALY = "network_anomaly"
    SUSPICIOUS_EXECUTION = "suspicious_execution"
    FILE_TAMPERING = "file_tampering"
    ROOTKIT_SIGNATURE = "rootkit_signature"


class LogEvent(BaseModel):
    """Log event model"""
    event_id: str
    timestamp: datetime
    source_file: str
    type: EventType
    severity: SeverityEnum
    raw_log: str
    description: Optional[str] = None


class RiskAssessment(BaseModel):
    """Risk assessment model"""
    event_id: str
    risk_score: int = Field(ge=0, le=100)
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    cve_references: List[str] = []
    analysis: Optional[str] = None
    remediation: Optional[str] = None
    prevention: Optional[str] = None


class Alert(BaseModel):
    """Alert model"""
    id: str
    timestamp: datetime
    title: str
    severity: SeverityEnum
    risk_score: int
    event_count: int
    description: Optional[str] = None
    events: List[LogEvent] = []
    analysis: Optional[RiskAssessment] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatSession(BaseModel):
    """Chat session model"""
    session_id: str
    messages: List[ChatMessage] = []
    related_alert_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class UploadResponse(BaseModel):
    """Upload response model"""
    status: str
    message: str
    analysis_id: Optional[str] = None
    events: Optional[List[LogEvent]] = None


class HealthCheck(BaseModel):
    """Health check model"""
    status: str
    ollama_status: str
    version: str

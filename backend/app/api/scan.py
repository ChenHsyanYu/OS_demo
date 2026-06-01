"""
API 路由 - 掃描和分析端點
"""

from fastapi import APIRouter, HTTPException
from typing import List
import os
import subprocess
from datetime import datetime
from app.models import LogEvent, Alert, SeverityEnum
from app.modules.log_parser import LogParser, EventCorrelator
from app.modules.ollama_client import OllamaClient, RiskScorer
from app.config import settings
from app.api.alerts import add_alert

router = APIRouter(prefix="/api/scan", tags=["scan"])

log_parser = LogParser()
correlator = EventCorrelator()
ollama_client = OllamaClient()


@router.post("/log")
async def scan_system_logs() -> dict:
    """
    掃描系統日誌
    
    支援的日誌格式：
    - /var/log/syslog
    - /var/log/auth.log
    - /var/log/kern.log
    - journald (journalctl JSON)
    """
    try:
        events = []
        
        # 支援的日誌檔案
        log_files = [
            "/var/log/syslog",
            "/var/log/messages",
            "/var/log/auth.log",
            "/var/log/kern.log",
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    file_events = log_parser.parse_log_file(log_file)
                    events.extend(file_events)
                except Exception as e:
                    print(f"解析 {log_file} 失敗: {e}")
        
        # 如果可用，也解析 journald
        try:
            result = subprocess.run(
                ["journalctl", "-n", "1000", "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.strip():
                        import json
                        try:
                            json_data = json.loads(line)
                            event = log_parser.parse_json_log(json_data)
                            if event:
                                events.append(event)
                        except:
                            pass
        except:
            pass
        
        # 關聯事件
        event_groups = correlator.correlate_events(events)
        
        # 生成警報
        alerts = []
        for event_group in event_groups:
            if event_group:
                alert = _create_alert(event_group)
                add_alert(alert)
                alerts.append(alert)

        return {
            "status": "success",
            "total_events": len(events),
            "alerts": [a.dict() for a in alerts],
            "scan_time": datetime.now().isoformat(),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _create_alert(event_group: List[LogEvent]) -> Alert:
    """從事件組建立警報"""
    # 計算最高嚴重程度
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    max_severity = min(
        (severity_order.get(e.severity.value, 3) for e in event_group),
        default=3
    )
    severity_map = {0: SeverityEnum.CRITICAL, 1: SeverityEnum.HIGH, 
                   2: SeverityEnum.MEDIUM, 3: SeverityEnum.LOW}
    
    # 計算風險評分
    risk_scores = [
        RiskScorer.calculate_risk_score(e.type.value, e.severity.value)
        for e in event_group
    ]
    avg_risk = int(sum(risk_scores) / len(risk_scores))
    
    alert = Alert(
        id=f"alert_{event_group[0].timestamp.timestamp()}",
        timestamp=event_group[0].timestamp,
        title=f"偵測到 {event_group[0].type.value} 事件",
        severity=severity_map[max_severity],
        risk_score=avg_risk,
        event_count=len(event_group),
        events=event_group,
    )
    
    return alert

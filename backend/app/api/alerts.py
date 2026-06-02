"""
API routes - alert management
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models import Alert, SeverityEnum
from app.modules.ollama_client import OllamaClient
from datetime import datetime
import json

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

ollama_client = OllamaClient()

# Simple in-memory storage; production should use a database.
alerts_store = {}


@router.get("/")
async def get_alerts(severity: str = None, limit: int = 50) -> dict:
    """
    Get the alert list.
    
    Optional filter: severity (Critical/High/Medium/Low).
    """
    try:
        alerts_list = list(alerts_store.values())
        
        # Filter by severity
        if severity:
            alerts_list = [a for a in alerts_list if a.severity == severity]
        
        # Sort by time
        alerts_list.sort(key=lambda a: a.timestamp, reverse=True)
        
        # Limit result count
        alerts_list = alerts_list[:limit]
        
        return {
            "total": len(alerts_list),
            "alerts": [a.dict() for a in alerts_list],
            "timestamp": datetime.now().isoformat(),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}")
async def get_alert_detail(alert_id: str) -> dict:
    """Get alert details"""
    if alert_id not in alerts_store:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    try:
        alert = alerts_store[alert_id]
        
        # Run LLM analysis if it has not been generated yet
        if not alert.analysis:
            analysis_text = ""
            for chunk in ollama_client.generate_analysis(alert.events):
                analysis_text += chunk
            
            # Parse analysis result
            alert.analysis = {
                "analysis": analysis_text[:500],  # Simplified handling
                "risk_score": alert.risk_score,
            }
        
        return alert.dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str) -> dict:
    """Delete an alert"""
    if alert_id in alerts_store:
        del alerts_store[alert_id]
        return {"status": "success", "message": "Alert deleted"}
    
    raise HTTPException(status_code=404, detail="Alert not found")


def add_alert(alert: Alert) -> None:
    """Add an alert to storage"""
    alerts_store[alert.id] = alert

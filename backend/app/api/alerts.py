"""
API 路由 - 警報管理
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models import Alert, SeverityEnum
from app.modules.ollama_client import OllamaClient
from datetime import datetime
import json

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

ollama_client = OllamaClient()

# 簡單的在記憶體存儲（生產環境應使用數據庫）
alerts_store = {}


@router.get("/")
async def get_alerts(severity: str = None, limit: int = 50) -> dict:
    """
    取得警訊列表
    
    可選過濾：severity (Critical/High/Medium/Low)
    """
    try:
        alerts_list = list(alerts_store.values())
        
        # 過濾嚴重程度
        if severity:
            alerts_list = [a for a in alerts_list if a.severity == severity]
        
        # 按時間排序
        alerts_list.sort(key=lambda a: a.timestamp, reverse=True)
        
        # 限制數量
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
    """取得警訊詳情"""
    if alert_id not in alerts_store:
        raise HTTPException(status_code=404, detail="警訊不存在")
    
    try:
        alert = alerts_store[alert_id]
        
        # 如果還沒有分析，執行 LLM 分析
        if not alert.analysis:
            analysis_text = ""
            for chunk in ollama_client.generate_analysis(alert.events):
                analysis_text += chunk
            
            # 解析分析結果
            alert.analysis = {
                "analysis": analysis_text[:500],  # 簡化處理
                "risk_score": alert.risk_score,
            }
        
        return alert.dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str) -> dict:
    """刪除警訊"""
    if alert_id in alerts_store:
        del alerts_store[alert_id]
        return {"status": "success", "message": "警訊已刪除"}
    
    raise HTTPException(status_code=404, detail="警訊不存在")


def add_alert(alert: Alert) -> None:
    """新增警訊到存儲"""
    alerts_store[alert.id] = alert

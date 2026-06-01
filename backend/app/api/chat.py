"""
API 路由 - 對話介面
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.models import ChatMessage, ChatSession
from app.modules.ollama_client import OllamaClient
from app.modules.log_parser import LogParser
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=2)

router = APIRouter(prefix="/api/chat", tags=["chat"])

ollama_client = OllamaClient()
log_parser = LogParser()

# 簡單的在記憶體存儲（生產環境應使用數據庫）
chat_sessions = {}


class ChatRequest(BaseModel):
    """對話請求"""
    session_id: Optional[str] = None
    message: str
    alert_id: Optional[str] = None


@router.post("")
async def chat(request: ChatRequest) -> StreamingResponse:
    """
    LLM 對話端點（串流回應）
    
    支援多輪對話，可結合上傳的日誌進行專項排查
    """
    try:
        # 獲取或建立會話
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        
        if session_id not in chat_sessions:
            chat_sessions[session_id] = ChatSession(
                session_id=session_id,
                related_alert_id=request.alert_id,
            )
        
        session = chat_sessions[session_id]
        
        # 添加用戶消息
        user_msg = ChatMessage(
            role="user",
            content=request.message,
        )
        session.messages.append(user_msg)
        
        # 生成回應流（在 thread pool 執行同步 Ollama 呼叫，避免 block event loop）
        async def async_response_generator():
            loop = asyncio.get_event_loop()
            queue: asyncio.Queue = asyncio.Queue()

            def run_ollama():
                try:
                    context = _build_context(session)
                    full_response = ""
                    for chunk in ollama_client.generate_analysis(
                        events=[],
                        context=context + f"\n\n用戶提問: {request.message}"
                    ):
                        full_response += chunk
                        loop.call_soon_threadsafe(queue.put_nowait, json.dumps({
                            "session_id": session_id,
                            "content": chunk,
                            "timestamp": datetime.now().isoformat(),
                        }) + "\n")

                    if full_response:
                        assistant_msg = ChatMessage(role="assistant", content=full_response)
                        session.messages.append(assistant_msg)
                except Exception as e:
                    loop.call_soon_threadsafe(queue.put_nowait, json.dumps({
                        "error": str(e),
                        "session_id": session_id,
                    }) + "\n")
                finally:
                    loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

            future = loop.run_in_executor(_executor, run_ollama)

            while True:
                item = await queue.get()
                if item is None:
                    break
                yield item

            await future

        return StreamingResponse(async_response_generator(), media_type="application/x-ndjson")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    """獲取對話會話"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="會話不存在")
    
    session = chat_sessions[session_id]
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in session.messages
        ],
        "related_alert_id": session.related_alert_id,
        "created_at": session.created_at.isoformat(),
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict:
    """刪除對話會話"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"status": "success", "message": "會話已刪除"}
    
    raise HTTPException(status_code=404, detail="會話不存在")


def _build_context(session: ChatSession) -> str:
    """構建對話上下文"""
    context = "對話歷史:\n"
    for msg in session.messages[-5:]:  # 最近 5 條消息
        context += f"{msg.role}: {msg.content[:200]}\n"
    
    return context

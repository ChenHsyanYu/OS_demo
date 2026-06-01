"""
API 路由 - 文件上傳和分析
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import UploadResponse
from app.utils.file_handler import FileValidator, FileStorage
from app.modules.log_parser import LogParser, EventCorrelator
from app.modules.ollama_client import RiskScorer
import os
from datetime import datetime

router = APIRouter(prefix="/api/upload", tags=["upload"])

file_validator = FileValidator()
file_storage = FileStorage()
log_parser = LogParser()
correlator = EventCorrelator()


@router.post("/log")
async def upload_log(file: UploadFile = File(...)) -> UploadResponse:
    """
    上傳並解析日誌文件
    
    支援的格式：.log, .txt（最大 50 MB）
    """
    try:
        # 驗證檔案
        content = await file.read()
        is_valid, error_msg = file_validator.validate_upload(file.filename, len(content))
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 檢查 Magic Number
        ext = file.filename.split('.')[-1].lower()
        if not file_validator.check_magic_number(content, ext):
            raise HTTPException(status_code=400, detail="不有效的檔案格式")
        
        # 保存檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_filename = f"{timestamp}_{file.filename}"
        file_path = file_storage.save_upload(saved_filename, content)
        
        # 解析日誌
        events = log_parser.parse_log_file(file_path)
        
        if not events:
            # 嘗試作為單個消息解析
            try:
                decoded = content.decode('utf-8')
                lines = decoded.split('\n')
                for line in lines:
                    if line.strip():
                        event = log_parser._parse_line(line, file.filename)
                        if event:
                            events.append(event)
            except:
                pass
        
        # 關聯事件
        event_groups = correlator.correlate_events(events)
        
        # 計算分析 ID
        analysis_id = f"analysis_{timestamp}"
        
        return UploadResponse(
            status="success",
            message=f"成功解析 {len(events)} 個事件",
            analysis_id=analysis_id,
            events=events,
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上傳處理失敗: {str(e)}")

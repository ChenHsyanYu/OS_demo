"""
API routes - file upload and analysis
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import UploadResponse
from app.utils.file_handler import FileValidator, FileStorage
from app.modules.log_parser import LogParser, EventCorrelator
from app.modules.ollama_client import RiskScorer
from app.api.alerts import add_alert
from app.api.scan import _create_alert
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
    Upload and parse a log file.
    
    Supported formats: .log and .txt, up to 50 MB.
    """
    try:
        # Validate file
        content = await file.read()
        is_valid, error_msg = file_validator.validate_upload(file.filename, len(content))
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Check magic number
        ext = file.filename.split('.')[-1].lower()
        if not file_validator.check_magic_number(content, ext):
            raise HTTPException(status_code=400, detail="Invalid file format")
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_filename = f"{timestamp}_{file.filename}"
        file_path = file_storage.save_upload(saved_filename, content)
        
        # Parse log
        events = log_parser.parse_log_file(file_path)
        
        if not events:
            # Try parsing as individual messages
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
        
        # Correlate events
        event_groups = correlator.correlate_events(events)

        # Create and store alerts
        for event_group in event_groups:
            if event_group:
                alert = _create_alert(event_group)
                add_alert(alert)

        # Generate analysis ID
        analysis_id = f"analysis_{timestamp}"

        return UploadResponse(
            status="success",
            message=f"Parsed {len(events)} events successfully",
            analysis_id=analysis_id,
            events=events,
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")

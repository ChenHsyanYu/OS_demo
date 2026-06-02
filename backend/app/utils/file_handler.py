"""
File handling utilities
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from app.config import settings


class FileValidator:
    """File validator"""
    
    @staticmethod
    def validate_upload(filename: str, file_size: int) -> Tuple[bool, str]:
        """
        Validate an uploaded file.
        
        Returns:
            (is_valid, error_message)
        """
        # Check file size
        if file_size > settings.max_upload_size:
            return False, f"File size exceeds the limit (maximum {settings.max_upload_size / 1024 / 1024} MB)"
        
        # Check file extension
        ext = Path(filename).suffix.lstrip('.').lower()
        if ext not in settings.allowed_extensions:
            return False, f"Unsupported file format. Allowed formats: {', '.join(settings.allowed_extensions)}"
        
        # Check magic number
        return True, ""
    
    @staticmethod
    def check_magic_number(file_bytes: bytes, extension: str) -> bool:
        """Check the file magic number"""
        if extension.lower() == "txt":
            # .txt files should contain readable characters
            try:
                file_bytes.decode('utf-8')
                return True
            except:
                pass
        elif extension.lower() == "log":
            # .log file check
            try:
                file_bytes.decode('utf-8')
                return True
            except:
                pass
        
        return True


class FileStorage:
    """File storage manager"""
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def save_upload(self, filename: str, content: bytes) -> str:
        """Save an uploaded file"""
        file_path = os.path.join(self.upload_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return file_path
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
        
        return False
    
    def cleanup_old_files(self, days: int = 7) -> None:
        """Clean up old files"""
        import time
        current_time = time.time()
        
        for filename in os.listdir(self.upload_dir):
            file_path = os.path.join(self.upload_dir, filename)
            file_age = current_time - os.path.getmtime(file_path)
            
            if file_age > days * 86400:
                self.delete_file(file_path)

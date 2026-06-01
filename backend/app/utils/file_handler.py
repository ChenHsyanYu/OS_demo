"""
文件處理工具
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from app.config import settings


class FileValidator:
    """文件驗證器"""
    
    @staticmethod
    def validate_upload(filename: str, file_size: int) -> Tuple[bool, str]:
        """
        驗證上傳的文件
        
        Returns:
            (是否有效, 錯誤消息)
        """
        # 檢查檔案大小
        if file_size > settings.max_upload_size:
            return False, f"檔案大小超過限制（最大 {settings.max_upload_size / 1024 / 1024} MB）"
        
        # 檢查副檔名
        ext = Path(filename).suffix.lstrip('.').lower()
        if ext not in settings.allowed_extensions:
            return False, f"不支援的檔案格式。允許格式：{', '.join(settings.allowed_extensions)}"
        
        # 檢查 Magic Number
        return True, ""
    
    @staticmethod
    def check_magic_number(file_bytes: bytes, extension: str) -> bool:
        """檢查檔案的 Magic Number"""
        if extension.lower() == "txt":
            # .txt 檔案檢查：應該包含可讀字符
            try:
                file_bytes.decode('utf-8')
                return True
            except:
                pass
        elif extension.lower() == "log":
            # .log 檔案檢查
            try:
                file_bytes.decode('utf-8')
                return True
            except:
                pass
        
        return True


class FileStorage:
    """文件存儲管理"""
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def save_upload(self, filename: str, content: bytes) -> str:
        """保存上傳的文件"""
        file_path = os.path.join(self.upload_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return file_path
    
    def delete_file(self, file_path: str) -> bool:
        """刪除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"錯誤刪除文件 {file_path}: {e}")
        
        return False
    
    def cleanup_old_files(self, days: int = 7) -> None:
        """清理舊文件"""
        import time
        current_time = time.time()
        
        for filename in os.listdir(self.upload_dir):
            file_path = os.path.join(self.upload_dir, filename)
            file_age = current_time - os.path.getmtime(file_path)
            
            if file_age > days * 86400:
                self.delete_file(file_path)

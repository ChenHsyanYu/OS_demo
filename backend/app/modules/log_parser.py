"""
日誌解析模組
支援 Linux 日誌格式：syslog、journald、auditd、auth.log、kern.log
"""

import re
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models import LogEvent, EventType, SeverityEnum


class LogParser:
    """日誌解析器"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """初始化解析規則"""
        return {
            # 權限提升事件
            "privilege_escalation": {
                "patterns": [
                    r"sudo\[.*?\]:\s+.*?COMMAND=",  # sudo 命令執行
                    r"sudo.*?:\s+(.*?)\s+:\s+command\s+not\s+allowed",  # sudo 失敗
                    r"su\[.*?\]:\s+.*?\-\s+(.*?)\s+on",  # su 提升
                ],
                "event_type": EventType.PRIVILEGE_ESCALATION,
                "default_severity": SeverityEnum.MEDIUM,
            },
            # 異常登入
            "anomalous_login": {
                "patterns": [
                    r"Invalid user.*?from\s+(\S+)\s+port",  # SSH 無效用戶
                    r"Failed password for.*?from\s+(\S+)\s+port",  # SSH 密碼失敗
                    r"authentication failure.*?user=(.*?)\s+",  # 認證失敗
                    r"failed.*?sshd.*?port",  # SSH 連線失敗
                ],
                "event_type": EventType.ANOMALOUS_LOGIN,
                "default_severity": SeverityEnum.HIGH,
            },
            # 可疑程式執行
            "suspicious_execution": {
                "patterns": [
                    r"SUID.*?executed",  # SUID 執行
                    r"cron.*?cmd.*?=",  # Cron 任務
                    r"execve.*?name=",  # 程式執行
                ],
                "event_type": EventType.SUSPICIOUS_EXECUTION,
                "default_severity": SeverityEnum.MEDIUM,
            },
            # 網路異常
            "network_anomaly": {
                "patterns": [
                    r"Connection.*?attempt",  # 連線嘗試
                    r"port scan|portscanning",  # 連接埠掃描
                    r"DNS.*?query|query\s+name",  # DNS 查詢
                ],
                "event_type": EventType.NETWORK_ANOMALY,
                "default_severity": SeverityEnum.MEDIUM,
            },
            # 檔案竄改
            "file_tampering": {
                "patterns": [
                    r"file.*?changed|changed\s+\(mode\)|changed\s+\(size\)",  # 檔案變更
                    r"/etc/.*?modified",  # /etc 檔案修改
                    r"/bin/.*?modified|/sbin/.*?modified",  # 二進位修改
                ],
                "event_type": EventType.FILE_TAMPERING,
                "default_severity": SeverityEnum.HIGH,
            },
        }
    
    def parse_log_file(self, file_path: str) -> List[LogEvent]:
        """解析日誌檔案"""
        events = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    event = self._parse_line(line, file_path)
                    if event:
                        events.append(event)
        except Exception as e:
            print(f"Error parsing log file {file_path}: {e}")
        
        return events
    
    def parse_json_log(self, json_data: Dict[str, Any]) -> Optional[LogEvent]:
        """解析 JSON 格式日誌 (journald export)"""
        try:
            timestamp = datetime.fromisoformat(
                json_data.get("__REALTIME_TIMESTAMP", {}).get("__value__", "").replace("Z", "+00:00")
            ) if "__REALTIME_TIMESTAMP" in json_data else datetime.now()
            
            message = json_data.get("MESSAGE", "")
            
            event_type, severity = self._classify_event(message)
            
            event = LogEvent(
                event_id=f"{timestamp.timestamp()}_{json_data.get('__PID__', 'unknown')}",
                timestamp=timestamp,
                source_file="journald",
                type=event_type,
                severity=severity,
                raw_log=json.dumps(json_data),
                description=message,
            )
            return event
        except Exception as e:
            print(f"Error parsing JSON log: {e}")
            return None
    
    def _parse_line(self, line: str, source_file: str) -> Optional[LogEvent]:
        """解析單一行日誌"""
        timestamp = self._extract_timestamp(line)
        event_type, severity = self._classify_event(line)
        
        if event_type == EventType.SUSPICIOUS_EXECUTION:
            # 不是特別的安全事件，可能是誤判
            if not any(keyword in line.lower() for keyword in ["failed", "error", "denied", "invalid"]):
                return None
        
        event_id = f"{timestamp.timestamp()}_{hash(line) % 10000}"
        
        event = LogEvent(
            event_id=event_id,
            timestamp=timestamp,
            source_file=source_file,
            type=event_type,
            severity=severity,
            raw_log=line,
            description=self._extract_description(line),
        )
        
        return event
    
    def _extract_timestamp(self, line: str) -> datetime:
        """提取時間戳"""
        # 嘗試匹配常見的日誌時間格式
        patterns = [
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})",  # ISO format
            r"(\w+\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})",  # 標準 syslog 格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    return datetime.fromisoformat(match.group(1))
                except:
                    pass
        
        return datetime.now()
    
    def _classify_event(self, line: str) -> tuple:
        """分類事件類型和嚴重程度"""
        line_lower = line.lower()
        
        # 掃描所有模式
        for category, config in self.patterns.items():
            for pattern in config["patterns"]:
                if re.search(pattern, line_lower):
                    return config["event_type"], config["default_severity"]
        
        # 預設為低風險
        return EventType.SUSPICIOUS_EXECUTION, SeverityEnum.LOW
    
    def _extract_description(self, line: str) -> str:
        """從日誌行提取描述"""
        # 移除時間戳和主機名
        description = re.sub(r"^\s*\w+\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\S+\s+", "", line)
        description = re.sub(r"^\[.*?\]\s+", "", description)
        return description[:200]  # 限制長度


class EventCorrelator:
    """事件關聯分析"""
    
    @staticmethod
    def correlate_events(events: List[LogEvent]) -> List[List[LogEvent]]:
        """關聯相關事件"""
        # 按時間排序
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        correlated = []
        current_group = []
        last_time = None
        
        for event in sorted_events:
            # 如果時間差超過 5 分鐘，開始新的分組
            if (last_time and 
                (event.timestamp - last_time).total_seconds() > 300):
                if current_group:
                    correlated.append(current_group)
                current_group = []
            
            current_group.append(event)
            last_time = event.timestamp
        
        if current_group:
            correlated.append(current_group)
        
        return correlated

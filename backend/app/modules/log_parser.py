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
                    r"sudo(\[.*?\])?:\s+.*?COMMAND=",  # sudo 命令執行（有無 PID 皆可）
                    r"sudo.*?:\s+(.*?)\s+:\s+command\s+not\s+allowed",  # sudo 失敗
                    r"su(\[.*?\])?:\s+.*?\-\s+(.*?)\s+on",  # su 提升
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
        """解析日誌檔案，自動偵測 auditd 或 syslog 格式"""
        events = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 偵測 auditd 格式
            if 'msg=audit(' in content or 'type=SYSCALL' in content:
                return self.parse_auditd_content(content)

            # syslog 格式逐行解析
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                event = self._parse_line(line, file_path)
                if event:
                    events.append(event)
        except Exception as e:
            print(f"Error parsing log file {file_path}: {e}")

        return events

    def parse_auditd_content(self, content: str) -> List[LogEvent]:
        """解析 auditd 格式的完整內容（ausearch 輸出）"""
        events = []
        blocks = re.split(r'\n?----\n?', content)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            event = self._parse_auditd_block(block)
            if event:
                events.append(event)
        return events

    def _parse_auditd_block(self, block: str) -> Optional[LogEvent]:
        """解析單一 auditd 事件區塊（可能含多行）"""
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        types = []
        fields = {}
        timestamp = None
        raw_lines = []

        for line in lines:
            # ausearch 加的 time-> 行
            time_match = re.match(r'time->(.+)', line)
            if time_match:
                try:
                    timestamp = datetime.strptime(
                        time_match.group(1).strip(), "%a %b %d %H:%M:%S %Y"
                    )
                except Exception:
                    pass
                continue

            # type=XXX msg=audit(ts:seq): ...
            type_match = re.match(r'type=(\w+)\s+msg=audit\((\d+\.\d+):\d+\):\s*(.*)', line)
            if not type_match:
                continue

            record_type = type_match.group(1)
            ts_raw = float(type_match.group(2))
            kv_str = type_match.group(3)

            types.append(record_type)
            raw_lines.append(line)

            if timestamp is None:
                try:
                    timestamp = datetime.fromtimestamp(ts_raw)
                except Exception:
                    pass

            # 解析 key=value（值可能有引號）
            for m in re.finditer(r'(\w+)=(?:"([^"]*)"|([\S]*))', kv_str):
                key = m.group(1)
                value = m.group(2) if m.group(2) is not None else m.group(3)
                if key not in fields:
                    fields[key] = value

        if not types or timestamp is None:
            return None

        event_type, severity, description = self._classify_auditd_block(types, fields)
        if event_type is None:
            return None

        raw_log = ' | '.join(raw_lines[:2])[:500]
        return LogEvent(
            event_id=f"{timestamp.timestamp()}_{hash(raw_log) % 10000}",
            timestamp=timestamp,
            source_file="auditd",
            type=event_type,
            severity=severity,
            raw_log=raw_log,
            description=description,
        )

    def _classify_auditd_block(self, types: List[str], fields: Dict[str, str]):
        """根據 auditd 欄位分類事件"""
        cwd       = fields.get('cwd', '').strip('"')
        proctitle = fields.get('proctitle', '').strip('"')
        argc      = fields.get('argc', '')
        key       = fields.get('key', '').strip('"')
        uid       = fields.get('uid', '')
        gid       = fields.get('gid', '')
        euid      = fields.get('euid', '')

        # CVE-2021-4034：argc=0 是核心特徵
        if 'EXECVE' in types and argc == '0':
            desc = "疑似 CVE-2021-4034 (PwnKit)：pkexec 以空參數執行 (argc=0)"
            if cwd:
                desc += f"，工作目錄：{cwd}"
            return EventType.PRIVILEGE_ESCALATION, SeverityEnum.CRITICAL, desc

        # 從已知 exploit 目錄執行
        if cwd and re.search(r'CVE-\d{4}-\d+|/exploit', cwd, re.IGNORECASE):
            desc = f"從可疑目錄執行程式：{cwd}"
            return EventType.PRIVILEGE_ESCALATION, SeverityEnum.HIGH, desc

        # priv_change：setuid/setgid syscall 成功取得 root
        if key == 'priv_change' and 'SYSCALL' in types:
            if uid == '0' and gid == '0':
                desc = f"完全提權成功（uid=0, gid=0），程式：{proctitle}"
                return EventType.PRIVILEGE_ESCALATION, SeverityEnum.CRITICAL, desc
            if uid == '0' or euid == '0':
                desc = f"權限提升至 root（uid={uid}, euid={euid}），程式：{proctitle}"
                return EventType.PRIVILEGE_ESCALATION, SeverityEnum.HIGH, desc

        # exec_track：可疑程式呼叫 pkexec
        if key == 'exec_track' and 'SYSCALL' in types:
            if proctitle and re.search(r'\./exploit|exploit', proctitle, re.IGNORECASE):
                desc = f"可疑程式透過 pkexec 執行：{proctitle}"
                return EventType.SUSPICIOUS_EXECUTION, SeverityEnum.HIGH, desc

        return None, None, None
    
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
        # ISO format: 2024-01-01T10:00:00
        iso_match = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", line)
        if iso_match:
            try:
                return datetime.fromisoformat(iso_match.group(1))
            except:
                pass

        # syslog format: Jan  1 10:00:00 or Jun  1 10:01:15
        syslog_match = re.search(r"(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})", line)
        if syslog_match:
            try:
                return datetime.strptime(
                    f"{datetime.now().year} {syslog_match.group(1)}",
                    "%Y %b %d %H:%M:%S"
                )
            except:
                pass

        return datetime.now()
    
    def _classify_event(self, line: str) -> tuple:
        """分類事件類型和嚴重程度"""
        line_lower = line.lower()
        
        # 掃描所有模式
        for category, config in self.patterns.items():
            for pattern in config["patterns"]:
                if re.search(pattern, line_lower, re.IGNORECASE):
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

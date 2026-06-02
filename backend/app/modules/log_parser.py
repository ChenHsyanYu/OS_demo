"""
Log parsing module
Supports Linux log formats: syslog, journald, auditd, auth.log, and kern.log.
"""

import re
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models import LogEvent, EventType, SeverityEnum


class LogParser:
    """Log parser"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize parsing rules"""
        return {
            # Privilege escalation events
            "privilege_escalation": {
                "patterns": [
                    r"sudo(\[.*?\])?:\s+.*?COMMAND=",  # sudo command execution, with or without PID
                    r"sudo.*?:\s+(.*?)\s+:\s+command\s+not\s+allowed",  # sudo failure
                    r"su(\[.*?\])?:\s+.*?\-\s+(.*?)\s+on",  # su escalation
                ],
                "event_type": EventType.PRIVILEGE_ESCALATION,
                "default_severity": SeverityEnum.MEDIUM,
            },
            # Anomalous login
            "anomalous_login": {
                "patterns": [
                    r"Invalid user.*?from\s+(\S+)\s+port",  # Invalid SSH user
                    r"Failed password for.*?from\s+(\S+)\s+port",  # Failed SSH password
                    r"authentication failure.*?user=(.*?)\s+",  # Authentication failure
                    r"failed.*?sshd.*?port",  # Failed SSH connection
                ],
                "event_type": EventType.ANOMALOUS_LOGIN,
                "default_severity": SeverityEnum.HIGH,
            },
            # Suspicious program execution
            "suspicious_execution": {
                "patterns": [
                    r"SUID.*?executed",  # SUID execution
                    r"cron.*?cmd.*?=",  # Cron task
                    r"execve.*?name=",  # Program execution
                ],
                "event_type": EventType.SUSPICIOUS_EXECUTION,
                "default_severity": SeverityEnum.MEDIUM,
            },
            # Network anomaly
            "network_anomaly": {
                "patterns": [
                    r"Connection.*?attempt",  # Connection attempt
                    r"port scan|portscanning",  # Port scan
                    r"DNS.*?query|query\s+name",  # DNS query
                ],
                "event_type": EventType.NETWORK_ANOMALY,
                "default_severity": SeverityEnum.MEDIUM,
            },
            # File tampering
            "file_tampering": {
                "patterns": [
                    r"file.*?changed|changed\s+\(mode\)|changed\s+\(size\)",  # File change
                    r"/etc/.*?modified",  # /etc file modification
                    r"/bin/.*?modified|/sbin/.*?modified",  # Binary modification
                ],
                "event_type": EventType.FILE_TAMPERING,
                "default_severity": SeverityEnum.HIGH,
            },
        }
    
    def parse_log_file(self, file_path: str) -> List[LogEvent]:
        """Parse a log file and auto-detect auditd or syslog format"""
        events = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Detect auditd format
            if 'msg=audit(' in content or 'type=SYSCALL' in content:
                return self.parse_auditd_content(content)

            # Parse syslog format line by line
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
        """Parse full auditd content from ausearch output"""
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
        """Parse a single auditd event block, possibly containing multiple lines"""
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        types = []
        fields = {}
        timestamp = None
        raw_lines = []

        for line in lines:
            # time-> line added by ausearch
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

            # Parse key=value fields, where values may be quoted
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
        """Classify an event from auditd fields"""
        cwd       = fields.get('cwd', '').strip('"')
        proctitle = fields.get('proctitle', '').strip('"')
        argc      = fields.get('argc', '')
        key       = fields.get('key', '').strip('"')
        uid       = fields.get('uid', '')
        gid       = fields.get('gid', '')
        euid      = fields.get('euid', '')

        # CVE-2021-4034: argc=0 is a core indicator
        if 'EXECVE' in types and argc == '0':
            desc = "Possible CVE-2021-4034 (PwnKit): pkexec executed with empty arguments (argc=0)"
            if cwd:
                desc += f", working directory: {cwd}"
            return EventType.PRIVILEGE_ESCALATION, SeverityEnum.CRITICAL, desc

        # Execution from a known exploit directory
        if cwd and re.search(r'CVE-\d{4}-\d+|/exploit', cwd, re.IGNORECASE):
            desc = f"Program executed from a suspicious directory: {cwd}"
            return EventType.PRIVILEGE_ESCALATION, SeverityEnum.HIGH, desc

        # priv_change: setuid/setgid syscall successfully obtained root
        if key == 'priv_change' and 'SYSCALL' in types:
            if uid == '0' and gid == '0':
                desc = f"Full privilege escalation succeeded (uid=0, gid=0), program: {proctitle}"
                return EventType.PRIVILEGE_ESCALATION, SeverityEnum.CRITICAL, desc
            if uid == '0' or euid == '0':
                desc = f"Privilege escalated to root (uid={uid}, euid={euid}), program: {proctitle}"
                return EventType.PRIVILEGE_ESCALATION, SeverityEnum.HIGH, desc

        # exec_track: suspicious program called pkexec
        if key == 'exec_track' and 'SYSCALL' in types:
            if proctitle and re.search(r'\./exploit|exploit', proctitle, re.IGNORECASE):
                desc = f"Suspicious program executed through pkexec: {proctitle}"
                return EventType.SUSPICIOUS_EXECUTION, SeverityEnum.HIGH, desc

        return None, None, None
    
    def parse_json_log(self, json_data: Dict[str, Any]) -> Optional[LogEvent]:
        """Parse JSON log format from journald export"""
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
        """Parse a single log line"""
        timestamp = self._extract_timestamp(line)
        event_type, severity = self._classify_event(line)
        
        if event_type == EventType.SUSPICIOUS_EXECUTION:
            # Not a specific security event; likely a false positive
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
        """Extract a timestamp"""
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
        """Classify event type and severity"""
        line_lower = line.lower()
        
        # Scan all patterns
        for category, config in self.patterns.items():
            for pattern in config["patterns"]:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    return config["event_type"], config["default_severity"]
        
        # Default to low risk
        return EventType.SUSPICIOUS_EXECUTION, SeverityEnum.LOW
    
    def _extract_description(self, line: str) -> str:
        """Extract a description from a log line"""
        # Remove timestamp and hostname
        description = re.sub(r"^\s*\w+\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\S+\s+", "", line)
        description = re.sub(r"^\[.*?\]\s+", "", description)
        return description[:200]  # Limit length


class EventCorrelator:
    """Event correlation analysis"""
    
    @staticmethod
    def correlate_events(events: List[LogEvent]) -> List[List[LogEvent]]:
        """Correlate related events"""
        # Sort by time
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        correlated = []
        current_group = []
        last_time = None
        
        for event in sorted_events:
            # Start a new group if the time gap is over 5 minutes
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

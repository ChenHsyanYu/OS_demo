"""
Ollama LLM 客戶端
與本地 Ollama 伺服器進行交互，進行風險評估和分析
"""

import requests
import json
import asyncio
from typing import Generator, Optional, List, Dict, Any
from app.config import settings
from app.models import LogEvent, RiskAssessment


class OllamaClient:
    """Ollama 客戶端"""
    
    def __init__(self):
        self.url = settings.ollama_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
    
    def health_check(self) -> bool:
        """檢查 Ollama 服務狀態"""
        try:
            response = requests.get(
                f"{self.url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def generate_analysis(
        self,
        events: List[LogEvent],
        context: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        生成風險分析（串流）
        """
        # 構建提示詞
        prompt = self._build_system_prompt(events, context)
        
        # 調用 Ollama API
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": "你是一位 Linux 資安專家，提供漏洞分析與排除建議。排除建議不得包含系統升級。",
            "stream": True,
            "options": {
                "temperature": settings.llm_temperature,
                "top_p": settings.llm_top_p,
                "num_predict": settings.llm_max_tokens,
            }
        }
        
        try:
            response = requests.post(
                f"{self.url}/api/generate",
                json=payload,
                stream=True,
                timeout=self.timeout
            )

            if response.status_code != 200:
                try:
                    error_body = response.json()
                except ValueError:
                    error_body = response.text
                raise Exception(
                    f"Ollama API error {response.status_code}: {error_body}"
                )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if data.get("response"):
                        yield data["response"]
        except Exception as e:
            raise Exception(f"Ollama API 錯誤: {str(e)}")
    
    def generate_remediation(self, event: LogEvent) -> str:
        """
        生成修復建議
        """
        prompt = f"""
根據以下 Linux 安全事件，提供具體的排除和預防步驟。

事件類型: {event.type}
嚴重程度: {event.severity}
原始日誌: {event.raw_log}

請提供：
1. 漏洞說明：此攻擊對系統的影響
2. 漏洞原因：可能的入侵途徑
3. 如何排除：具體的修復步驟（禁止包含系統升級）
4. 如何預防：系統加固建議

使用繁體中文回應，並包含具體的 Linux 命令。
"""
        
        try:
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception as e:
            print(f"錯誤: {e}")
        
        return ""
    
    def _build_system_prompt(self, events: List[LogEvent], context: Optional[str] = None) -> str:
        """構建系統提示詞"""
        events_json = json.dumps(
            [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "type": e.type.value,
                    "severity": e.severity.value,
                    "raw_log": e.raw_log,
                    "description": e.description,
                }
                for e in events
            ],
            ensure_ascii=False,
            indent=2
        )
        
        prompt = f"""
請分析以下 Linux 系統日誌事件序列，並進行風險評估。

事件序列（JSON 格式）：
{events_json}

請提供以下分析：
1. 風險評分（0-100）
2. 對應的 MITRE ATT&CK 戰術和技術
3. 相關的 CVE 編號（如有）
4. 詳細的分析說明
5. 具體的排除步驟（禁止包含系統升級指令）
6. 預防建議

使用繁體中文回應，並確保分析內容的一致性。
"""
        
        if context:
            prompt += f"\n\n額外背景信息：\n{context}"
        
        return prompt


class RiskScorer:
    """風險評分器"""
    
    @staticmethod
    def calculate_risk_score(
        event_type: str,
        severity: str,
        frequency: int = 1
    ) -> int:
        """
        計算風險評分
        
        Args:
            event_type: 事件類型
            severity: 嚴重程度
            frequency: 事件頻率
        
        Returns:
            風險評分 (0-100)
        """
        # 基礎分數根據嚴重程度
        base_scores = {
            "Critical": 90,
            "High": 70,
            "Medium": 50,
            "Low": 20,
        }
        
        # 事件類型加權
        type_weights = {
            "privilege_escalation": 1.5,
            "anomalous_login": 1.3,
            "network_anomaly": 1.1,
            "suspicious_execution": 1.2,
            "file_tampering": 1.4,
            "rootkit_signature": 1.8,
        }
        
        base = base_scores.get(severity, 50)
        weight = type_weights.get(event_type, 1.0)
        
        # 根據頻率調整
        frequency_factor = min(1 + (frequency - 1) * 0.1, 1.5)
        
        score = int(base * weight * frequency_factor)
        return min(score, 100)

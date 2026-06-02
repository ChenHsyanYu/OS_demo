"""
Ollama LLM client
Interacts with the local Ollama server for risk assessment and analysis.
"""

import requests
import json
import asyncio
from typing import Generator, Optional, List, Dict, Any
from app.config import settings
from app.models import LogEvent, RiskAssessment


class OllamaClient:
    """Ollama client"""
    
    def __init__(self):
        self.url = settings.ollama_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
    
    def health_check(self) -> bool:
        """Check Ollama service status"""
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
        Generate a risk analysis stream.
        """
        # Build the prompt.
        prompt = self._build_system_prompt(events, context)
        
        # Call the Ollama API.
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": "You are a Linux cybersecurity expert. Provide clear vulnerability analysis and remediation advice, but do not include system upgrades in remediation suggestions. Always respond in English.",
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
            raise Exception(f"Ollama API error: {str(e)}")
    
    def generate_remediation(self, event: LogEvent) -> str:
        """
        Generate remediation guidance.
        """
        prompt = f"""
Based on the following Linux security event, provide specific remediation and prevention steps.

Event type: {event.type}
Severity: {event.severity}
Original log: {event.raw_log}

Please include:
1. Vulnerability description: the impact of this attack on the system
2. Root cause: possible intrusion path
3. Remediation: specific repair steps (do not include system upgrades)
4. Prevention: system hardening recommendations

Describe the event in plain, easy-to-understand language.
Please respond in English and include concrete Linux commands.
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
            print(f"Error: {e}")
        
        return ""
    
    def _build_system_prompt(self, events: List[LogEvent], context: Optional[str] = None) -> str:
        """Build the system prompt"""
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
Please analyze the following Linux system log events and perform a risk assessment.

Event sequence (JSON format):
{events_json}

Provide the following analysis:
1. Risk score (0-100)
2. Relevant MITRE ATT&CK tactics and techniques
3. Related CVE identifiers, if any
4. A detailed explanation of the findings
5. Specific remediation steps (do not include system upgrades)
6. Prevention recommendations

Describe each event in simple, plain language so it is easy to understand.
Please ensure the response is consistent and written in English.
"""
        
        if context:
            prompt += f"\n\nAdditional context:\n{context}"
        
        return prompt


class RiskScorer:
    """Risk scorer"""
    
    @staticmethod
    def calculate_risk_score(
        event_type: str,
        severity: str,
        frequency: int = 1
    ) -> int:
        """
        Calculate the risk score.
        
        Args:
            event_type: Event type
            severity: Severity
            frequency: Event frequency
        
        Returns:
            Risk score (0-100)
        """
        # Base score by severity
        base_scores = {
            "Critical": 90,
            "High": 70,
            "Medium": 50,
            "Low": 20,
        }
        
        # Event type weights
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
        
        # Adjust by frequency
        frequency_factor = min(1 + (frequency - 1) * 0.1, 1.5)
        
        score = int(base * weight * frequency_factor)
        return min(score, 100)

"""CrewAI metering with Primordia receipts."""

from __future__ import annotations
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Callable
from functools import wraps


class PrimordiaMeter:
    """Meter CrewAI crew executions with MSR receipts.

    Example:
        >>> from crewai import Crew
        >>> from crewai_primordia import PrimordiaMeter
        >>>
        >>> meter = PrimordiaMeter(agent_id="my-crew")
        >>> crew = Crew(agents=[...], tasks=[...])
        >>>
        >>> with meter:
        ...     result = crew.kickoff()
        >>>
        >>> print(f"Cost: ${meter.get_total_usd():.4f}")
    """

    def __init__(
        self,
        agent_id: str,
        kernel_url: str = "https://clearing.kaledge.app",
        submit: bool = False,
    ):
        self.agent_id = agent_id
        self.kernel_url = kernel_url
        self.submit = submit
        self.receipts: List[Dict[str, Any]] = []
        self._start_time: Optional[float] = None

    def __enter__(self):
        self._start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._start_time:
            duration = time.time() - self._start_time
            # Create execution receipt
            receipt = {
                "msr_version": "0.1",
                "receipt_id": f"crew_{int(time.time()*1000)}",
                "agent_id": self.agent_id,
                "type": "crew_execution",
                "duration_seconds": duration,
                "timestamp_ms": int(time.time() * 1000),
                "success": exc_type is None,
            }
            receipt["receipt_hash"] = self._hash(receipt)
            self.receipts.append(receipt)

            if self.submit:
                self.flush()

    def track_task(self, task_name: str, cost_usd: float, tokens: int = 0):
        """Manually track a task cost."""
        receipt = {
            "msr_version": "0.1",
            "receipt_id": f"task_{int(time.time()*1000)}",
            "agent_id": self.agent_id,
            "type": "task",
            "task_name": task_name,
            "cost_usd": cost_usd,
            "cost_usd_micros": int(cost_usd * 1_000_000),
            "tokens": tokens,
            "timestamp_ms": int(time.time() * 1000),
        }
        receipt["receipt_hash"] = self._hash(receipt)
        self.receipts.append(receipt)

    def _hash(self, data: Dict) -> str:
        clean = {k: v for k, v in data.items() if k != "receipt_hash"}
        return hashlib.sha256(
            json.dumps(clean, sort_keys=True).encode()
        ).hexdigest()[:32]

    def get_receipts(self) -> List[Dict]:
        return self.receipts.copy()

    def get_total_usd(self) -> float:
        return sum(r.get("cost_usd", 0) for r in self.receipts)

    def flush(self) -> Optional[Dict]:
        if not self.submit or not self.receipts:
            return None
        try:
            import requests
            resp = requests.post(
                f"{self.kernel_url}/v1/index/batch",
                json={"agent_id": self.agent_id, "receipts": self.receipts},
                timeout=30
            )
            if resp.ok:
                self.receipts = []
                return resp.json()
        except Exception:
            pass
        return None


def meter_crew(agent_id: str, submit: bool = False) -> Callable:
    """Decorator to meter a crew execution.

    Example:
        >>> @meter_crew("my-crew")
        ... def run_analysis():
        ...     crew = Crew(...)
        ...     return crew.kickoff()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            meter = PrimordiaMeter(agent_id=agent_id, submit=submit)
            with meter:
                result = func(*args, **kwargs)
            # Attach meter to result for inspection
            if hasattr(result, '__dict__'):
                result._primordia_meter = meter
            return result
        return wrapper
    return decorator

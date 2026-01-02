"""AutoGen wrapper for Primordia metering."""
import hashlib, json, time
from typing import Any, Dict, List

class PrimordiaWrapper:
    def __init__(self, agent_id: str, kernel_url: str = "https://clearing.kaledge.app"):
        self.agent_id = agent_id
        self.kernel_url = kernel_url
        self.receipts: List[Dict] = []

    def track(self, model: str, tokens: int, cost_usd: float):
        receipt = {
            "msr_version": "0.1",
            "agent_id": self.agent_id,
            "model": model,
            "tokens": tokens,
            "cost_usd": cost_usd,
            "cost_usd_micros": int(cost_usd * 1_000_000),
            "timestamp_ms": int(time.time() * 1000),
        }
        receipt["receipt_hash"] = hashlib.sha256(
            json.dumps(receipt, sort_keys=True).encode()
        ).hexdigest()[:32]
        self.receipts.append(receipt)

    def get_total_usd(self) -> float:
        return sum(r.get("cost_usd", 0) for r in self.receipts)

def wrap_agent(agent: Any, agent_id: str) -> Any:
    """Wrap an AutoGen agent with metering."""
    agent._primordia = PrimordiaWrapper(agent_id)
    return agent

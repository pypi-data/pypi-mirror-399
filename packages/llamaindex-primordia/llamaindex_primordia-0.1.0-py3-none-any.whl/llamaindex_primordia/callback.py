"""LlamaIndex callback for Primordia metering."""
import hashlib, json, time
from typing import Any, Dict, List, Optional
from llama_index.core.callbacks import CBEventType, CallbackManager
from llama_index.core.callbacks.base_handler import BaseCallbackHandler

class PrimordiaCallback(BaseCallbackHandler):
    def __init__(self, agent_id: str, kernel_url: str = "https://clearing.kaledge.app"):
        super().__init__(event_starts_to_ignore=[], event_ends_to_ignore=[])
        self.agent_id = agent_id
        self.kernel_url = kernel_url
        self.receipts: List[Dict] = []

    def on_event_end(self, event_type: CBEventType, payload: Optional[Dict] = None, event_id: str = "", **kwargs):
        if event_type == CBEventType.LLM and payload:
            tokens = payload.get("tokens", 0)
            receipt = {
                "msr_version": "0.1",
                "agent_id": self.agent_id,
                "event": str(event_type),
                "tokens": tokens,
                "timestamp_ms": int(time.time() * 1000),
            }
            self.receipts.append(receipt)

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(self, trace_id: Optional[str] = None, trace_map: Optional[Dict] = None) -> None:
        pass

    def get_total_tokens(self) -> int:
        return sum(r.get("tokens", 0) for r in self.receipts)

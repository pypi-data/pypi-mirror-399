"""Primordia callback handler for LangChain."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult


class PrimordiaCallbackHandler(BaseCallbackHandler):
    """Callback handler that emits MSR receipts for LLM usage.

    Tracks costs per LLM call with machine-readable receipts (MSR).
    Shadow mode by default (local only). Set submit=True to index for netting.

    Example:
        >>> from langchain_primordia import PrimordiaCallbackHandler
        >>> handler = PrimordiaCallbackHandler(agent_id="my-agent")
        >>> llm = ChatOpenAI(callbacks=[handler])
        >>> response = llm.invoke("Hello")
        >>> print(f"Cost: ${handler.get_total_usd():.4f}")
        >>> print(f"Receipts: {len(handler.get_receipts())}")

    For settlement (PAID - 5 bps):
        >>> handler = PrimordiaCallbackHandler(
        ...     agent_id="my-agent",
        ...     submit=True,
        ...     kernel_url="https://clearing.kaledge.app"
        ... )
    """

    # Token pricing (USD per 1K tokens) - approximate
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    }

    def __init__(
        self,
        agent_id: str,
        kernel_url: str = "https://clearing.kaledge.app",
        submit: bool = False,
        auto_flush_count: int = 100,
    ):
        """Initialize handler.

        Args:
            agent_id: Your agent identifier
            kernel_url: Primordia kernel URL
            submit: If True, submit receipts to kernel for later netting (PAID)
            auto_flush_count: Auto-flush after this many receipts (if submit=True)
        """
        self.agent_id = agent_id
        self.kernel_url = kernel_url
        self.submit = submit
        self.auto_flush_count = auto_flush_count
        self.receipts: List[Dict[str, Any]] = []
        self._pending_start: Dict[UUID, Dict[str, Any]] = {}

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Track LLM call start."""
        model = serialized.get("kwargs", {}).get("model_name", "unknown")
        self._pending_start[run_id] = {
            "model": model,
            "start_time": time.time(),
            "input_tokens": sum(len(p.split()) * 1.3 for p in prompts),  # Approximate
        }

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Track chat model start."""
        model = serialized.get("kwargs", {}).get("model_name", "unknown")
        # Flatten messages and estimate tokens
        all_content = []
        for msg_list in messages:
            for msg in msg_list:
                if hasattr(msg, "content"):
                    all_content.append(str(msg.content))

        self._pending_start[run_id] = {
            "model": model,
            "start_time": time.time(),
            "input_tokens": sum(len(c.split()) * 1.3 for c in all_content),
        }

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Emit MSR receipt on LLM completion."""
        start_info = self._pending_start.pop(run_id, {})
        model = start_info.get("model", "unknown")
        input_tokens = int(start_info.get("input_tokens", 0))

        # Get token usage from response if available
        token_usage = {}
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})

        input_tokens = token_usage.get("prompt_tokens", input_tokens)
        output_tokens = token_usage.get("completion_tokens", 0)

        if output_tokens == 0:
            # Estimate from response
            for gen_list in response.generations:
                for gen in gen_list:
                    output_tokens += int(len(gen.text.split()) * 1.3)

        # Calculate cost
        pricing = self._get_pricing(model)
        cost_usd = (
            (input_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )
        cost_usd_micros = int(cost_usd * 1_000_000)

        # Create MSR receipt
        receipt = {
            "msr_version": "0.1",
            "receipt_id": f"msr_{run_id.hex[:16]}",
            "agent_id": self.agent_id,
            "provider": self._get_provider(model),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": cost_usd,
            "cost_usd_micros": cost_usd_micros,
            "timestamp_ms": int(time.time() * 1000),
            "metadata": {
                "run_id": str(run_id),
                "parent_run_id": str(parent_run_id) if parent_run_id else None,
            }
        }

        # Add hash
        receipt["receipt_hash"] = self._hash_receipt(receipt)
        self.receipts.append(receipt)

        # Auto-flush if needed
        if self.submit and len(self.receipts) >= self.auto_flush_count:
            self.flush()

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Clean up on error."""
        self._pending_start.pop(run_id, None)

    def _get_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing for model."""
        model_lower = model.lower()
        for key, pricing in self.PRICING.items():
            if key in model_lower:
                return pricing
        return {"input": 0.001, "output": 0.002}  # Default

    def _get_provider(self, model: str) -> str:
        """Infer provider from model name."""
        model_lower = model.lower()
        if "gpt" in model_lower or "o1" in model_lower:
            return "openai"
        elif "claude" in model_lower:
            return "anthropic"
        elif "gemini" in model_lower:
            return "google"
        elif "llama" in model_lower or "mixtral" in model_lower:
            return "meta"
        return "unknown"

    def _hash_receipt(self, receipt: Dict[str, Any]) -> str:
        """Generate receipt hash."""
        # Exclude hash field itself
        data = {k: v for k, v in receipt.items() if k != "receipt_hash"}
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()[:32]

    def get_receipts(self) -> List[Dict[str, Any]]:
        """Get all collected receipts."""
        return self.receipts.copy()

    def get_total_usd(self) -> float:
        """Get total cost in USD."""
        return sum(r.get("cost_usd", 0) for r in self.receipts)

    def get_total_tokens(self) -> int:
        """Get total tokens used."""
        return sum(r.get("total_tokens", 0) for r in self.receipts)

    def flush(self) -> Optional[Dict[str, Any]]:
        """Flush receipts to kernel for indexing.

        Returns:
            Kernel response if submit=True, None otherwise
        """
        if not self.submit or not self.receipts:
            return None

        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests required for submit mode. "
                "Install with: pip install langchain-primordia[submit]"
            )

        response = requests.post(
            f"{self.kernel_url}/v1/index/batch",
            json={
                "agent_id": self.agent_id,
                "receipts": self.receipts
            },
            timeout=30
        )

        if response.ok:
            result = response.json()
            self.receipts = []  # Clear after successful flush
            return result
        else:
            # Keep receipts for retry
            return {"error": response.text, "status": response.status_code}

    def net_receipts(self) -> Dict[str, Any]:
        """Net accumulated receipts into a SIGNED IAN.

        This is the PAID operation (5 bps) that creates a kernel-signed
        Inter-Agent Netting document - the clearing-grade proof of settlement.

        Returns:
            Signed IAN from kernel, or 402 error if no credit
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests required. pip install langchain-primordia[submit]")

        response = requests.post(
            f"{self.kernel_url}/v1/net",
            json={
                "agent_id": self.agent_id,
                "receipts": self.receipts
            },
            timeout=30
        )

        result = response.json()

        if response.status_code == 402:
            # BOOKS OPEN - need credit
            return {
                "error": "BOOKS OPEN - CREDIT REQUIRED",
                "message": "Netting requires credit. Purchase pack to continue.",
                "purchase_url": f"{self.kernel_url}/v1/credit/packs",
                "details": result
            }

        if response.ok:
            self.receipts = []  # Clear after successful netting
            return {
                "signed_ian": result,
                "message": "Kernel-signed IAN created. This is clearing-grade settlement proof."
            }

        return result

    def get_balance_sheet(self) -> Dict[str, Any]:
        """Get audit-grade Machine Balance Sheet (MBS).

        PAID operation - requires pack_team ($25K) minimum.

        Returns:
            Kernel-signed MBS or 402 if insufficient credit
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests required. pip install langchain-primordia[submit]")

        response = requests.post(
            f"{self.kernel_url}/v1/mbs",
            json={"agent_id": self.agent_id},
            timeout=30
        )

        if response.status_code == 402:
            return {
                "error": "PACK_TEAM REQUIRED",
                "message": "MBS requires pack_team ($25K) or higher.",
                "purchase_url": f"{self.kernel_url}/v1/credit/packs"
            }

        return response.json()

    def clear(self) -> None:
        """Clear all receipts without flushing."""
        self.receipts = []

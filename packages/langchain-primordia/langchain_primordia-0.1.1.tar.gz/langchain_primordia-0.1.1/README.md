# langchain-primordia

Economic settlement infrastructure for LangChain agents.

## What is this?

Not just cost tracking. **Clearing-grade settlement** for AI agents.

```
MSR (local receipts)  →  IAN (kernel-signed netting)  →  MBS/ALR (audit-grade)
     FREE                      5 bps                        $25K+
```

## Installation

```bash
pip install langchain-primordia
```

## Quick Start (Shadow Mode - FREE)

```python
from langchain_openai import ChatOpenAI
from langchain_primordia import PrimordiaCallbackHandler

handler = PrimordiaCallbackHandler(agent_id="agent-alpha")
llm = ChatOpenAI(callbacks=[handler])

response = llm.invoke("Hello")

# Local receipts accumulated
print(f"Receipts: {len(handler.get_receipts())}")
print(f"Total: ${handler.get_total_usd():.4f}")
```

## Settlement (PAID - 5 bps)

When you need **proof of settlement** between agents:

```python
handler = PrimordiaCallbackHandler(
    agent_id="agent-alpha",
    submit=True
)

# ... run your agent ...

# Net receipts into kernel-signed IAN
result = handler.net_receipts()

if "signed_ian" in result:
    # This is clearing-grade proof
    # Agent B can verify this signature
    print("IAN signed by Primordia kernel")
else:
    # 402 - need to purchase credit
    print(result["purchase_url"])
```

## Audit-Grade Reports (Enterprise)

```python
# Requires pack_team ($25K) minimum
mbs = handler.get_balance_sheet()

if "error" in mbs:
    # 402 - PACK_TEAM REQUIRED
    print("Purchase pack_team for audit-grade MBS")
else:
    # Kernel-signed Machine Balance Sheet
    print(mbs)
```

## The Rail

| Stage | What | Cost |
|-------|------|------|
| MSR | Local receipt per LLM call | FREE |
| Index | Submit receipts to kernel | FREE |
| **IAN** | **Kernel-signed netting** | **5 bps** |
| MBS | Machine Balance Sheet | $100 (pack_team min) |
| ALR | Agent Liability Report | $100 (pack_team min) |
| Default | Resolution | $25,000 |

## Why Kernel Signature?

```
Agent A: "I paid Agent B $100"
Agent B: "Prove it"
Agent A: shows IAN with Primordia kernel signature
Agent B: verifies signature → TRUST
```

**No kernel signature = no clearing-grade proof.**

## Links

- **Kernel**: https://clearing.kaledge.app
- **Specs**: https://primordia.dev/specs
- **Credit Packs**: POST /v1/credit/packs

## License

MIT

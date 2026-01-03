# Janus Sentinel SDK

[![PyPI](https://img.shields.io/pypi/v/janus-sdk.svg)](https://pypi.org/project/janus-sdk/)

Compliance & policy checks for AI agents. Perform pre-action checks, approvals, and post-action reporting with minimal code.

## Installation
```bash
pip install janus-sdk
```

## Quickstart (sync)
```python
from janus import JanusClient

client = JanusClient(tenant_id="your_tenant_id", api_key="janus_xyz", fail_open=False)

decision = client.check(
    action="payment.process",
    params={"amount": 5000, "currency": "USD"},
    agent_id="payment-bot-01",
)

if decision.allowed:
    process_payment(...)
    client.report(decision, status="success", result={"transaction_id": "tx_123"}, action="payment.process", agent_id="payment-bot-01")
elif decision.requires_approval:
    print(f"Approval required: {decision.reason}")
else:
    print(f"Action denied: {decision.reason}")
```

## Decorators
```python
from janus import JanusClient, janus_guard

client = JanusClient(tenant_id="acme", api_key="janus_xxx")

@janus_guard(client, action="email.send", agent_id="email-bot")
def send_email(to, subject, body):
    return mailer.send(to, subject, body)
```

## Async
```python
from janus import AsyncJanusClient

async def main():
    async with AsyncJanusClient(tenant_id="acme", api_key="janus_xxx") as client:
        res = await client.check("database.drop", params={"table": "users"})
        if res.allowed:
            await client.report(res, status="success", action="database.drop", agent_id="ops-bot")
```

## Docs
- Quickstart & SDK reference live in `docs/janus/` (quickstart, sdk/*, policies/*, compliance/*, operations/*, api/*).\n- Start with `docs/janus/quickstart.md` for a 5-minute setup.\n

## License
MIT

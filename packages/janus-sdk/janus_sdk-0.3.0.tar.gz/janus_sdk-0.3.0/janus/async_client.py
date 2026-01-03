import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, AsyncIterator, Callable

import httpx

from .models import CheckResult, Decision, ApprovalDecision, ApprovalStatus
from .exceptions import JanusError, JanusConnectionError, JanusAuthError, JanusRateLimitError


class AsyncJanusClient:
    """Asynchronous Janus SDK client."""

    DEFAULT_BASE_URL = "https://krystalunity.com"
    DEFAULT_TIMEOUT = 5.0

    def __init__(
        self,
        tenant_id: str,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        fail_open: bool = False,
        retry_count: int = 2,
    ):
        self.tenant_id = tenant_id
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.fail_open = fail_open
        self.retry_count = retry_count

        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "X-Tenant-Id": self.tenant_id,
                "X-API-Key": self.api_key,
                "X-Admin-Token": self.api_key,  # Also send as admin token for approval endpoints
            },
        )

    async def check(self, action: str, params: Dict[str, Any], agent_id: str = "default") -> CheckResult:
        request_id = str(uuid.uuid4())

        for attempt in range(self.retry_count + 1):
            try:
                response = await self._client.post(
                    f"{self.base_url}/api/sentinel/action/check",
                    json={"agent_id": agent_id, "action": action, "params": params},
                )

                if response.status_code == 401:
                    raise JanusAuthError("Invalid API key")
                if response.status_code == 429:
                    if attempt < self.retry_count:
                        continue
                    raise JanusRateLimitError("Rate limit exceeded")
                if response.status_code >= 400:
                    raise JanusError(f"API error: {response.text}")

                data = response.json()
                return CheckResult(
                    decision=Decision(data["decision"]),
                    reason=data.get("reason", ""),
                    policy_id=data.get("policy_id"),
                    latency_ms=data.get("latency_ms", 0),
                    request_id=request_id,
                )

            except httpx.RequestError as exc:
                if attempt < self.retry_count:
                    continue
                if self.fail_open:
                    return CheckResult(
                        decision=Decision.ALLOW,
                        reason="Fail-open: connection error",
                        policy_id=None,
                        latency_ms=0,
                        request_id=request_id,
                    )
                raise JanusConnectionError(f"Connection failed: {exc}")

        raise JanusError("Unknown error")

    async def report(
        self,
        check_result: CheckResult,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        agent_id: str = "default",
        action: Optional[str] = None,
    ) -> None:
        payload = {
            "request_id": check_result.request_id,
            "agent_id": agent_id,
            "action": action or "",
            "status": status,
            "decision": check_result.decision.value,
            "policy_id": check_result.policy_id,
            "result": result,
        }
        try:
            await self._client.post(f"{self.base_url}/api/sentinel/action/report", json=payload)
        except Exception:
            return

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    # =========================================================================
    # Approval Notifications - SSE Stream & Catch-up
    # =========================================================================

    async def get_approvals_since(
        self,
        since: str,
        limit: int = 100,
    ) -> List[ApprovalDecision]:
        """
        Fetch approval decisions since a given timestamp.
        Use this for catch-up when reconnecting or for polling-based integrations.

        Args:
            since: ISO timestamp (e.g., "2025-01-01T00:00:00Z")
            limit: Maximum number of decisions to return (1-500)

        Returns:
            List of ApprovalDecision objects ordered by decided_at ascending
        """
        try:
            response = await self._client.get(
                f"{self.base_url}/api/sentinel/approvals/since",
                params={"tenant_id": self.tenant_id, "since": since, "limit": limit},
            )

            if response.status_code == 401:
                raise JanusAuthError("Invalid API key")
            if response.status_code >= 400:
                raise JanusError(f"API error: {response.text}")

            data = response.json()
            decisions = []
            for d in data.get("decisions", []):
                decisions.append(ApprovalDecision(
                    request_id=d["request_id"],
                    status=ApprovalStatus(d["status"]),
                    approver=d.get("approver"),
                    reason=d.get("reason"),
                    agent_id=d.get("agent_id"),
                    action=d.get("action"),
                    timestamp=d.get("decided_at"),
                    is_catchup=True,
                ))
            return decisions

        except httpx.RequestError as exc:
            raise JanusConnectionError(f"Connection failed: {exc}")

    async def subscribe_approvals(
        self,
        last_seen: Optional[str] = None,
        on_connected: Optional[Callable[[], None]] = None,
    ) -> AsyncIterator[ApprovalDecision]:
        """
        Subscribe to real-time approval decision notifications via SSE.

        This is an async generator that yields ApprovalDecision objects as they arrive.
        The connection is kept alive with heartbeats from the server.

        Args:
            last_seen: Optional ISO timestamp for catch-up. If provided, any decisions
                       made after this timestamp will be sent first before real-time events.
            on_connected: Optional callback invoked when SSE connection is established.

        Yields:
            ApprovalDecision objects as they arrive

        Example:
            async for decision in client.subscribe_approvals(last_seen="2025-01-01T00:00:00Z"):
                if decision.approved:
                    print(f"Request {decision.request_id} was approved!")
                elif decision.rejected:
                    print(f"Request {decision.request_id} was rejected: {decision.reason}")
        """
        url = f"{self.base_url}/api/sentinel/approvals/stream"
        params = {"tenant_id": self.tenant_id}
        if last_seen:
            params["last_seen"] = last_seen

        # Use a separate client for SSE with longer timeout
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(None, connect=10.0),  # No read timeout for SSE
            headers={
                "Accept": "text/event-stream",
                "X-Tenant-Id": self.tenant_id,
                "X-API-Key": self.api_key,
                "X-Admin-Token": self.api_key,  # Admin token for approval endpoints
            },
        ) as sse_client:
            try:
                async with sse_client.stream("GET", url, params=params) as response:
                    if response.status_code == 401:
                        raise JanusAuthError("Invalid API key")
                    if response.status_code >= 400:
                        raise JanusError(f"SSE connection failed: {response.status_code}")

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        # SSE format: "data: {...}" or ": heartbeat ..."
                        if line.startswith(":"):
                            # Heartbeat/comment, ignore
                            continue

                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])  # Skip "data: " prefix
                            except json.JSONDecodeError:
                                continue

                            event_type = data.get("type")

                            if event_type == "CONNECTED":
                                if on_connected:
                                    on_connected()
                                continue

                            if event_type == "ERROR":
                                raise JanusError(f"SSE error: {data.get('message')}")

                            if event_type == "APPROVAL_DECISION":
                                yield ApprovalDecision(
                                    request_id=data["request_id"],
                                    status=ApprovalStatus(data["status"]),
                                    approver=data.get("approver"),
                                    reason=data.get("reason"),
                                    agent_id=data.get("agent_id"),
                                    action=data.get("action"),
                                    timestamp=data.get("timestamp"),
                                    is_catchup=data.get("catchup", False),
                                )

            except httpx.RequestError as exc:
                raise JanusConnectionError(f"SSE connection failed: {exc}")

    async def wait_for_approval(
        self,
        request_id: str,
        timeout_seconds: float = 300,
    ) -> ApprovalDecision:
        """
        Wait for a specific approval request to be decided.

        This is a convenience method that subscribes to the approval stream
        and waits for a decision on the specified request_id.

        Args:
            request_id: The request ID to wait for
            timeout_seconds: Maximum time to wait (default 5 minutes)

        Returns:
            ApprovalDecision when the request is decided

        Raises:
            JanusError: If timeout is exceeded or connection fails
        """
        import asyncio

        start_time = datetime.now()

        # First check if already decided
        try:
            decisions = await self.get_approvals_since(
                since=(datetime.now().replace(hour=0, minute=0, second=0)).isoformat() + "Z"
            )
            for d in decisions:
                if d.request_id == request_id:
                    return d
        except Exception:
            pass  # Fall through to SSE

        async for decision in self.subscribe_approvals():
            if decision.request_id == request_id:
                return decision

            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                raise JanusError(f"Timeout waiting for approval: {request_id}")

        raise JanusError(f"SSE stream ended without decision for: {request_id}")

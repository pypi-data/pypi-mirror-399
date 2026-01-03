import uuid
import json
import time
import threading
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable

import httpx

from .models import CheckResult, Decision, ApprovalDecision, ApprovalStatus
from .exceptions import JanusError, JanusConnectionError, JanusAuthError, JanusRateLimitError, JanusApprovalTimeoutError

_log = logging.getLogger("janus.client")


class JanusClient:
    """Synchronous Janus SDK client with automatic approval callback support."""

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

        self._client = httpx.Client(
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "X-Tenant-Id": self.tenant_id,
                "X-API-Key": self.api_key,
                "X-Admin-Token": self.api_key,  # Also send as admin token for approval endpoints
            },
        )

        # Approval callback infrastructure
        self._approval_callback: Optional[Callable[[ApprovalDecision], None]] = None
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}  # request_id -> metadata
        self._listener_thread: Optional[threading.Thread] = None
        self._listener_stop_event = threading.Event()
        self._listener_started = threading.Event()
        self._last_seen: Optional[str] = None

    def check(self, action: str, params: Dict[str, Any], agent_id: str = "default") -> CheckResult:
        request_id = str(uuid.uuid4())

        for attempt in range(self.retry_count + 1):
            try:
                response = self._client.post(
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
                decision = Decision(data["decision"])
                approval_id = data.get("approval_id") or data.get("request_id")

                result = CheckResult(
                    decision=decision,
                    reason=data.get("reason", ""),
                    policy_id=data.get("policy_id"),
                    latency_ms=data.get("latency_ms", 0),
                    request_id=request_id,
                    approval_id=approval_id if decision == Decision.APPROVAL_REQUIRED else None,
                )

                # Track pending approvals for callback matching
                if result.requires_approval and result.approval_id:
                    self._pending_approvals[result.approval_id] = {
                        "action": action,
                        "agent_id": agent_id,
                        "params": params,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }

                return result

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

        # Should not reach here
        raise JanusError("Unknown error")

    # =========================================================================
    # Blocking Approval Wait (for cron jobs / one-shot scripts)
    # =========================================================================

    def wait_for_approval(
        self,
        approval_id: str,
        timeout: float = 3600,
        poll_interval: float = 5.0,
        max_poll_interval: float = 30.0,
    ) -> ApprovalDecision:
        """
        Block until an approval decision is made (for cron jobs / one-shot scripts).

        This is the synchronous polling alternative to on_approval() callbacks.
        Use this when your script needs to wait for approval before proceeding.

        Args:
            approval_id: The approval_id from CheckResult.approval_id
            timeout: Maximum time to wait in seconds (default 1 hour)
            poll_interval: Initial polling interval in seconds (default 5s)
            max_poll_interval: Maximum polling interval after backoff (default 30s)

        Returns:
            ApprovalDecision with the final status (approved/rejected)

        Raises:
            JanusApprovalTimeoutError: If timeout is reached before decision
            JanusAuthError: If authentication fails
            JanusError: For other API errors

        Example:
            result = client.check("prune_logs", {"days": 30})
            if result.requires_approval:
                print(f"Waiting for approval of {result.approval_id}...")
                decision = client.wait_for_approval(result.approval_id, timeout=3600)
                if decision.approved:
                    prune_logs(days=30)
                else:
                    print(f"Rejected: {decision.reason}")
        """
        start_time = time.time()
        current_interval = poll_interval
        backoff_factor = 1.5

        while True:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise JanusApprovalTimeoutError(
                    f"Approval {approval_id} not decided within {timeout}s timeout"
                )

            try:
                response = self._client.get(
                    f"{self.base_url}/api/sentinel/approval/{approval_id}",
                )

                if response.status_code == 401:
                    raise JanusAuthError("Invalid API key")
                if response.status_code == 404:
                    raise JanusError(f"Approval {approval_id} not found")
                if response.status_code >= 400:
                    raise JanusError(f"API error: {response.text}")

                data = response.json()
                status = data.get("status")

                if status in ("approved", "rejected", "expired"):
                    return ApprovalDecision(
                        request_id=approval_id,
                        status=ApprovalStatus(status),
                        approver=data.get("approver"),
                        reason=data.get("reason"),
                        agent_id=data.get("agent_id"),
                        action=data.get("action"),
                        timestamp=data.get("decided_at"),
                        is_catchup=False,
                    )

                # Still pending - wait and retry with backoff
                _log.debug(f"Approval {approval_id} still pending, waiting {current_interval}s...")
                time.sleep(current_interval)
                current_interval = min(current_interval * backoff_factor, max_poll_interval)

            except httpx.RequestError as exc:
                _log.warning(f"Connection error while polling: {exc}, retrying...")
                time.sleep(current_interval)
                current_interval = min(current_interval * backoff_factor, max_poll_interval)

    def report(
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
            self._client.post(f"{self.base_url}/api/sentinel/action/report", json=payload)
        except Exception:
            # Best-effort; swallow errors
            return

    def close(self) -> None:
        """Close the client and stop any background listeners."""
        self._stop_approval_listener()
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # =========================================================================
    # Approval Callback System - Automatic SSE Listener
    # =========================================================================

    def on_approval(
        self,
        callback: Callable[[ApprovalDecision], None],
        catch_up_hours: int = 24,
    ) -> None:
        """
        Register a callback for approval decisions and start background listener.

        Once registered, the SDK automatically:
        1. Starts a background SSE listener thread
        2. Catches up on any decisions from the last N hours
        3. Fires your callback for each decision (matched to pending requests)

        Args:
            callback: Function called with ApprovalDecision when a decision arrives.
                      Called for ALL decisions, not just pending ones from this client.
            catch_up_hours: Hours of history to catch up on startup (default 24)

        Example:
            def handle_approval(decision):
                if decision.approved:
                    print(f"Request {decision.request_id} approved!")
                else:
                    print(f"Request {decision.request_id} rejected: {decision.reason}")

            client.on_approval(handle_approval)
            result = client.check("deploy", {"model": "gpt-5"})
            # callback fires automatically when admin decides
        """
        self._approval_callback = callback

        # Calculate catch-up timestamp
        catch_up_since = datetime.now(timezone.utc)
        catch_up_since = catch_up_since.replace(
            hour=catch_up_since.hour - catch_up_hours if catch_up_since.hour >= catch_up_hours else 0
        )
        self._last_seen = catch_up_since.isoformat()

        # Start listener if not already running
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_stop_event.clear()
            self._listener_started.clear()
            self._listener_thread = threading.Thread(
                target=self._run_approval_listener,
                daemon=True,
                name="janus-approval-listener",
            )
            self._listener_thread.start()
            # Wait for connection (up to 5 seconds)
            self._listener_started.wait(timeout=5.0)

    def _stop_approval_listener(self) -> None:
        """Stop the background approval listener."""
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_stop_event.set()
            self._listener_thread.join(timeout=2.0)

    def _run_approval_listener(self) -> None:
        """Background thread that listens for approval decisions via SSE."""
        url = f"{self.base_url}/api/sentinel/approvals/stream"
        params = {"tenant_id": self.tenant_id}
        if self._last_seen:
            params["last_seen"] = self._last_seen

        while not self._listener_stop_event.is_set():
            try:
                with httpx.Client(
                    timeout=httpx.Timeout(None, connect=10.0),
                    headers={
                        "Accept": "text/event-stream",
                        "X-Tenant-Id": self.tenant_id,
                        "X-API-Key": self.api_key,
                        "X-Admin-Token": self.api_key,
                    },
                ) as sse_client:
                    with sse_client.stream("GET", url, params=params) as response:
                        if response.status_code == 401:
                            _log.error("Approval listener: Invalid API key")
                            break
                        if response.status_code >= 400:
                            _log.error(f"Approval listener: HTTP {response.status_code}")
                            break

                        for line in response.iter_lines():
                            if self._listener_stop_event.is_set():
                                return

                            if not line:
                                continue

                            if line.startswith(":"):
                                # Heartbeat
                                continue

                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                except json.JSONDecodeError:
                                    continue

                                event_type = data.get("type")

                                if event_type == "CONNECTED":
                                    self._listener_started.set()
                                    _log.debug("Approval listener connected")
                                    continue

                                if event_type == "ERROR":
                                    _log.error(f"Approval listener error: {data.get('message')}")
                                    continue

                                if event_type == "APPROVAL_DECISION":
                                    decision = ApprovalDecision(
                                        request_id=data["request_id"],
                                        status=ApprovalStatus(data["status"]),
                                        approver=data.get("approver"),
                                        reason=data.get("reason"),
                                        agent_id=data.get("agent_id"),
                                        action=data.get("action"),
                                        timestamp=data.get("timestamp"),
                                        is_catchup=data.get("catchup", False),
                                    )

                                    # Update last_seen for reconnection
                                    if decision.timestamp:
                                        self._last_seen = decision.timestamp

                                    # Remove from pending if tracked
                                    self._pending_approvals.pop(decision.request_id, None)

                                    # Fire callback
                                    if self._approval_callback:
                                        try:
                                            self._approval_callback(decision)
                                        except Exception as e:
                                            _log.error(f"Approval callback error: {e}")

            except Exception as e:
                if not self._listener_stop_event.is_set():
                    _log.warning(f"Approval listener disconnected: {e}, reconnecting...")
                    self._listener_stop_event.wait(timeout=2.0)  # Backoff before retry

    def is_listening(self) -> bool:
        """Check if the approval listener is running."""
        return self._listener_thread is not None and self._listener_thread.is_alive()

    def pending_approval_count(self) -> int:
        """Get the number of pending approval requests tracked by this client."""
        return len(self._pending_approvals)

    # =========================================================================
    # Approval Notifications - Catch-up Query (Sync)
    # =========================================================================

    def get_approvals_since(
        self,
        since: str,
        limit: int = 100,
    ) -> List[ApprovalDecision]:
        """
        Fetch approval decisions since a given timestamp.
        Use this for catch-up or polling-based integrations.

        Note: For real-time SSE subscriptions, use AsyncJanusClient.subscribe_approvals()

        Args:
            since: ISO timestamp (e.g., "2025-01-01T00:00:00Z")
            limit: Maximum number of decisions to return (1-500)

        Returns:
            List of ApprovalDecision objects ordered by decided_at ascending
        """
        try:
            response = self._client.get(
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

from .client import JanusClient
from .async_client import AsyncJanusClient
from .models import CheckResult, Decision, ApprovalDecision, ApprovalStatus
from .decorators import janus_guard, openai_guard
from .exceptions import JanusError, JanusConnectionError, JanusAuthError, JanusRateLimitError, JanusApprovalTimeoutError

__all__ = [
    "JanusClient",
    "AsyncJanusClient",
    "CheckResult",
    "Decision",
    "ApprovalDecision",
    "ApprovalStatus",
    "janus_guard",
    "openai_guard",
    "JanusError",
    "JanusConnectionError",
    "JanusAuthError",
    "JanusRateLimitError",
    "JanusApprovalTimeoutError",
]

__version__ = "0.4.0"  # Added wait_for_approval() for cron jobs / one-shot scripts

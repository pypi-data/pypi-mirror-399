from __future__ import annotations

"""Async version of march-history SDK.

Note: Async implementation is partially complete. The async HTTP client and base
infrastructure are ready, but async resources need to be created by copying
sync resources and adding async/await keywords.

For now, use the sync client (MarchHistoryClient) which is fully functional.
"""

from march_history._async.client import AsyncMarchHistoryClient

__all__ = ["AsyncMarchHistoryClient"]

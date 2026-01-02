import logging
from typing import Dict, Any
from openpanel import OpenPanel  # type: ignore
from ..interfaces import APMBackend

logger = logging.getLogger(__name__)


class OpenPanelBackend(APMBackend):
    """
    OpenPanel backend implementation using the official SDK.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ):
        """
        Initialize the OpenPanel SDK.

        Args:
            client_id: The OpenPanel Client ID.
            client_secret: The OpenPanel Client Secret.
        """
        self.op = OpenPanel(client_id, client_secret)

    async def track(self, event: str, properties: Dict[str, Any] | None = None) -> None:
        """
        Track an event using the OpenPanel SDK.
        The SDK's track method is synchronous but non-blocking (queues the event),
        so we can call it directly.
        """
        try:
            self.op.track(event, properties or {})
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("OpenPanel SDK error: %s", e)

    async def close(self) -> None:
        """
        No explicit close exposed by standard introspection, but if there is one,
        we would call it. The SDK likely handles shutdown via atexit or similar.
        """
        pass

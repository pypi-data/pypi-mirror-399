import asyncio
import logging
from typing import Optional, Dict, Any
from .interfaces import APMBackend

logger = logging.getLogger(__name__)


class GlobyAPM:
    """
    Main APM Client.
    """

    _instance: Optional["GlobyAPM"] = None

    def __init__(self, backend: APMBackend):
        self.backend = backend

    @classmethod
    def init(cls, backend: APMBackend) -> "GlobyAPM":
        """
        Initialize the global APM instance.
        """
        cls._instance = cls(backend)
        return cls._instance

    @classmethod
    def get(cls) -> "GlobyAPM":
        """
        Get the global APM instance.
        """
        if cls._instance is None:
            raise RuntimeError(
                "GlobyAPM not initialized. Call GlobyAPM.init(...) first."
            )
        return cls._instance

    async def track(
        self,
        event: str,
        properties: Dict[str, Any] | None = None,
        fire_and_forget: bool = True,
    ) -> None:
        """
        Track an event.

        Args:
            event: The name of the event to track.
            properties: Optional dictionary of properties associated with the event.
            fire_and_forget: If True (default), schedules the request as a background task.
                             If False, awaits the request.
        """
        if fire_and_forget:
            # Schedule task to run in background
            asyncio.create_task(self._track_safe(event, properties))
        else:
            # Await directly
            await self._track_safe(event, properties)

    async def _track_safe(self, event: str, properties: Dict[str, Any] | None) -> None:
        try:
            await self.backend.track(event, properties)
        except Exception as e:  # pylint: disable=broad-exception-caught
            # We catch broad exceptions here to ensure the APM never crashes the main application.
            logger.error("GlobyAPM failed to track event '%s': %s", event, e)

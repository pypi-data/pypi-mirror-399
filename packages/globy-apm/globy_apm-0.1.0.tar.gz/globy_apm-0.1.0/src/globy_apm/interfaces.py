from typing import Protocol, Any, Dict


class APMBackend(Protocol):
    """Interface for APM backends."""

    async def track(self, event: str, properties: Dict[str, Any] | None = None) -> None:
        """
        Track an event.

        Args:
            event: The name of the event to track.
            properties: Optional dictionary of properties associated with the event.
        """

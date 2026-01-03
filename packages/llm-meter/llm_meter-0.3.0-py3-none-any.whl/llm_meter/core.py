import logging
from typing import Any, ClassVar, Optional, cast

from typing_extensions import Self

from llm_meter.context import update_current_context
from llm_meter.providers import registry
from llm_meter.storage.base import StorageEngine
from llm_meter.storage.manager import StorageManager

logger = logging.getLogger(__name__)


class LLMMeter:
    """
    The main entry point for the llm-meter SDK.
    Manages storage, provider instrumentation, and context.
    """

    _instance: ClassVar[Optional["LLMMeter"]] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cast(Self, cls._instance)

    def __init__(
        self,
        storage_url: str = "sqlite+aiosqlite:///llm_usage.db",
        storage_engine: StorageEngine | None = None,
        providers: dict[str, Any] | None = None,
    ) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return

        # DIP: Depend on StorageEngine protocol
        self.storage: StorageEngine = storage_engine or StorageManager(storage_url)
        self.providers_config = providers or {}
        self._initialized = True

    async def initialize(self) -> None:
        """Initialize storage (create tables)."""
        await self.storage.initialize()

    def wrap_client(self, client: Any, provider: str = "openai") -> Any:
        """
        Instruments an LLM client (e.g., OpenAI or AsyncOpenAI).
        Uses a registry to support the Open/Closed Principle.
        """
        instrumenter = registry.get(provider)
        if not instrumenter:
            raise ValueError(f"Provider {provider} not supported. Registered: {registry.list_providers()}")

        return instrumenter.instrument(client, self.storage.record_usage)

    def set_context(self, **kwargs: Any) -> None:
        """Update the current attribution context."""
        update_current_context(**kwargs)

    async def flush_request(self) -> None:
        """
        No-op for now as records are persisted immediately.
        In future versions, this could handle batch flushing.
        """
        pass

    async def shutdown(self) -> None:
        """Close storage connections."""
        await self.storage.close()

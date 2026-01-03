from typing import Protocol

class PolicySyncer(Protocol):
    """
    Interface for policy synchronization.
    """
    async def sync_policies(self) -> None:
        ...


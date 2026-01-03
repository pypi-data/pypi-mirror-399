from typing import Optional, Callable, Any
from pydantic import BaseModel, Field, ConfigDict


class ACLConfig(BaseModel):
    """
    Global configuration for the ACL system.
    """

    external_model_path: Optional[str] = Field(
        default=None,
        description="Path to a custom Casbin model file. "
        "If provided, it will be registered with name 'external'.",
    )
    admin_role: str = Field(
        default="admin", description="Role name that bypasses ownership checks"
    )
    policy_router_enable: bool = Field(
        default=False,
        description="is enable policy router to register and protect the policy router."
        "If enable, you need to pass the app parameter in init() and configure the get_subject function to get the current user identifier.",
    )
    policy_router_prefix: Optional[str] = Field(
        default=None,
        description="The API prefix of the policy router. If None, use the default prefix '/casbin_policies'."
        "Only effective when policy_router_enable=True.",
    )
    get_subject: Optional[Callable[..., Any]] = Field(
        default=None,
        description="The dependency function to get the current user subject, must be compatible with FastAPI Depends mechanism."
        "Must be configured when policy_router_enable=True.",
    )
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection URL for multi-worker policy synchronization. "
        "If provided, enables automatic policy synchronization across all workers. "
        "Example: 'redis://localhost:6379/0'. "
        "When running with multiple workers (e.g., gunicorn), this ensures all workers "
        "reload policies when any worker updates them.",
    )
    policy_sync_channel: str = Field(
        default="fastapi_casbin:policy_update",
        description="Redis Pub/Sub channel name for policy update notifications. "
        "All workers subscribe to this channel to receive policy update notifications.",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

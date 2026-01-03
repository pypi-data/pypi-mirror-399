"""
Async Enforcer Manager for Casbin.

This module provides a centralized manager for multiple Casbin AsyncEnforcer instances,
supporting different permission models for different routes/resources.
"""

import casbin
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .config import ACLConfig
from .exceptions import ACLNotInitialized
from .registry import model_registry

if TYPE_CHECKING:
    from fastapi import FastAPI


class AsyncEnforcerManager:
    """
    Singleton manager for multiple Casbin AsyncEnforcer instances.

    This manager provides centralized access to Casbin AsyncEnforcer instances,
    supporting multiple permission models. Each model has its own enforcer instance,
    allowing different routes to use different permission models.

    Example:
        # Initialize with default models
        await acl.init(adapter)

        # Initialize with specific models
        await acl.init(adapter, models=['rbac', 'abac'])

        # Enforce using a specific model
        allowed = acl.enforce('rbac', user_id, '/api/users', 'read')

        # Enforce using ABAC model with owner check
        allowed = acl.enforce('abac', user_id, '/api/orders/{id}', 'read', owner_id)
    """

    _instance = None

    def __init__(self):
        self._enforcers: Dict[str, casbin.AsyncEnforcer] = {}
        self._adapters: Dict[str, Any] = {}
        self._config: Optional[ACLConfig] = None
        self._initialized: bool = False
        self._watcher: Optional[Any] = None  # RedisPolicyWatcher instance
        self._api_name_map: Dict[str, str] = {}  # api_name -> route_path mapping

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AsyncEnforcerManager, cls).__new__(cls)
        return cls._instance

    async def init(
        self,
        adapter: Any,
        models: Optional[List[str]] = None,
        config: Optional[ACLConfig] = None,
        app: Optional["FastAPI"] = None,
    ) -> None:
        """
        Initialize AsyncEnforcer instances for the specified models.

        :param adapter: Casbin async adapter (e.g. SQLModelAdapter). All models share the same adapter.
        :param models: List of model names to initialize. If None, initializes the default model from config.
        :param config: ACLConfig instance. If None, creates a default one.
        :param app: Optional FastAPI application instance. Required if policy_router_enable=True.
                     If provided and policy_router_enable=True, the policy router will be automatically registered.
        """
        # Create default config if not provided
        if config is None:
            config = ACLConfig()

        self._config = config

        # If external_model_path is provided, register it
        if config.external_model_path:
            model_registry.register("external", config.external_model_path)

        # Determine which models to initialize
        if models is None:
            # Initialize only the default model
            models_to_init = ["permission_rbac"]
        else:
            models_to_init = models

        # Initialize enforcer for each model
        for model_name in models_to_init:
            await self._init_model(model_name, adapter)

        # Build api_name mapping table if app is provided
        if app is not None:
            self._build_api_name_map(app)
        else:
            import warnings

            warnings.warn(
                "app parameter not provided. API name-based permission matching "
                "will not be available. Consider passing app parameter to init() "
                "for better performance.",
                UserWarning,
            )

        # if policy router is enabled, do related settings
        if self._config.policy_router_enable:

            # if app is provided, automatically register router
            if app is not None:
                from .router import casbin_router

                # determine prefix: use the configured prefix first, otherwise use the default value
                prefix = self._config.policy_router_prefix or "/casbin_policies"
                app.include_router(casbin_router, prefix=prefix)
            elif self._config.get_subject is None:
                # if router is enabled but app and get_subject are not provided, give a warning
                # in this case, the user needs to manually register the router
                import warnings

                warnings.warn(
                    "policy_router_enable=True but app parameter not provided. "
                    "You need to manually register the router using app.include_router(casbin_router).",
                    UserWarning,
                )

        # Initialize Redis watcher for multi-worker synchronization
        if self._config.redis_url:
            from .watcher import RedisPolicyWatcher

            self._watcher = RedisPolicyWatcher(
                redis_url=self._config.redis_url,
                channel=self._config.policy_sync_channel,
                reload_callback=self.load_policy,
            )
            await self._watcher.start()

        self._initialized = True

    async def _init_model(self, model_name: str, adapter: Any) -> None:
        """
        Initialize an enforcer for a specific model.

        :param model_name: Name of the model to initialize
        :param adapter: Casbin async adapter
        """
        # Skip if already initialized
        if model_name in self._enforcers:
            return

        # Get model path from registry
        model_path = model_registry.get_path(model_name)

        # Create enforcer
        enforcer = casbin.AsyncEnforcer(model_path, adapter)
        await enforcer.load_policy()

        self._enforcers[model_name] = enforcer
        self._adapters[model_name] = adapter

    async def init_model(self, model_name: str, adapter: Optional[Any] = None) -> None:
        """
        Initialize or reinitialize an enforcer for a specific model at runtime.

        This allows adding new models after the initial init() call.

        :param model_name: Name of the model to initialize
        :param adapter: Casbin async adapter. If None, uses the adapter from the first initialized model.
        """
        if adapter is None:
            if not self._adapters:
                raise ACLNotInitialized(
                    "No adapter available. Call init() first or provide an adapter."
                )
            # Use the first available adapter
            adapter = next(iter(self._adapters.values()))

        await self._init_model(model_name, adapter)

    def get_enforcer(self, model_name: str) -> casbin.AsyncEnforcer:
        """
        Get the AsyncEnforcer instance for a specific model.

        :param model_name: Name of the model
        :return: AsyncEnforcer instance
        :raises ACLNotInitialized: If the model has not been initialized
        """
        if model_name not in self._enforcers:
            available = ", ".join(self._enforcers.keys()) if self._enforcers else "none"
            raise ACLNotInitialized(
                f"Model '{model_name}' not initialized. "
                f"Available models: {available}. "
                f"Call await acl.init(adapter, models=['{model_name}']) first."
            )
        return self._enforcers[model_name]

    @property
    def enforcer(self) -> casbin.AsyncEnforcer:
        """
        Get the default AsyncEnforcer instance.

        This property provides backward compatibility and returns the enforcer
        for the default model specified in config.

        :return: AsyncEnforcer instance for the default model
        :raises ACLNotInitialized: If the enforcer has not been initialized
        """
        if not self._initialized or not self._config:
            raise ACLNotInitialized(
                "AsyncEnforcerManager is not initialized. Call await acl.init() first."
            )
        return self.get_enforcer("permission_rbac")

    @property
    def config(self) -> ACLConfig:
        """
        Get the ACLConfig instance.

        :raises ACLNotInitialized: If the enforcer has not been initialized
        """
        if self._config is None:
            raise ACLNotInitialized(
                "AsyncEnforcerManager is not initialized. Call await acl.init() first."
            )
        return self._config

    def enforce(self, model_name: str, *args) -> bool:
        """
        Execute the Casbin enforce method using the specified model.

        Note: enforce is synchronous even in AsyncEnforcer as it operates on in-memory policies.

        :param model_name: Name of the model to use for enforcement
        :param args: Arguments to pass to enforce (sub, obj, act, ...)
        :return: True if access is allowed, False otherwise
        """
        enforcer = self.get_enforcer(model_name)
        return enforcer.enforce(*args)

    def is_model_initialized(self, model_name: str) -> bool:
        """
        Check if a model has been initialized.

        :param model_name: Name of the model
        :return: True if the model is initialized, False otherwise
        """
        return model_name in self._enforcers

    def list_initialized_models(self) -> List[str]:
        """
        List all initialized model names.

        :return: List of initialized model names
        """
        return list(self._enforcers.keys())

    async def load_policy(self, model_name: Optional[str] = None) -> None:
        """
        Reload policies from the adapter.

        :param model_name: Name of the model to reload. If None, reloads all models.
        """
        if model_name:
            enforcer = self.get_enforcer(model_name)
            await enforcer.load_policy()
        else:
            for enforcer in self._enforcers.values():
                await enforcer.load_policy()

    async def save_policy(self, model_name: Optional[str] = None) -> None:
        """
        Save policies to the adapter.

        :param model_name: Name of the model to save. If None, saves all models.
        """
        if model_name:
            enforcer = self.get_enforcer(model_name)
            await enforcer.save_policy()
        else:
            for enforcer in self._enforcers.values():
                await enforcer.save_policy()

    async def notify_policy_update(self, model_name: Optional[str] = None) -> None:
        """
        Notify all workers that policies have been updated.

        This method publishes a notification to Redis (if configured) to trigger
        policy reload in all workers. This is essential for multi-worker deployments
        (e.g., gunicorn) to ensure all workers have consistent policy state.

        :param model_name: Optional model name to reload. If None, all models are reloaded.
        """
        if self._watcher:
            await self._watcher.notify_update(model_name)

    def _build_api_name_map(self, app: "FastAPI") -> None:
        """
        Build api_name mapping table from FastAPI routes.

        This method scans all APIRoute instances in the FastAPI app and builds
        a mapping from route names (api_name) to route paths. Route names are
        determined by the route.name attribute, which FastAPI automatically
        sets to the function name if not explicitly provided.

        :param app: FastAPI application instance
        :raises ValueError: If duplicate api_name is found
        """
        from fastapi.routing import APIRoute

        self._api_name_map.clear()

        for route in app.routes:
            if isinstance(route, APIRoute):
                # Skip documentation routes
                if route.path in ["/docs", "/redoc", "/openapi.json"]:
                    continue

                # Get route name (FastAPI uses function name as default)
                api_name = route.name

                # Check for duplicates
                if api_name in self._api_name_map:
                    raise ValueError(
                        f"Duplicate api_name '{api_name}' found. "
                        f"Route 1: {self._api_name_map[api_name]}, "
                        f"Route 2: {route.path}. "
                        "Please explicitly set unique names for routes using the 'name' parameter."
                    )

                self._api_name_map[api_name] = route.path

    def get_api_name_map(self) -> Dict[str, str]:
        """
        Get the api_name to route_path mapping table.

        :return: Dictionary mapping api_name to route_path
        """
        return self._api_name_map.copy()

    async def shutdown(self) -> None:
        """
        Shutdown the enforcer manager and clean up resources.

        This should be called when the application is shutting down to properly
        stop the Redis watcher and close connections.
        """
        if self._watcher:
            await self._watcher.stop()
            self._watcher = None


# Global accessor
acl = AsyncEnforcerManager()

"""Router proxy class for convenient router access and operations.

This module provides a Router proxy class that makes it easy to reference
and interact with routers in a workspace.

Example:
    >>> from mixtrain import get_router, Router
    >>> router = get_router("my-router")
    >>> result = router.route({"user": {"tier": "premium"}})
    >>> print(result.matched_rule.name)
"""

import logging
from typing import Any, Dict, List, Optional

from .client import MixClient
from .helpers import validate_resource_name
from .routing.engine import RoutingEngine, RoutingEngineFactory
from .routing.models import RoutingResult

logger = logging.getLogger(__name__)


class Router:
    """Proxy class for convenient router access and operations.

    This class provides a clean, object-oriented interface for working with
    routers. The RoutingEngine is used internally for routing evaluation.

    Args:
        name: Name of the router
        client: Optional MixClient instance (creates new one if not provided)

    Attributes:
        name: Router name
        client: MixClient instance for API operations

    Example:
        >>> router = Router("my-router")
        >>> result = router.route({"user": {"tier": "premium"}})
        >>> print(result.matched_rule.name)
        >>> print(router.rules)
    """

    def __init__(self, name: str, client: Optional[MixClient] = None):
        """Initialize Router proxy.

        Args:
            name: Name of the router
            client: Optional MixClient instance (creates new one if not provided)

        Raises:
            ValueError: If name is invalid (must be lowercase alphanumeric with hyphens/underscores)
        """
        validate_resource_name(name, "router")
        self.name = name
        self.client = client or MixClient()
        self._config: Optional[Dict[str, Any]] = None
        self._engine: RoutingEngine = self._create_engine()  # Eager load

    def _create_engine(self) -> RoutingEngine:
        """Internal: Create routing engine from fetched config."""
        config = self._fetch_config()
        return RoutingEngineFactory.from_json(config)

    def _fetch_config(self, version: Optional[int] = None) -> Dict[str, Any]:
        """Internal: Fetch config directly via HTTP."""
        params = {"version": version} if version else None
        response = self.client._make_request(
            "GET",
            f"/workspaces/{self.client._workspace_name}/inference/routers/{self.name}",
            params=params,
        )
        config = response.json()
        # Cache the config
        if version is None:
            self._config = config
        return config

    # === Properties ===

    @property
    def config(self) -> Dict[str, Any]:
        """Get current router configuration (cached).

        Returns:
            Full router configuration including rules, metadata, etc.

        Example:
            >>> router = Router("my-router")
            >>> print(router.config["description"])
        """
        if self._config is None:
            self._config = self._fetch_config()
        return self._config

    @property
    def rules(self) -> List[Dict[str, Any]]:
        """Get current routing rules (shortcut to config['rules']).

        Returns:
            List of routing rules

        Example:
            >>> router = Router("my-router")
            >>> for rule in router.rules:
            ...     print(f"{rule['name']}: priority {rule['priority']}")
        """
        return self.config.get("rules", [])

    @property
    def versions(self) -> List[Dict[str, Any]]:
        """Get all configuration versions.

        Returns:
            List of version records with version number, created_at, etc.

        Example:
            >>> router = Router("my-router")
            >>> for v in router.versions:
            ...     print(f"Version {v['version']}: {v['change_message']}")
        """
        response = self.client._make_request(
            "GET",
            f"/workspaces/{self.client._workspace_name}/inference/routers/{self.name}/versions",
        )
        return response.json().get("versions", [])

    @property
    def active_version(self) -> Optional[int]:
        """Get currently deployed version number.

        Returns:
            Active version number or None if not deployed

        Example:
            >>> router = Router("my-router")
            >>> print(f"Active version: {router.active_version}")
        """
        return self.config.get("active_version")

    # === Core Operations ===

    def route(self, request_data: Dict[str, Any]) -> RoutingResult:
        """Route a request using the eager-loaded routing engine.

        Args:
            request_data: The request data to route (e.g., user info, model name)

        Returns:
            RoutingResult with matched rule, selected targets, and explanation

        Example:
            >>> router = Router("my-router")
            >>> result = router.route({"user": {"tier": "premium"}})
            >>> if result.matched_rule:
            ...     print(f"Matched: {result.matched_rule.name}")
            ...     for target in result.selected_targets:
            ...         print(f"  -> {target.endpoint}")
        """
        return self._engine.route_request(request_data)

    # === CRUD Operations ===

    def update(
        self,
        rules: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        change_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update router configuration (creates a new version).

        Args:
            rules: Optional new rules list
            description: Optional new description
            settings: Optional deployment settings (inference_uri, update_uri)
            change_message: Optional change summary message

        Returns:
            Updated router configuration

        Example:
            >>> router = Router("my-router")
            >>> router.update(
            ...     rules=[...],
            ...     change_message="Added premium tier rule"
            ... )
        """
        payload: Dict[str, Any] = {}
        if description is not None:
            payload["description"] = description
        if settings is not None:
            payload["settings"] = settings
        if rules is not None:
            payload["rules"] = rules
            if change_message:
                payload["change_message"] = change_message

        response = self.client._make_request(
            "PUT",
            f"/workspaces/{self.client._workspace_name}/inference/routers/{self.name}",
            json=payload,
        )
        # Refresh config and engine
        self.refresh()
        return response.json()

    def deploy(self, version: Optional[int] = None) -> Dict[str, Any]:
        """Deploy/activate a router configuration version.

        This sets the specified version as the active deployment and
        notifies the router's update_uri (if configured) to reload config.

        Args:
            version: Optional specific version to deploy (defaults to latest)

        Returns:
            Deployment result with version info

        Example:
            >>> router = Router("my-router")
            >>> router.deploy()  # Deploy latest
            >>> router.deploy(version=3)  # Deploy specific version
        """
        payload: Dict[str, Any] = {}
        if version is not None:
            payload["version"] = version

        response = self.client._make_request(
            "POST",
            f"/workspaces/{self.client._workspace_name}/inference/routers/{self.name}/activate",
            json=payload,
        )
        # Refresh config
        self.refresh()
        return response.json()

    def delete(self) -> Dict[str, Any]:
        """Delete this router and all its versions.

        Returns:
            Deletion result

        Example:
            >>> router = Router("my-router")
            >>> router.delete()
        """
        response = self.client._make_request(
            "DELETE",
            f"/workspaces/{self.client._workspace_name}/inference/routers/{self.name}",
        )
        return response.json()

    # === Request History ===

    def list_requests(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        matched_rule: Optional[str] = None,
        response_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List routed requests with pagination and filtering.

        Args:
            limit: Maximum number of requests to return (default: 20)
            offset: Number of requests to skip (for pagination)
            status: Filter by status (e.g., "completed", "failed")
            matched_rule: Filter by matched rule name
            response_code: Filter by response code (e.g., "200", "4xx", "5xx")

        Returns:
            Dict with 'requests' list and 'total' count

        Example:
            >>> router = Router("my-router")
            >>> result = router.list_requests(limit=50, status="completed")
            >>> for req in result["requests"]:
            ...     print(f"{req['request_id']}: {req['matched_rule_name']}")
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if matched_rule is not None:
            params["matched_rule"] = matched_rule
        if response_code:
            params["response_code"] = response_code

        response = self.client._make_request(
            "GET",
            f"/workspaces/{self.client._workspace_name}/inference/routers/{self.name}/requests",
            params=params,
        )
        return response.json()

    def get_request(self, request_id: str) -> Dict[str, Any]:
        """Get details of a specific routed request.

        Args:
            request_id: UUID of the request

        Returns:
            Request details including input, routing result, response, etc.

        Example:
            >>> router = Router("my-router")
            >>> req = router.get_request("uuid-123")
            >>> print(req["matched_rule_name"])
            >>> print(req["response_status_code"])
        """
        response = self.client._make_request(
            "GET",
            f"/workspaces/{self.client._workspace_name}/inference/routers/{self.name}/requests/{request_id}",
        )
        return response.json()

    def create_request(
        self,
        input_request: Dict[str, Any],
        status: Optional[str] = None,
        matched_rule_name: Optional[str] = None,
        routing_result: Optional[Dict[str, Any]] = None,
        selected_target: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        response_status_code: Optional[int] = None,
        error_message: Optional[str] = None,
        routing_latency_ms: Optional[float] = None,
        execution_latency_ms: Optional[float] = None,
        total_latency_ms: Optional[float] = None,
        invocation_type: Optional[str] = None,
        invoked_model_run_number: Optional[int] = None,
        invoked_workflow_run_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a router request log entry.

        Used by external systems to log requests processed outside the platform.

        Args:
            input_request: The original request payload
            status: Initial status (pending, routing, executing, completed, failed)
            matched_rule_name: Name of the matched routing rule
            routing_result: Full routing decision result
            selected_target: Selected target endpoint
            response_data: Response from target
            response_status_code: HTTP response status code
            error_message: Error message if failed
            routing_latency_ms: Time spent on routing decision
            execution_latency_ms: Time spent on execution
            total_latency_ms: Total request latency
            invocation_type: Type of downstream invocation (model, workflow, external)
            invoked_model_run_number: Run number of invoked model run
            invoked_workflow_run_number: Run number of invoked workflow run

        Returns:
            Created router request details

        Example:
            >>> router = Router("my-router")
            >>> req = router.create_request(
            ...     input_request={"user": {"tier": "premium"}},
            ...     status="completed",
            ...     matched_rule_name="premium-route",
            ...     response_status_code=200,
            ... )
        """
        payload: Dict[str, Any] = {"input_request": input_request}
        if status:
            payload["status"] = status
        if matched_rule_name:
            payload["matched_rule_name"] = matched_rule_name
        if routing_result:
            payload["routing_result"] = routing_result
        if selected_target:
            payload["selected_target"] = selected_target
        if response_data:
            payload["response_data"] = response_data
        if response_status_code:
            payload["response_status_code"] = response_status_code
        if error_message:
            payload["error_message"] = error_message
        if routing_latency_ms:
            payload["routing_latency_ms"] = routing_latency_ms
        if execution_latency_ms:
            payload["execution_latency_ms"] = execution_latency_ms
        if total_latency_ms:
            payload["total_latency_ms"] = total_latency_ms
        if invocation_type:
            payload["invocation_type"] = invocation_type
        if invoked_model_run_number:
            payload["invoked_model_run_number"] = invoked_model_run_number
        if invoked_workflow_run_number:
            payload["invoked_workflow_run_number"] = invoked_workflow_run_number

        response = self.client._make_request(
            "POST",
            f"/workspaces/{self.client._workspace_name}/inference/routers/{self.name}/requests",
            json=payload,
        )
        return response.json()

    # === Utility ===

    def refresh(self):
        """Re-fetch config and re-create engine.

        Use this after external changes to the router configuration.

        Example:
            >>> router = Router("my-router")
            >>> router.refresh()
            >>> print(router.config)  # Fresh data
        """
        self._config = None
        self._engine = self._create_engine()

    def __repr__(self) -> str:
        """String representation of the Router."""
        return f"Router(name='{self.name}')"

    def __str__(self) -> str:
        """Human-readable string representation."""
        active = self.active_version
        return f"Router: {self.name} (v{active})" if active else f"Router: {self.name}"

    # === Factory Methods ===

    @classmethod
    def get(cls, name: str, client: Optional[MixClient] = None) -> "Router":
        """Get a router by name (primary access method).

        Args:
            name: Router name
            client: Optional MixClient instance

        Returns:
            Router proxy instance

        Example:
            >>> router = Router.get("my-router")
            >>> result = router.route({"user": {"tier": "premium"}})
        """
        return cls(name, client=client)

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        rules: List[Dict[str, Any]],
        settings: Optional[Dict[str, Any]] = None,
        client: Optional[MixClient] = None,
    ) -> "Router":
        """Create a new router.

        Args:
            name: Router name (must be unique in workspace)
            description: Router description
            rules: List of routing rules
            settings: Optional deployment settings (inference_uri, update_uri)
            client: Optional MixClient instance

        Returns:
            Router proxy instance for the created router

        Example:
            >>> router = Router.create(
            ...     name="ab-test-router",
            ...     description="A/B test between models",
            ...     rules=[
            ...         {"name": "premium", "priority": 100, ...},
            ...         {"name": "default", "priority": 1, ...},
            ...     ]
            ... )
        """
        c = client or MixClient()
        payload: Dict[str, Any] = {
            "name": name,
            "description": description,
            "rules": rules,
        }
        if settings:
            payload["settings"] = settings

        c._make_request(
            "POST",
            f"/workspaces/{c._workspace_name}/inference/routers",
            json=payload,
        )
        return cls(name, client=c)

    @classmethod
    def list(
        cls, status: Optional[str] = None, client: Optional[MixClient] = None
    ) -> List["Router"]:
        """List all routers in workspace.

        Args:
            status: Optional filter by status ('active', 'inactive')
            client: Optional MixClient instance

        Returns:
            List of Router proxy instances

        Example:
            >>> for router in Router.list():
            ...     print(f"{router.name}: v{router.active_version}")
        """
        c = client or MixClient()
        params = {"status": status} if status else None
        response = c._make_request(
            "GET",
            f"/workspaces/{c._workspace_name}/inference/routers",
            params=params,
        )
        routers_data = response.json().get("data", [])
        return [cls(r["name"], client=c) for r in routers_data]


# Module-level convenience functions


def get_router(name: str, client: Optional[MixClient] = None) -> Router:
    """Get a router by name.

    This is the primary way to access routers in a workspace.

    Args:
        name: Router name
        client: Optional MixClient instance

    Returns:
        Router proxy instance

    Example:
        >>> from mixtrain import get_router
        >>> router = get_router("my-router")
        >>> result = router.route({"user": {"tier": "premium"}})
    """
    return Router.get(name, client=client)


def list_routers(
    status: Optional[str] = None, client: Optional[MixClient] = None
) -> List[Router]:
    """List all routers in the workspace.

    Args:
        status: Optional filter by status ('active', 'inactive')
        client: Optional MixClient instance

    Returns:
        List of Router instances

    Example:
        >>> from mixtrain import list_routers
        >>> routers = list_routers()
        >>> for router in routers:
        ...     print(router.name)
    """
    return Router.list(status=status, client=client)

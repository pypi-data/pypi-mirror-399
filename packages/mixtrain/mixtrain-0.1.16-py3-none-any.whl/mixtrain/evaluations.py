"""Evaluation reference system for convenient evaluation access.

This module provides an Eval proxy class that makes it easy to reference
and interact with evaluations in a workspace.

Example:
    >>> from mixtrain import get_evaluation
    >>> eval = get_evaluation("my-eval")
    >>> print(eval.config)
    >>> eval.delete()
"""

from typing import Any, Dict, List, Optional

from .client import MixClient
from .helpers import validate_resource_name


class Eval:
    """Proxy class for convenient evaluation access and operations.

    This class wraps MixClient evaluation operations and provides a clean,
    object-oriented interface for working with evaluations.

    Usage:
        # Reference an existing evaluation (lazy, no API call)
        eval = Eval("accuracy-eval")
        print(eval.config)  # API call happens here

        # Create a new evaluation
        eval = Eval.create("new-eval", config={...})

    Args:
        name: Name of the evaluation
        client: Optional MixClient instance (creates new one if not provided)
        _response: Optional cached response from creation

    Attributes:
        name: Evaluation name
        client: MixClient instance for API operations
    """

    def __init__(
        self,
        name: str,
        client: Optional[MixClient] = None,
        _response: Optional[Dict[str, Any]] = None,
    ):
        """Initialize Eval proxy.

        Args:
            name: Name of the evaluation
            client: Optional MixClient instance (creates new one if not provided)
            _response: Optional cached response from creation

        Raises:
            ValueError: If name is invalid (must be lowercase alphanumeric with hyphens/underscores)
        """
        validate_resource_name(name, "evaluation")
        self.name = name
        self.client = client or MixClient()
        self._response = _response
        self._metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def create(
        cls,
        name: str,
        config: Dict[str, Any],
        description: str = "",
        client: Optional[MixClient] = None,
    ) -> "Eval":
        """Create a new evaluation.

        Args:
            name: Name for the evaluation
            config: Evaluation configuration
            description: Optional description
            client: Optional MixClient instance

        Returns:
            Eval proxy for the created evaluation

        Example:
            >>> eval = Eval.create("my-eval", config={"type": "comparison"})
        """
        if client is None:
            client = MixClient()

        payload = {"name": name, "description": description, "config": config}
        response = client._make_request(
            "POST", f"/workspaces/{client._workspace_name}/evaluations/", json=payload
        )
        return cls(name=name, client=client, _response=response.json())

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get evaluation metadata (cached after first access).

        Returns:
            Evaluation details including name, description, config, etc.

        Example:
            >>> eval = Eval("my-eval")
            >>> print(eval.metadata["description"])
        """
        if self._metadata is None:
            if self._response is not None:
                self._metadata = self._response
            else:
                self._metadata = self.client.get_evaluation(self.name)
        return self._metadata

    @property
    def config(self) -> Dict[str, Any]:
        """Get evaluation configuration.

        Returns:
            Evaluation config dictionary
        """
        return self.metadata.get("config", {})

    @property
    def description(self) -> str:
        """Get evaluation description.

        Returns:
            Evaluation description string
        """
        return self.metadata.get("description", "")

    @property
    def status(self) -> str:
        """Get evaluation status.

        Returns:
            Evaluation status string
        """
        return self.metadata.get("status", "")

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update evaluation metadata.

        Args:
            name: Optional new name
            description: Optional new description
            config: Optional new config
            status: Optional new status

        Returns:
            Updated evaluation data

        Example:
            >>> eval = Eval("my-eval")
            >>> eval.update(description="Updated description")
        """
        result = self.client.update_evaluation(
            self.name,
            name=name,
            description=description,
            config=config,
            status=status,
        )
        # Update local name if changed
        if name:
            self.name = name
        # Clear metadata cache
        self._metadata = None
        self._response = None
        return result

    def delete(self) -> Dict[str, Any]:
        """Delete the evaluation.

        Returns:
            Deletion result

        Example:
            >>> eval = Eval("my-eval")
            >>> eval.delete()
        """
        return self.client.delete_evaluation(self.name)

    def refresh(self):
        """Clear cached data and force refresh on next access.

        Example:
            >>> eval = Eval("my-eval")
            >>> eval.refresh()
            >>> print(eval.metadata)  # Will fetch fresh data
        """
        self._metadata = None
        self._response = None

    def __repr__(self) -> str:
        """String representation of the Eval."""
        return f"Eval(name='{self.name}')"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Eval: {self.name}"


def get_eval(name: str, client: Optional[MixClient] = None) -> Eval:
    """Get an evaluation reference by name.

    This is the primary way to access evaluations in a workspace.

    Args:
        name: Evaluation name
        client: Optional MixClient instance

    Returns:
        Eval proxy instance

    Example:
        >>> from mixtrain import get_eval
        >>> eval = get_eval("accuracy-eval")
        >>> print(eval.config)
    """
    return Eval(name, client=client)


def list_evals(client: Optional[MixClient] = None) -> List[Eval]:
    """List all evaluations in the workspace.

    Args:
        client: Optional MixClient instance

    Returns:
        List of Eval instances

    Example:
        >>> from mixtrain import list_evals
        >>> evals = list_evals()
        >>> for e in evals:
        ...     print(e.name)
    """
    if client is None:
        client = MixClient()

    response = client.list_evaluations()
    evals_data = response.get("evaluations", [])

    return [Eval(e["name"], client=client) for e in evals_data]

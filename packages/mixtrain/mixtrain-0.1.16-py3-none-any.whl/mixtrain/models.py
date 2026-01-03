"""Model reference system for convenient model access.

This module provides a Model proxy class that makes it easy to reference
and interact with models in a workspace.

Example:
    >>> from mixtrain import get_model
    >>> model = get_model("my-model")
    >>> result = model.run({"text": "Hello world"})
    >>> print(result)
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional

from .client import MixClient
from .helpers import validate_resource_name

logger = logging.getLogger(__name__)


class Model:
    """Proxy class for convenient model access and operations.

    This class wraps MixClient model operations and provides a clean,
    object-oriented interface for working with models.

    Args:
        name: Name of the model
        client: Optional MixClient instance (creates new one if not provided)

    Attributes:
        name: Model name
        client: MixClient instance for API operations

    Example:
        >>> model = Model("sentiment-analyzer")
        >>> result = model.run({"text": "Great product!"})
        >>> print(model.metadata)
        >>> print(model.runs)
    """

    def __init__(self, name: str, client: Optional[MixClient] = None):
        """Initialize Model proxy.

        Args:
            name: Name of the model
            client: Optional MixClient instance (creates new one if not provided)

        Raises:
            ValueError: If name is invalid (must be lowercase alphanumeric with hyphens/underscores)
        """
        validate_resource_name(name, "model")
        self.name = name
        self.client = client or MixClient()
        self._metadata: Optional[Dict[str, Any]] = None
        self._runs_cache: Optional[List[Dict[str, Any]]] = None

    def submit(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Submit model inference asynchronously. Returns run info immediately.

        This starts a model run and returns immediately without waiting for completion.
        Use this when you want to manage the run lifecycle yourself or run multiple
        models in parallel.

        Args:
            inputs: Input data for the model
            config: Optional configuration overrides

        Returns:
            Run info including run_number and status

        Example:
            >>> model = Model("sentiment-analyzer")
            >>> run_info = model.submit({"text": "Great product!"})
            >>> print(f"Started run #{run_info['run_number']}")
            >>> # Later, check status:
            >>> run = model.get_run(run_info['run_number'])
        """
        return self.client.run_model(self.name, inputs=inputs, config=config)

    def run(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """Run model inference synchronously. Blocks until completion.

        This submits a model run and polls until it completes. Use this when you
        want a simple blocking call that returns the outputs directly.

        For long-running models, uses polling with exponential backoff to avoid
        HTTP connection timeout issues.

        Args:
            inputs: Input data for the model
            config: Optional configuration overrides
            timeout: Maximum seconds to wait for completion (default: 300)

        Returns:
            Run result including status and outputs

        Raises:
            TimeoutError: If model doesn't complete within timeout
            ValueError: If run submission fails

        Example:
            >>> model = Model("sentiment-analyzer")
            >>> result = model.run({"text": "Great product!"})
            >>> print(result["outputs"])
        """
        import time

        # Submit the run
        run_info = self.submit(inputs=inputs, config=config)
        run_number = run_info.get("run_number")
        if not run_number:
            raise ValueError(f"Failed to start model run: {run_info}")

        # Poll for completion with error handling
        start_time = time.time()
        poll_interval = 0.5
        consecutive_errors = 0
        max_consecutive_errors = 5
        last_known_run: Optional[Dict[str, Any]] = None

        while time.time() - start_time < timeout:
            try:
                run = self.get_run(run_number)
                last_known_run = run
                consecutive_errors = 0  # Reset on success

                if run["status"] in ["completed", "failed", "cancelled"]:
                    return run
            except Exception as e:
                consecutive_errors += 1
                logger.warning(
                    f"Failed to fetch run status (attempt {consecutive_errors}): {e}"
                )
                if consecutive_errors >= max_consecutive_errors:
                    # Return last known state or raise with context
                    if last_known_run:
                        logger.error(
                            f"Too many errors, returning last known state for run {run_number}"
                        )
                        last_known_run["_polling_error"] = str(e)
                        return last_known_run
                    raise RuntimeError(
                        f"Failed to poll model run {run_number} after {max_consecutive_errors} attempts: {e}"
                    ) from e

            time.sleep(poll_interval)
            # Exponential backoff up to 5s
            poll_interval = min(poll_interval * 1.5, 5)

        raise TimeoutError(f"Model run {run_number} did not complete within {timeout}s")

    def run_batch(
        self,
        inputs_list: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None,
        max_workers: int = 10,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Dict[str, Any]]:
        """Run model inference on multiple inputs in parallel.

        Args:
            inputs_list: List of input dictionaries
            config: Optional configuration overrides applied to all runs
            max_workers: Maximum number of parallel workers (default: 10)
            progress_callback: Optional callback(completed, total) for progress updates

        Returns:
            List of run results (in same order as inputs)

        Example:
            >>> model = Model("sentiment-analyzer")
            >>> results = model.run_batch([
            ...     {"text": "Great!"},
            ...     {"text": "Terrible!"}
            ... ])
            >>> # With progress callback
            >>> results = model.run_batch(
            ...     inputs_list,
            ...     progress_callback=lambda done, total: print(f"{done}/{total}")
            ... )
        """
        if not inputs_list:
            return []

        results: List[Optional[Dict[str, Any]]] = [None] * len(inputs_list)
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(self.run, inputs, config): idx
                for idx, inputs in enumerate(inputs_list)
            }
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                results[idx] = future.result()
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(inputs_list))

        return results  # type: ignore

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get model metadata (cached after first access).

        Returns:
            Model details including name, source, description, etc.

        Example:
            >>> model = Model("my-model")
            >>> print(model.metadata["source"])
            >>> print(model.metadata["description"])
        """
        if self._metadata is None:
            self._metadata = self.client.get_model(self.name)
        return self._metadata

    @property
    def spec(self) -> Optional[Dict[str, Any]]:
        """Get model specification.

        Returns:
            Model spec dictionary or None
        """
        return self.metadata.get("spec")

    @property
    def source(self) -> str:
        """Get model source (native, fal, modal, openai, anthropic, etc.).

        Returns:
            Model source string
        """
        return self.metadata.get("source", "")

    @property
    def description(self) -> str:
        """Get model description.

        Returns:
            Model description string
        """
        return self.metadata.get("description", "")

    @property
    def runs(self) -> List[Dict[str, Any]]:
        """Get recent model runs (cached).

        Returns:
            List of model runs

        Example:
            >>> model = Model("my-model")
            >>> for run in model.runs:
            ...     print(f"Run #{run['run_number']}: {run['status']}")
        """
        if self._runs_cache is None:
            response = self.client.list_model_runs(self.name)
            self._runs_cache = response.get("runs", [])
        return self._runs_cache

    def get_runs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get model runs with optional limit.

        Args:
            limit: Maximum number of runs to return

        Returns:
            List of model runs

        Example:
            >>> model = Model("my-model")
            >>> recent_runs = model.get_runs(limit=5)
        """
        response = self.client.list_model_runs(self.name)
        runs = response.get("runs", [])
        if limit:
            runs = runs[:limit]
        return runs

    def get_run(self, run_number: int) -> Dict[str, Any]:
        """Get details of a specific model run.

        Args:
            run_number: Run number

        Returns:
            Run details

        Example:
            >>> model = Model("my-model")
            >>> run = model.get_run(5)
            >>> print(run["status"])
        """
        return self.client.get_model_run(self.name, run_number)

    def update_run(
        self,
        run_number: int,
        status: Optional[str] = None,
        outputs: Optional[Any] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a model run's status and outputs.

        Args:
            run_number: Run number to update
            status: New status (e.g., "running", "completed", "failed")
            outputs: Output data from the model run
            error: Error message if run failed

        Returns:
            Updated run details

        Example:
            >>> model = Model("my-model")
            >>> model.update_run(5, status="completed", outputs={"result": "success"})
        """
        return self.client.update_model_run_status(
            self.name, run_number, status=status, outputs=outputs, error=error
        )

    def get_logs(self, run_number: Optional[int] = None) -> str:
        """Get logs for a model run.

        Args:
            run_number: Optional run number (defaults to latest run)

        Returns:
            Log content as string

        Example:
            >>> model = Model("my-model")
            >>> logs = model.get_logs()  # Latest run
            >>> print(logs)
        """
        logs_data = self.client.get_model_run_logs(self.name, run_number)
        return logs_data.get("logs", "")

    def get_code(self) -> str:
        """Get model source code (for native models).

        Returns:
            Model code as string

        Example:
            >>> model = Model("my-model")
            >>> code = model.get_code()
            >>> print(code)
        """
        code_data = self.client.get_model_code(self.name)
        return code_data.get("code", "")

    def update_code(self, code: str) -> Dict[str, Any]:
        """Update model source code (for native models).

        Args:
            code: New code content

        Returns:
            Update result

        Example:
            >>> model = Model("my-model")
            >>> model.update_code("def run():\\n    return {'result': 'success'}")
        """
        return self.client.update_model_code(self.name, code)

    def list_files(self) -> List[Dict[str, Any]]:
        """List files in the model.

        Returns:
            List of files

        Example:
            >>> model = Model("my-model")
            >>> files = model.list_files()
            >>> for file in files:
            ...     print(file["path"])
        """
        response = self.client.list_model_files(self.name)
        return response.get("files", [])

    def get_file(self, file_path: str) -> str:
        """Get content of a specific model file.

        Args:
            file_path: Path to file within model

        Returns:
            File content as string

        Example:
            >>> model = Model("my-model")
            >>> content = model.get_file("requirements.txt")
        """
        response = self.client.get_model_file(self.name, file_path)
        return response.get("content", "")

    def update(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update model metadata.

        Args:
            name: Optional new name
            description: Optional new description

        Returns:
            Updated model data

        Example:
            >>> model = Model("my-model")
            >>> model.update(description="Updated description")
        """
        result = self.client.update_model(self.name, name=name, description=description)
        # Update local name if changed
        if name:
            self.name = name
        # Clear metadata cache
        self._metadata = None
        return result

    def delete(self) -> Dict[str, Any]:
        """Delete the model.

        Returns:
            Deletion result

        Example:
            >>> model = Model("my-model")
            >>> model.delete()
        """
        return self.client.delete_model(self.name)

    def refresh(self):
        """Clear cached data and force refresh on next access.

        Example:
            >>> model = Model("my-model")
            >>> model.refresh()
            >>> print(model.metadata)  # Will fetch fresh data
        """
        self._metadata = None
        self._runs_cache = None

    def __repr__(self) -> str:
        """String representation of the Model."""
        return f"Model(name='{self.name}', source='{self.source}')"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Model: {self.name} ({self.source})"

    @staticmethod
    def compare(
        models: List[str],
        inputs_list: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None,
        client: Optional[MixClient] = None,
        max_workers: int = 10,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Run same inputs across multiple models in parallel.

        This is useful for comparing model outputs side-by-side.

        Args:
            models: List of model names to compare
            inputs_list: List of input dictionaries (same for all models)
            config: Optional configuration overrides applied to all runs
            client: Optional MixClient instance
            max_workers: Maximum number of parallel workers (default: 10)
            progress_callback: Optional callback(completed, total) for progress updates

        Returns:
            Dict mapping model_name to list of results

        Example:
            >>> results = Model.compare(
            ...     ["fal-ai/flux", "fal-ai/stable-diffusion"],
            ...     [{"prompt": "a cat"}, {"prompt": "a dog"}]
            ... )
            >>> for model, outputs in results.items():
            ...     print(f"{model}: {len(outputs)} results")
        """
        if client is None:
            client = MixClient()

        # Total tasks = models * inputs
        total_tasks = len(models) * len(inputs_list)
        results: Dict[str, List[Optional[Dict[str, Any]]]] = {
            model: [None] * len(inputs_list) for model in models
        }
        completed = 0

        def run_single(model_name: str, idx: int, inputs: Dict[str, Any]) -> tuple:
            """Run a single model and return result or error dict."""
            try:
                model = Model(model_name, client=client)
                result = model.run(inputs=inputs, config=config)
                return (model_name, idx, result)
            except Exception as e:
                logger.warning(f"Model {model_name} failed for input {idx}: {e}")
                return (model_name, idx, {"error": str(e), "status": "failed"})

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for model_name in models:
                for idx, inputs in enumerate(inputs_list):
                    future = executor.submit(run_single, model_name, idx, inputs)
                    futures.append(future)

            for future in as_completed(futures):
                # run_single catches exceptions internally, so result() won't raise
                model_name, idx, result = future.result()
                results[model_name][idx] = result
                completed += 1
                if progress_callback:
                    progress_callback(completed, total_tasks)

        return results  # type: ignore


def get_model(name: str, client: Optional[MixClient] = None) -> Model:
    """Get a model reference by name.

    This is the primary way to access models in a workspace.

    Args:
        name: Model name
        client: Optional MixClient instance

    Returns:
        Model proxy instance

    Example:
        >>> from mixtrain import get_model
        >>> model = get_model("sentiment-analyzer")
        >>> result = model.run({"text": "Great!"})
    """
    return Model(name, client=client)


def list_models(
    provider: Optional[str] = None, client: Optional[MixClient] = None
) -> List[Model]:
    """List all models in the workspace.

    Args:
        provider: Optional filter by provider type
        client: Optional MixClient instance

    Returns:
        List of Model instances

    Example:
        >>> from mixtrain import list_models
        >>> models = list_models()
        >>> for model in models:
        ...     print(model.name)
    """
    if client is None:
        client = MixClient()

    response = client.list_models(provider=provider)
    models_data = response.get("models", [])

    return [Model(m["name"], client=client) for m in models_data]

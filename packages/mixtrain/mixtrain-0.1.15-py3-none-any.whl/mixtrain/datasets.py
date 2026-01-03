"""Dataset reference system for convenient dataset access.

This module provides a Dataset proxy class that makes it easy to reference
and interact with datasets in a workspace.

Example:
    >>> from mixtrain import get_dataset
    >>> dataset = get_dataset("my-dataset")
    >>> print(dataset.metadata)
    >>> df = dataset.to_pandas()
"""

from typing import Any, Dict, List, Optional

from .client import MixClient
from .helpers import validate_resource_name


class Dataset:
    """Proxy class for convenient dataset access and operations.

    This class wraps MixClient dataset operations and provides a clean,
    object-oriented interface for working with datasets.

    Usage:
        # Reference an existing dataset (lazy, no API call)
        dataset = Dataset("training-data")
        df = dataset.to_pandas()  # API call happens here

        # Create a new dataset from file
        dataset = Dataset.create_from_file("new-data", "data.csv")

    Args:
        name: Name of the dataset
        client: Optional MixClient instance (creates new one if not provided)
        _response: Optional cached response from creation

    Attributes:
        name: Dataset name
        client: MixClient instance for API operations
    """

    def __init__(
        self,
        name: str,
        client: Optional[MixClient] = None,
        _response: Optional[Dict[str, Any]] = None,
    ):
        """Initialize Dataset proxy.

        Args:
            name: Name of the dataset
            client: Optional MixClient instance (creates new one if not provided)
            _response: Optional cached response from creation

        Raises:
            ValueError: If name is invalid (must be lowercase alphanumeric with hyphens/underscores)
        """
        validate_resource_name(name, "dataset")
        self.name = name
        self.client = client or MixClient()
        self._response = _response
        self._metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def create_from_file(
        cls,
        name: str,
        file_path: str,
        description: Optional[str] = None,
        provider_type: Optional[str] = None,
        client: Optional[MixClient] = None,
    ) -> "Dataset":
        """Create a new dataset from a file.

        Args:
            name: Name for the dataset
            file_path: Path to the file to upload
            description: Optional description
            provider_type: Optional provider type (defaults to apache_iceberg)
            client: Optional MixClient instance

        Returns:
            Dataset proxy for the created dataset

        Example:
            >>> dataset = Dataset.create_from_file("my-data", "data.csv")
        """
        if client is None:
            client = MixClient()

        headers = {}
        if description:
            headers["X-Description"] = description

        if not provider_type:
            provider_type = "apache_iceberg"

        with open(file_path, "rb") as f:
            files = {"file": (file_path.split("/")[-1], f, "application/octet-stream")}
            response = client._make_request(
                "POST",
                f"/lakehouse/workspaces/{client._workspace_name}/tables/{name}?provider_type={provider_type}",
                files=files,
                headers=headers,
            )
        return cls(name=name, client=client, _response=response.json())

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get dataset metadata (cached after first access).

        Returns:
            Dataset metadata including name, description, row count, etc.

        Example:
            >>> dataset = Dataset("my-dataset")
            >>> print(dataset.metadata["row_count"])
        """
        if self._metadata is None:
            if self._response is not None:
                self._metadata = self._response
            else:
                self._metadata = self.client.get_dataset_metadata(self.name)
        return self._metadata

    @property
    def description(self) -> str:
        """Get dataset description.

        Returns:
            Dataset description string
        """
        return self.metadata.get("description", "")

    @property
    def row_count(self) -> Optional[int]:
        """Get dataset row count.

        Returns:
            Number of rows in the dataset, or None if unknown
        """
        return self.metadata.get("row_count")

    def to_table(self):
        """Get dataset as a PyArrow Table.

        Returns:
            PyArrow Table containing the dataset data

        Example:
            >>> dataset = Dataset("my-dataset")
            >>> table = dataset.to_table()
        """
        return self.client.get_dataset(self.name)

    def to_pandas(self):
        """Get dataset as a Pandas DataFrame.

        Returns:
            Pandas DataFrame containing the dataset data

        Example:
            >>> dataset = Dataset("my-dataset")
            >>> df = dataset.to_pandas()
        """
        table = self.to_table()
        return table.to_pandas()

    def delete(self) -> Dict[str, Any]:
        """Delete the dataset.

        Returns:
            Deletion result

        Example:
            >>> dataset = Dataset("my-dataset")
            >>> dataset.delete()
        """
        response = self.client.delete_dataset(self.name)
        return {"status": "deleted"}

    def refresh(self):
        """Clear cached data and force refresh on next access.

        Example:
            >>> dataset = Dataset("my-dataset")
            >>> dataset.refresh()
            >>> print(dataset.metadata)  # Will fetch fresh data
        """
        self._metadata = None
        self._response = None

    def __repr__(self) -> str:
        """String representation of the Dataset."""
        return f"Dataset(name='{self.name}')"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Dataset: {self.name}"


def get_dataset(name: str, client: Optional[MixClient] = None) -> Dataset:
    """Get a dataset reference by name.

    This is the primary way to access datasets in a workspace.

    Args:
        name: Dataset name
        client: Optional MixClient instance

    Returns:
        Dataset proxy instance

    Example:
        >>> from mixtrain import get_dataset
        >>> dataset = get_dataset("training-data")
        >>> df = dataset.to_pandas()
    """
    return Dataset(name, client=client)


def list_datasets(client: Optional[MixClient] = None) -> List[Dataset]:
    """List all datasets in the workspace.

    Args:
        client: Optional MixClient instance

    Returns:
        List of Dataset instances

    Example:
        >>> from mixtrain import list_datasets
        >>> datasets = list_datasets()
        >>> for ds in datasets:
        ...     print(ds.name)
    """
    if client is None:
        client = MixClient()

    response = client.list_datasets()
    datasets_data = response.get("datasets", [])

    return [Dataset(d["name"], client=client) for d in datasets_data]

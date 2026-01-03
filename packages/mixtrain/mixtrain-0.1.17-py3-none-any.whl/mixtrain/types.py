"""MixType - Typed values for workflow and model inputs/outputs.

This module provides type classes that enable rich rendering in the UI.
When workflows or models return typed values, the frontend can render
them appropriately (images, videos, links to resources, etc.).
"""

from dataclasses import dataclass, field
from typing import Any, get_type_hints, get_origin, get_args, Union


@dataclass
class MixType:
    """Base class for typed values. Used for both inputs and outputs.

    Subclasses define specific types with their own `_type` identifier
    that tells the frontend how to render the value.
    """

    _type: str = field(default="", init=False)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {}
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                result[k] = v
            else:
                result[k] = v
        return result


# =============================================================================
# Media Types - Render content inline
# =============================================================================


@dataclass
class Image(MixType):
    """An image to render inline.

    Args:
        url: URL to the image
        width: Optional width in pixels
        height: Optional height in pixels
        format: Optional format (png, jpg, webp)

    Example:
        >>> return {"image": Image(url="https://...", width=1024, height=1024)}
    """

    url: str
    width: int | None = None
    height: int | None = None
    format: str | None = None
    _type: str = field(default="link-image", init=False)


@dataclass
class Video(MixType):
    """A video to render with a player.

    Args:
        url: URL to the video
        duration_seconds: Optional duration in seconds
        width: Optional width in pixels
        height: Optional height in pixels
        format: Optional format (mp4, webm)

    Example:
        >>> return {"video": Video(url="https://...", duration_seconds=5.0)}
    """

    url: str
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    format: str | None = None
    _type: str = field(default="link-video", init=False)


@dataclass
class Audio(MixType):
    """An audio file to render with a player.

    Args:
        url: URL to the audio file
        duration_seconds: Optional duration in seconds
        format: Optional format (mp3, wav)

    Example:
        >>> return {"audio": Audio(url="https://...", duration_seconds=30.0)}
    """

    url: str
    duration_seconds: float | None = None
    format: str | None = None
    _type: str = field(default="link-audio", init=False)


@dataclass
class Model3D(MixType):
    """A 3D model to render with a viewer.

    Args:
        url: URL to the 3D model file
        format: Optional format (glb, gltf, obj)

    Example:
        >>> return {"model": Model3D(url="https://...", format="glb")}
    """

    url: str
    format: str | None = None
    _type: str = field(default="3d", init=False)


# =============================================================================
# Text Types
# =============================================================================


@dataclass
class Text(MixType):
    """Plain text content.

    Args:
        content: The text content

    Example:
        >>> return {"message": Text(content="Processing complete!")}
    """

    content: str
    _type: str = field(default="text", init=False)


@dataclass
class Markdown(MixType):
    """Markdown content - renders with formatting.

    Args:
        content: The markdown content

    Example:
        >>> return {"report": Markdown(content="# Results\\n- Item 1\\n- Item 2")}
    """

    content: str
    _type: str = field(default="markdown", init=False)


@dataclass
class JSON(MixType):
    """JSON data - renders with syntax highlighting.

    Args:
        data: The JSON-serializable data (dict or list)

    Example:
        >>> return {"config": JSON(data={"key": "value", "items": [1, 2, 3]})}
    """

    data: dict | list
    _type: str = field(default="json", init=False)


# =============================================================================
# Serialization Functions
# =============================================================================


def _is_proxy_class(value: Any) -> tuple[bool, str | None, dict | None]:
    """Check if value is a proxy class instance and return type info.

    Returns:
        Tuple of (is_proxy, type_name, serialized_dict)
    """
    # Lazy imports to avoid circular dependencies
    from .models import Model as ModelProxy
    from .evaluations import Eval
    from .datasets import Dataset as DatasetProxy
    from .workflows import Workflow as WorkflowProxy

    if isinstance(value, ModelProxy):
        return (True, "model", {"_type": "model", "name": value.name})
    if isinstance(value, Eval):
        return (True, "evaluation", {"_type": "evaluation", "name": value.name})
    if isinstance(value, DatasetProxy):
        return (True, "dataset", {"_type": "dataset", "name": value.name})
    if isinstance(value, WorkflowProxy):
        result = {"_type": "workflow", "name": value.name}
        if value.run_number is not None:
            result["run_number"] = value.run_number
        return (True, "workflow", result)
    return (False, None, None)


def serialize_output(value: Any) -> dict | list | Any:
    """Serialize an output value with type information (recursive).

    Converts MixType instances, proxy classes, and nested structures into
    JSON-serializable dictionaries with `_type` fields for frontend rendering.

    Supports both explicit MixType wrappers (Image, Video, etc.) and proxy
    classes (Model, Eval, Dataset, Workflow) returned directly from SDK calls.

    Args:
        value: The value to serialize (MixType, proxy class, dict, list, or primitive)

    Returns:
        Serialized value with type information

    Example:
        >>> serialize_output(Image(url="https://..."))
        {'_type': 'link-image', 'url': 'https://...'}

        >>> serialize_output([Image(url="a"), Image(url="b")])
        {'_type': 'list', 'data': [{'_type': 'link-image', 'url': 'a'}, ...]}

        >>> from mixtrain import Eval
        >>> serialize_output(Eval("my-eval"))
        {'_type': 'evaluation', 'name': 'my-eval'}
    """
    # Check for proxy classes first
    is_proxy, _, serialized = _is_proxy_class(value)
    if is_proxy:
        return serialized

    if isinstance(value, MixType):
        # Serialize MixType instance
        result = {"_type": value._type}
        for k, v in value.__dict__.items():
            if not k.startswith("_") and v is not None:
                result[k] = serialize_output(v)
        return result
    elif isinstance(value, dict):
        # Check if any values are MixType instances or proxy classes
        has_typed_values = any(
            isinstance(v, MixType) or _is_proxy_class(v)[0] for v in value.values()
        )
        if has_typed_values:
            return {
                "_type": "dict",
                "data": {k: serialize_output(v) for k, v in value.items()},
            }
        else:
            # Plain dict - serialize recursively but don't wrap
            return {k: serialize_output(v) for k, v in value.items()}
    elif isinstance(value, list):
        # Check if any items are MixType instances or proxy classes
        has_typed_items = any(
            isinstance(v, MixType) or _is_proxy_class(v)[0] for v in value
        )
        if has_typed_items:
            return {"_type": "list", "data": [serialize_output(v) for v in value]}
        else:
            # Plain list - serialize recursively but don't wrap
            return [serialize_output(v) for v in value]
    else:
        # Primitive value - return as-is
        return value


def deserialize_output(data: Any) -> Any:
    """Deserialize typed output back to proxy classes or MixType objects (recursive).

    Args:
        data: Serialized data with _type fields

    Returns:
        Deserialized value (proxy class, MixType instance, dict, list, or primitive)
    """
    if not isinstance(data, dict):
        if isinstance(data, list):
            return [deserialize_output(v) for v in data]
        return data

    _type = data.get("_type")
    if _type is None:
        # Plain dict without type info
        return {k: deserialize_output(v) for k, v in data.items()}

    # Handle dict and list containers
    if _type == "dict":
        return {k: deserialize_output(v) for k, v in data.get("data", {}).items()}
    elif _type == "list":
        return [deserialize_output(v) for v in data.get("data", [])]

    # Handle resource types - return proxy classes
    if _type == "model":
        from .models import Model as ModelProxy

        return ModelProxy(data["name"])
    elif _type == "evaluation":
        from .evaluations import Eval

        return Eval(data["name"])
    elif _type == "dataset":
        from .datasets import Dataset as DatasetProxy

        return DatasetProxy(data["name"])
    elif _type == "workflow":
        from .workflows import Workflow as WorkflowProxy

        return WorkflowProxy(data["name"], run_number=data.get("run_number"))

    # Map type strings to MixType classes
    type_map = {
        "link-image": Image,
        "link-video": Video,
        "link-audio": Audio,
        "3d": Model3D,
        "text": Text,
        "markdown": Markdown,
        "json": JSON,
    }

    if _type in type_map:
        cls = type_map[_type]
        # Extract constructor args (exclude _type)
        kwargs = {k: deserialize_output(v) for k, v in data.items() if k != "_type"}
        return cls(**kwargs)
    else:
        # Unknown type - return as dict
        return data


# =============================================================================
# Schema Extraction
# =============================================================================


def extract_output_schema(cls: type) -> dict | None:
    """Extract output schema from a class's run() method return type annotation.

    Args:
        cls: The MixFlow or MixModel class

    Returns:
        Schema dict or None if no return type annotation

    Example:
        >>> class MyModel(MixModel):
        ...     def run(self, inputs) -> dict[str, Image]:
        ...         ...
        >>> extract_output_schema(MyModel)
        {'type': 'dict', 'valueSchema': {'type': 'link-image'}}
    """
    # Check for explicit output_schema attribute first
    if hasattr(cls, "output_schema") and cls.output_schema is not None:
        return cls.output_schema

    # Try to extract from type hints
    if not hasattr(cls, "run"):
        return None

    try:
        hints = get_type_hints(cls.run)
        return_type = hints.get("return")
        if return_type is None:
            return None
        return _type_to_schema(return_type)
    except Exception:
        # Type hint extraction can fail for various reasons
        return None


def _type_to_schema(t: type) -> dict:
    """Convert a Python type annotation to a JSON schema dict (recursive).

    Args:
        t: A Python type (e.g., Image, list[Video], dict[str, Audio])

    Returns:
        Schema dict describing the type
    """
    # Handle None/NoneType
    if t is type(None):
        return {"type": "null"}

    # Handle Union types (e.g., Optional, Union[A, B])
    origin = get_origin(t)

    if origin is Union:
        args = get_args(t)
        # Filter out NoneType for Optional handling
        non_none_args = [a for a in args if a is not type(None)]
        if len(non_none_args) == 1:
            # Optional[X] -> just return schema for X
            return _type_to_schema(non_none_args[0])
        else:
            # Union of multiple types
            return {
                "type": "union",
                "schemas": [_type_to_schema(a) for a in non_none_args],
            }

    if origin is dict:
        args = get_args(t)
        if len(args) >= 2:
            return {"type": "dict", "valueSchema": _type_to_schema(args[1])}
        return {"type": "dict"}

    if origin is list:
        args = get_args(t)
        if args:
            return {"type": "list", "itemSchema": _type_to_schema(args[0])}
        return {"type": "list"}

    # Handle MixType subclasses (media and text types)
    type_map = {
        Image: "link-image",
        Video: "link-video",
        Audio: "link-audio",
        Model3D: "3d",
        Text: "text",
        Markdown: "markdown",
        JSON: "json",
    }

    if t in type_map:
        return {"type": type_map[t]}

    # Handle proxy classes (lazy import to avoid circular deps)
    from .models import Model as ModelProxy
    from .evaluations import Eval
    from .datasets import Dataset as DatasetProxy
    from .workflows import Workflow as WorkflowProxy

    proxy_type_map = {
        ModelProxy: "model",
        Eval: "evaluation",
        DatasetProxy: "dataset",
        WorkflowProxy: "workflow",
    }

    if t in proxy_type_map:
        return {"type": proxy_type_map[t]}

    # Handle primitive types
    if t is str:
        return {"type": "string"}
    if t is int:
        return {"type": "integer"}
    if t is float:
        return {"type": "number"}
    if t is bool:
        return {"type": "boolean"}

    # Default for unknown types
    return {"type": "any"}


# =============================================================================
# Type aliases for convenience
# =============================================================================

# All MixType classes (media and text types only - resource types use proxy classes)
ALL_MIX_TYPES = (Image, Video, Audio, Model3D, Text, Markdown, JSON)

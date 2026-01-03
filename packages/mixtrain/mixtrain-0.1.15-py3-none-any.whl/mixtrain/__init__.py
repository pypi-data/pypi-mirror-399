"""MixTrain SDK - ML Platform Client and Workflow Framework."""

from .client import MixClient, MixFlow, MixModel, mixparam, mixflow_param

# Proxy classes for resources (lazy API access)
from .models import Model, get_model, list_models
from .evaluations import Eval, get_eval, list_evals
from .datasets import Dataset, get_dataset, list_datasets
from .workflows import Workflow, get_workflow, list_workflows

# Media and text types (explicit wrappers for outputs)
from .types import (
    MixType,
    Image,
    Video,
    Audio,
    Model3D,
    Text,
    Markdown,
    JSON,
    serialize_output,
    deserialize_output,
    extract_output_schema,
)

# Utilities for workflows
from .helpers import sanitize_model_name, generate_name, install_packages, validate_resource_name

__all__ = [
    # Client and workflow
    "MixClient",
    "MixFlow",
    "MixModel",
    "mixparam",
    "mixflow_param",
    # Proxy classes (for accessing and creating resources)
    "Model",
    "get_model",
    "list_models",
    "Eval",
    "get_eval",
    "list_evals",
    "Dataset",
    "get_dataset",
    "list_datasets",
    "Workflow",
    "get_workflow",
    "list_workflows",
    # Media and text types (explicit wrappers)
    "MixType",
    "Image",
    "Video",
    "Audio",
    "Model3D",
    "Text",
    "Markdown",
    "JSON",
    # Serialization
    "serialize_output",
    "deserialize_output",
    "extract_output_schema",
    # Utilities
    "sanitize_model_name",
    "generate_name",
    "install_packages",
    "validate_resource_name",
]

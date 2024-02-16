"""Project pipelines."""
from __future__ import annotations

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline
from .pipeline import (
    create_pipeline,
    create_extract_databases_to_parquet_pipeline,
)  # or wherever your create_pipeline function is defined


def register_pipelines() -> dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    # pipelines = find_pipelines()
    # pipelines["__default__"] = sum(pipelines.values())
    pipelines = {
        "__default__": create_pipeline(),
        "extract_data_to_parquet": create_extract_databases_to_parquet_pipeline(),
        # other pipelines...
    }
    return pipelines

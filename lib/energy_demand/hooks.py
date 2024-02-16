from typing import Any, Dict

from kedro.framework.hooks import hook_impl
from kedro.io import DataCatalog

from .schemas import schemas_context


class DataValidationHooks:
    @hook_impl
    def before_node_run(
        self, catalog: DataCatalog, inputs: Dict[str, Any], session_id: str
    ) -> None:
        """Validate inputs data to a node based on using great expectation
        if an expectation suite is defined in ``DATASET_EXPECTATION_MAPPING``.
        """
        self._run_validation(catalog, inputs, session_id)

    @hook_impl
    def after_node_run(
        self, catalog: DataCatalog, outputs: Dict[str, Any], session_id: str
    ) -> None:
        """Validate outputs data from a node based on using great expectation
        if an expectation suite is defined in ``DATASET_EXPECTATION_MAPPING``.
        """
        self._run_validation(catalog, outputs, session_id)

    def _run_validation(
        self, catalog: DataCatalog, data: Dict[str, Any], session_id: str
    ):
        for dataset_name, dataset_value in data.items():
            if dataset_name not in schemas_context.keys():
                continue
            print(f"Checking {dataset_name} validity")
            validation_schema = schemas_context[dataset_name]
            validation_schema.validate(dataset_value)

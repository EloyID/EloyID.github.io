import numpy as np
import pandas as pd
from kedro.pipeline import node

from energy_demand.nodes.model_pca_energy_as_target.utils import (
    reconstruct_data_from_pcas,
)


def test_xgboost_batched_energy_pca_as_target(
    trained_xgboost_batched_energy_pca_as_target,
    X_test_batched_energy_pca_as_target_dataset_preprocessed,
    fitted_fpca,
    X_test_batched_energy_pca_as_target_dataset,
    test_dataset,
):
    y_test_batched_energy_pca_as_target_dataset_predicted = (
        trained_xgboost_batched_energy_pca_as_target.predict(
            X_test_batched_energy_pca_as_target_dataset_preprocessed
        )
    )

    y_test_batched_energy_pca_as_target_dataset_predicted_reconstructed = (
        reconstruct_data_from_pcas(
            fitted_fpca,
            X_test_batched_energy_pca_as_target_dataset,
            y_test_batched_energy_pca_as_target_dataset_predicted,
            test_dataset,
        )
    )

    return (
        y_test_batched_energy_pca_as_target_dataset_predicted,
        y_test_batched_energy_pca_as_target_dataset_predicted_reconstructed,
    )


test_xgboost_batched_energy_pca_as_target_node = node(
    test_xgboost_batched_energy_pca_as_target,
    inputs=[
        "trained_xgboost_batched_energy_pca_as_target",
        "X_test_batched_energy_pca_as_target_dataset_preprocessed",
        "fitted_fpca",
        "X_test_batched_energy_pca_as_target_dataset",
        "X_test_dataset",
    ],
    outputs=[
        "y_test_batched_energy_pca_as_target_dataset_predicted",
        "y_test_batched_energy_pca_as_target_dataset_predicted_reconstructed",
    ],
    name="test_xgboost_batched_energy_pca_as_target",
)

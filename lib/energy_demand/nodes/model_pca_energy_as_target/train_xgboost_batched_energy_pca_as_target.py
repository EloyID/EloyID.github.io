from operator import index

import numpy as np
import pandas as pd
from kedro.pipeline import node
from xgboost import XGBRegressor

from energy_demand.nodes.model_pca_energy_as_target.utils import (
    reconstruct_data_from_pcas,
)


def train_xgboost_batched_energy_pca_as_target(
    X_train_dataset_preprocessed,
    y_train_dataset,
    fitted_fpca,
    X_train_batched_energy_pca_as_target_dataset,
    train_dataset,
):
    xgbm = XGBRegressor(
        objective="reg:squarederror",
        seed=2022,
    )
    xgbm.fit(X_train_dataset_preprocessed, y_train_dataset)
    y_train_batched_energy_pca_as_target_dataset_predicted = xgbm.predict(
        X_train_dataset_preprocessed
    )

    y_train_batched_energy_pca_as_target_dataset_predicted_reconstructed = (
        reconstruct_data_from_pcas(
            fitted_fpca,
            X_train_batched_energy_pca_as_target_dataset,
            y_train_batched_energy_pca_as_target_dataset_predicted,
            train_dataset,
        )
    )

    return (
        xgbm,
        y_train_batched_energy_pca_as_target_dataset_predicted,
        y_train_batched_energy_pca_as_target_dataset_predicted_reconstructed,
    )


train_xgboost_batched_energy_pca_as_target_node = node(
    train_xgboost_batched_energy_pca_as_target,
    inputs=[
        "X_train_batched_energy_pca_as_target_dataset_preprocessed",
        "y_train_batched_energy_pca_as_target_dataset",
        "fitted_fpca",
        "X_train_batched_energy_pca_as_target_dataset",
        "X_train_dataset",
    ],
    outputs=[
        "trained_xgboost_batched_energy_pca_as_target",
        "y_train_batched_energy_pca_as_target_dataset_predicted",
        "y_train_batched_energy_pca_as_target_dataset_predicted_reconstructed",
    ],
    name="train_xgboost_batched_energy_pca_as_target",
)

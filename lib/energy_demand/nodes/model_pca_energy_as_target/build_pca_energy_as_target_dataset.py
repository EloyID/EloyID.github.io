import pandas as pd
from kedro.pipeline import node

from energy_demand.config import N_PCA_COMPONENTS
from energy_demand.const import FPC_COLUMN_PATTERN
from energy_demand.nodes.utils import get_fpca_values


def build_batched_energy_pca_as_target_dataset(
    train_daily_info,
    test_daily_info,
    batched_input_data,
    fitted_fpca,
    batches,
):
    functional_principal_components = get_fpca_values(
        fitted_fpca=fitted_fpca,
        batches=batches,
        batched_data=batched_input_data,
        pivot_values="Precio Compra/Venta",
        pivot_columns="Energía Compra/Venta Acumulada",
    )

    functional_principal_components["Fecha UTC + 1D"] = functional_principal_components[
        "Fecha UTC"
    ] + pd.Timedelta(days=1)

    train_dataset = pd.merge(
        train_daily_info,
        functional_principal_components.drop("Fecha UTC", axis=1),
        left_on="Fecha UTC",
        right_on="Fecha UTC + 1D",
        how="left",
        validate="many_to_one",
    ).dropna()

    test_dataset = pd.merge(
        test_daily_info,
        functional_principal_components.drop("Fecha UTC", axis=1),
        left_on="Fecha UTC",
        right_on="Fecha UTC + 1D",
        how="left",
        validate="many_to_one",
    )

    functional_components_column_names = [
        FPC_COLUMN_PATTERN.format(pc_number=i + 1) for i in range(N_PCA_COMPONENTS)
    ]

    X_train_dataset = train_dataset.drop(functional_components_column_names, axis=1)
    y_train_dataset = train_dataset[functional_components_column_names]

    X_test_dataset = test_dataset.drop(functional_components_column_names, axis=1)
    y_test_dataset = test_dataset[functional_components_column_names]

    return X_train_dataset, y_train_dataset, X_test_dataset, y_test_dataset


build_batched_energy_pca_as_target_dataset_node = node(
    build_batched_energy_pca_as_target_dataset,
    inputs=[
        "train_daily_info",
        "test_daily_info",
        "batched_input_data",
        "fitted_fpca",
        "batches",
    ],
    outputs=[
        "X_train_batched_energy_pca_as_target_dataset",
        "y_train_batched_energy_pca_as_target_dataset",
        "X_test_batched_energy_pca_as_target_dataset",
        "y_test_batched_energy_pca_as_target_dataset",
    ],
    name="build_batched_energy_pca_as_target_dataset",
)

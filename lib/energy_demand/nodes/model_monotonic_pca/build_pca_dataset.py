import pandas as pd
from kedro.pipeline import node

from energy_demand.nodes.utils import get_fpca_values


def build_pca_dataset(
    train_merged_input_data,
    test_merged_input_data,
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
        train_merged_input_data,
        functional_principal_components.drop("Fecha UTC", axis=1),
        left_on="Fecha UTC",
        right_on="Fecha UTC + 1D",
        how="left",
        validate="many_to_one",
    ).dropna()

    test_dataset = pd.merge(
        test_merged_input_data,
        functional_principal_components.drop("Fecha UTC", axis=1),
        left_on="Fecha UTC",
        right_on="Fecha UTC + 1D",
        how="left",
        validate="many_to_one",
    )

    X_train_dataset = train_dataset.drop("Precio Compra/Venta", axis=1)
    y_train_dataset = train_dataset["Precio Compra/Venta"]

    X_test_dataset = test_dataset.drop("Precio Compra/Venta", axis=1)
    y_test_dataset = test_dataset["Precio Compra/Venta"]

    return X_train_dataset, y_train_dataset, X_test_dataset, y_test_dataset


build_pca_dataset_node = node(
    build_pca_dataset,
    inputs=[
        "train_merged_input_data",
        "test_merged_input_data",
        "batched_input_data",
        "fitted_fpca",
        "batches",
    ],
    outputs=["X_train_dataset", "y_train_dataset", "X_test_dataset", "y_test_dataset"],
    name="build_pca_dataset",
)

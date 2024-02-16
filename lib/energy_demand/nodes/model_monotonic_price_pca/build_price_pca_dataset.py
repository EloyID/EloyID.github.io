import pandas as pd
from kedro.pipeline import node

from energy_demand.nodes.utils import get_fpca_values


# TODO: refactor
def build_price_pca_dataset(
    train_merged_input_data,
    test_merged_input_data,
    batched_price_input_data,
    fitted_price_fpca,
    batches,
):
    functional_principal_components = get_fpca_values(
        fitted_fpca=fitted_price_fpca,
        batches=batches,
        batched_data=batched_price_input_data,
        pivot_values="Energía Compra/Venta Acumulada",
        pivot_columns="Precio Compra/Venta",
    )

    functional_principal_components["Fecha UTC + 1D"] = functional_principal_components[
        "Fecha UTC"
    ] + pd.Timedelta(days=1)

    train_price_dataset = pd.merge(
        train_merged_input_data,
        functional_principal_components.drop("Fecha UTC", axis=1),
        left_on="Fecha UTC",
        right_on="Fecha UTC + 1D",
        how="left",
        validate="many_to_one",
    ).dropna()

    test_price_dataset = pd.merge(
        test_merged_input_data,
        functional_principal_components.drop("Fecha UTC", axis=1),
        left_on="Fecha UTC",
        right_on="Fecha UTC + 1D",
        how="left",
        validate="many_to_one",
    )

    X_train_price_pca_dataset = train_price_dataset.drop(
        "Energía Compra/Venta Acumulada", axis=1
    )
    y_train_price_pca_dataset = train_price_dataset["Energía Compra/Venta Acumulada"]

    X_test_price_pca_dataset = test_price_dataset.drop(
        "Energía Compra/Venta Acumulada", axis=1
    )
    y_test_price_pca_dataset = test_price_dataset["Energía Compra/Venta Acumulada"]

    return (
        X_train_price_pca_dataset,
        y_train_price_pca_dataset,
        X_test_price_pca_dataset,
        y_test_price_pca_dataset,
    )


build_price_pca_dataset_node = node(
    build_price_pca_dataset,
    inputs=[
        "train_merged_input_data",
        "test_merged_input_data",
        "batched_price_input_data",
        "fitted_price_fpca",
        "price_batches",
    ],
    outputs=[
        "X_train_price_pca_dataset",
        "y_train_price_pca_dataset",
        "X_test_price_pca_dataset",
        "y_test_price_pca_dataset",
    ],
    name="build_price_pca_dataset",
)

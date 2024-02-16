import skfda
from kedro.pipeline import node
from skfda.preprocessing.dim_reduction.projection import FPCA

from energy_demand.config import N_PCA_COMPONENTS


def price_data_pca(batched_price_raw_train_dataset, price_batches):
    pivotted_batched_price_input_data = batched_price_raw_train_dataset.pivot_table(
        index="Fecha UTC",
        values="Energía Compra/Venta Acumulada",
        columns="Precio Compra/Venta",
        aggfunc="first",
    )

    price_fd = skfda.FDataGrid(
        data_matrix=pivotted_batched_price_input_data.values,
        grid_points=price_batches,
    )

    fitted_price_fpca = FPCA(n_components=N_PCA_COMPONENTS)
    fitted_price_fpca.fit(price_fd)

    return fitted_price_fpca


price_data_pca_node = node(
    price_data_pca,
    inputs=[
        "batched_price_raw_train_dataset",
        "price_batches",
    ],
    outputs="fitted_price_fpca",
    name="price_data_pca",
)

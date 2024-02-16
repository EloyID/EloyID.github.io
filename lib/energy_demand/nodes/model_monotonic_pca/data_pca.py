import matplotlib.pyplot as plt
import pandas as pd
import skfda
import sqlalchemy
from kedro.pipeline import node
from skfda.preprocessing.dim_reduction.projection import FPCA

from energy_demand.config import N_PCA_COMPONENTS
from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.exceptions import raise_exception_if_any_na


def data_pca(batched_raw_train_dataset, batches):
    pivotted_batched_input_data = batched_raw_train_dataset.pivot_table(
        index="Fecha UTC",
        columns="Energía Compra/Venta Acumulada",
        values="Precio Compra/Venta",
        aggfunc="first",
    )

    fd = skfda.FDataGrid(
        data_matrix=pivotted_batched_input_data.values,
        grid_points=batches,
    )

    fitted_fpca = FPCA(n_components=N_PCA_COMPONENTS)
    fitted_fpca.fit(fd)

    return fitted_fpca


data_pca_node = node(
    data_pca,
    inputs=["batched_raw_train_dataset", "batches"],
    outputs="fitted_fpca",
    name="data_pca",
)

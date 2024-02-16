from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import sqlalchemy
from kedro.pipeline import node

from energy_demand.const import PARAMS_DATE_PATTERN
from energy_demand.database.const import MYSQL_DATABASE_URI


def create_batched_input_data_table_plot(batched_input_data, merged_input_data):
    # Create a plot with two subplots
    fig, axs = plt.subplots(2, figsize=(10, 10))

    # First subplot
    example_dates = batched_input_data["Fecha UTC"].unique()[:3]
    example_batched_input_data = batched_input_data[
        batched_input_data["Fecha UTC"].isin(example_dates)
    ]

    for (date1, group1), (date2, group2) in zip(
        example_batched_input_data.groupby("Fecha UTC"),
        merged_input_data.groupby("Fecha UTC"),
    ):
        group1.sort_values("Energía Compra/Venta Acumulada").plot(
            "Energía Compra/Venta Acumulada",
            "Precio Compra/Venta",
            ax=axs[0],
            legend=False,
            linewidth=0.5,
        )

        group2.sort_values("Energía Compra/Venta Acumulada").plot(
            "Energía Compra/Venta Acumulada",
            "Precio Compra/Venta",
            ax=axs[0],
            legend=False,
            linewidth=0.5,
            linestyle="dashed",
        )
    axs[0].legend(["Batched", "Original"])

    axs[0].set_title(
        "Examples of batched Energía Compra/Venta Acumulada vs Precio Compra/Venta"
    )

    for date, group in batched_input_data.groupby("Fecha UTC"):
        group.sort_values("Energía Compra/Venta Acumulada").plot(
            "Energía Compra/Venta Acumulada",
            "Precio Compra/Venta",
            ax=axs[1],
            legend=False,
            linewidth=0.5,
        )
    axs[1].set_title("Batched Energía Compra/Venta Acumulada vs Precio Compra/Venta")

    return plt


create_batched_input_data_table_plot_node = node(
    create_batched_input_data_table_plot,
    inputs=[
        "batched_input_data",
        "featured_merged_input_data",
    ],
    outputs="create_batched_input_data_table_plots",
    name="create_batched_input_data_table_plot",
)

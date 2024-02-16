import matplotlib.pyplot as plt
import pandas as pd
import sqlalchemy
from kedro.pipeline import node

from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.exceptions import raise_exception_if_any_na


def end_of_data_extraction(
    featured_merged_input_data,
):
    plotting_featured_merged_input_data = featured_merged_input_data.copy()
    plotting_featured_merged_input_data["Fecha"] = featured_merged_input_data[
        "Fecha UTC"
    ].dt.date

    # create a figure with 6 subplots
    fig, axs = plt.subplots(6, figsize=(10, 10))

    # scatter 'Energía Compra/Venta' vs 'Precio Compra/venta'
    plotting_featured_merged_input_data.plot.scatter(
        "Energía Compra/Venta", "Precio Compra/Venta", ax=axs[0], s=0.1
    )
    axs[0].set_title("Energía Compra/Venta vs Precio Compra/Venta")

    # lines Fecha UTC (x) Predicción solar (y) Predicción eólica (y)
    plotting_featured_merged_input_data.plot(
        "Fecha UTC", ["Predicción solar", "Predicción eólica"], ax=axs[1]
    )
    axs[1].set_title("Fecha UTC vs Predicción solar and Predicción eólica")

    # group the data by 'Fecha'
    grouped = plotting_featured_merged_input_data.groupby("Fecha")

    # for each group, plot 'Hora' vs 'Predicción solar' and 'Hora' vs 'Predicción eólica'
    for name, group in grouped:
        group.plot(
            "Hora",
            "Predicción solar",
            ax=axs[2],
            legend=False,
            linewidth=0.5,
        )
        group.plot(
            "Hora",
            "Predicción eólica",
            ax=axs[3],
            legend=False,
            linewidth=0.5,
        )

    axs[2].set_title("Hora vs Predicción solar")
    axs[3].set_title("Hora vs Predicción eólica")

    # lines 'Energía Compra/Venta Acumulada' vs 'Precio Compra/venta', where the line shared only if same 'Fecha UTC'
    for date, group in plotting_featured_merged_input_data.groupby("Fecha UTC"):
        group = group.sort_values("Energía Compra/Venta Acumulada")
        group.plot(
            "Energía Compra/Venta Acumulada",
            "Precio Compra/Venta",
            ax=axs[4],
            legend=False,
            linewidth=0.5,
        )

    axs[4].set_title("Energía Compra/Venta Acumulada vs Precio Compra/Venta")

    plotting_featured_merged_input_data.plot.scatter(
        "Energía Compra/Venta Acumulada",
        "Energía Compra/Venta",
        ax=axs[5],
        c="Hora",
        colormap="viridis",
        legend=False,
        s=0.5,
    )
    axs[5].set_title("Energía Compra/Venta Acumulada vs Energía Compra/Venta")

    plt.tight_layout()

    return plt


end_of_data_extraction_node = node(
    end_of_data_extraction,
    inputs=[
        "featured_merged_input_data",
    ],
    outputs="featured_merged_input_data_plots",
    name="end_of_data_extraction",
)

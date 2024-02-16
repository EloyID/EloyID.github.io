import numpy as np
import pandas as pd
import sqlalchemy
from kedro.pipeline import node

from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.database.merged_input_data import create_merged_input_data_connection
from energy_demand.exceptions import raise_exception_if_any_na
from energy_demand.nodes.utils import latin_numeric_notation_to_numeric
from energy_demand.schemas import schemas_context


def merge_sios_data(pbc_data, sios_data, column_name):
    # Select necessary columns
    sios_data = sios_data[
        [
            "datetime",
            "value",
        ]
    ].copy()

    # Convert 'datetime' in sios_data to datetime
    sios_data["datetime"] = pd.to_datetime(sios_data["datetime"], utc=True)
    sios_data["value"] = pd.to_numeric(sios_data["value"])

    # Merge pbc_data with sios_data
    pbc_data = pd.merge(
        pbc_data,
        sios_data[["datetime", "value"]],
        left_on="Fecha UTC",
        right_on="datetime",
        how="left",
        validate="many_to_one",
    )

    # Rename 'value' column to 'Predicción eólica'
    pbc_data = pbc_data.rename(columns={"value": column_name})
    pbc_data = pbc_data.drop("datetime", axis=1)

    raise_exception_if_any_na(pbc_data)

    return pbc_data


def raw_pbc_data_date_hour_to_datetime(raw_pbc_data):
    dates = pd.to_datetime(raw_pbc_data["Fecha"], dayfirst=True)
    hour_timedelta = pd.to_timedelta(
        # Subtract 1 because 'Hora' ranges from 1 to 24
        pd.to_numeric(raw_pbc_data["Hora"]) - 1,
        unit="h",
    )
    datetime = dates + hour_timedelta
    datetime = datetime.dt.tz_localize("Europe/Madrid").dt.tz_convert("UTC")
    return datetime


def get_cumulative_energy(merged_input_data):
    # Returns a Series with the cumulative sum of 'Energía Compra/Venta' for each 'Fecha UTC'
    cumsum_energy_series = pd.Series(
        [np.nan] * len(merged_input_data), index=merged_input_data.index
    )

    df_o = (
        merged_input_data.loc[merged_input_data["Tipo Oferta"] == "V"]
        .sort_values(
            "Precio Compra/Venta",
        )
        .groupby(["Fecha UTC"])["Energía Compra/Venta"]
        .transform(pd.Series.cumsum)
    )

    df_c = (
        merged_input_data.loc[merged_input_data["Tipo Oferta"] == "C"]
        .sort_values(
            "Precio Compra/Venta",
            ascending=False,
        )
        .groupby(["Fecha UTC"])["Energía Compra/Venta"]
        .transform(pd.Series.cumsum)
    )

    cumsum_energy_series[df_o.index] = df_o
    cumsum_energy_series[df_c.index] = df_c

    raise_exception_if_any_na(cumsum_energy_series)

    return cumsum_energy_series


# TODO: rename
def transform_pbc_data(
    raw_pbc_data,
    raw_solar_data,
    raw_wind_data,
    bid_type,
    start_date,
    end_date,
    min_energy_cumsum,
    max_energy_cumsum,
):
    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)
    create_merged_input_data_connection()
    # Select necessary columns

    calculated_dates = pd.read_sql(
        "SELECT DISTINCT `Fecha UTC` FROM hades.merged_input_data", engine
    )

    calculated_dates = (
        (calculated_dates["Fecha UTC"].dt.tz_localize("UTC").dt.tz_convert("UTC"))
        if not calculated_dates.empty
        else pd.Series()
    )

    # Get the calculated 'Fecha UTC' values
    available_dates = pd.read_sql(
        "SELECT DISTINCT `Fecha`, `Hora` FROM hades.raw_pbc", engine
    )

    transformed_available_dates = raw_pbc_data_date_hour_to_datetime(available_dates)
    not_calculated_dates = available_dates[
        ~transformed_available_dates.isin(calculated_dates)
    ]

    if not not_calculated_dates.empty:
        not_calculated_raw_pbc_data = pd.read_sql(
            f"""SELECT * FROM raw_pbc
            WHERE (`Fecha`, `Hora`) IN {tuple(zip(not_calculated_dates["Fecha"], not_calculated_dates["Hora"]))}
            """,
            engine,
        )

        inserting_merged_input_data = not_calculated_raw_pbc_data[
            [
                "Hora",
                "Fecha",
                "Tipo Oferta",
                "Energía Compra/Venta",
                "Precio Compra/Venta",
                "Ofertada (O)/Casada (C)",
            ]
        ]

        # Convert columns to float
        # pd.to_numeric redundant to convert to cast as numeric since it was object
        inserting_merged_input_data.loc[:, "Energía Compra/Venta"] = pd.to_numeric(
            latin_numeric_notation_to_numeric(
                inserting_merged_input_data["Energía Compra/Venta"]
            )
        )
        inserting_merged_input_data.loc[:, "Precio Compra/Venta"] = pd.to_numeric(
            latin_numeric_notation_to_numeric(
                inserting_merged_input_data["Precio Compra/Venta"]
            )
        )

        inserting_merged_input_data.loc[
            :, "Fecha UTC"
        ] = raw_pbc_data_date_hour_to_datetime(inserting_merged_input_data)

        inserting_merged_input_data.loc[:, "Hora"] = (
            pd.to_numeric(inserting_merged_input_data["Hora"]) - 1
        )
        inserting_merged_input_data.loc[
            :, "Día de la semana"
        ] = inserting_merged_input_data["Fecha UTC"].dt.dayofweek

        # Drop the original 'Fecha' columns
        inserting_merged_input_data = inserting_merged_input_data.drop(
            ["Fecha"], axis=1
        )

        inserting_merged_input_data = merge_sios_data(
            inserting_merged_input_data, raw_solar_data, "Predicción solar"
        )
        inserting_merged_input_data = merge_sios_data(
            inserting_merged_input_data, raw_wind_data, "Predicción eólica"
        )

        inserting_merged_input_data[
            "Energía Compra/Venta Acumulada"
        ] = get_cumulative_energy(inserting_merged_input_data)

        inserting_merged_input_data = inserting_merged_input_data.to_sql(
            "merged_input_data",
            engine,
            if_exists="append",
            index=False,
        )

    merged_input_data = pd.read_sql(
        f"""
        SELECT * FROM merged_input_data 
        WHERE `Tipo Oferta` = '{bid_type}' 
        AND `Fecha UTC` BETWEEN '{start_date}' AND '{end_date}' 
        AND `Energía Compra/Venta Acumulada` BETWEEN {min_energy_cumsum} AND {max_energy_cumsum}
        ORDER BY `Fecha UTC` ASC
        """,
        engine,
    )

    return merged_input_data


# Define the node
transform_pbc_node = node(
    transform_pbc_data,
    inputs=[
        "raw_pbc_data",
        "raw_solar_data",
        "raw_wind_data",
        "params:bid_type",
        "params:start_date",
        "params:end_date",
        "params:min_energy_cumsum",
        "params:max_energy_cumsum",
    ],
    outputs="featured_merged_input_data",
    name="transform_pbc",
)

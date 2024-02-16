from datetime import datetime

import pandas as pd
import sqlalchemy
from kedro.pipeline import node

from energy_demand.const import PARAMS_DATE_PATTERN
from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.database.daily_info import create_daily_info_connection
from energy_demand.exceptions import raise_exception_if_any_na
from energy_demand.nodes.utils import extract_datetime_from_date_parameter


def create_daily_infos_table(
    raw_wind_data,
    raw_solar_data,
    start_date,
    end_date,
):
    connection = create_daily_info_connection()
    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)

    raw_wind_data = pd.read_sql_query(
        "SELECT datetime_utc, value FROM raw_wind", engine
    )
    raw_solar_data = pd.read_sql_query(
        "SELECT datetime_utc, value FROM raw_solar", engine
    )
    raw_wind_data["datetime_utc"] = pd.to_datetime(
        raw_wind_data["datetime_utc"]
    ).dt.tz_localize(None)
    wind_dates = raw_wind_data["datetime_utc"]

    raw_solar_data["datetime_utc"] = pd.to_datetime(
        raw_solar_data["datetime_utc"]
    ).dt.tz_localize(None)

    daily_infos_dates = pd.read_sql_query(
        "SELECT DISTINCT `Fecha UTC` FROM daily_info", engine
    )

    # Convert both date series to datetime and remove timezone information
    daily_infos_dates = pd.to_datetime(daily_infos_dates["Fecha UTC"]).dt.tz_localize(
        None
    )

    # Find the dates in wind_dates that are not in daily_infos_dates
    missing_dates = set(wind_dates) - set(daily_infos_dates)

    wind_data = raw_wind_data.loc[
        raw_wind_data["datetime_utc"].isin(missing_dates),
        ["datetime_utc", "value"],
    ]
    wind_data.columns = ["Fecha UTC", "Predicción eólica"]

    solar_data = raw_solar_data.loc[
        raw_solar_data["datetime_utc"].isin(missing_dates),
        ["datetime_utc", "value"],
    ]
    solar_data.columns = ["Fecha UTC", "Predicción solar"]

    data = pd.merge(wind_data, solar_data, on="Fecha UTC")
    data["Fecha UTC"] = pd.to_datetime(data["Fecha UTC"])

    data["Día de la semana"] = data["Fecha UTC"].dt.dayofweek
    data["Hora"] = data["Fecha UTC"].dt.hour

    raise_exception_if_any_na(data)
    data.to_sql("daily_info", engine, if_exists="append", index=False)

    start_date = extract_datetime_from_date_parameter(start_date)
    end_date = extract_datetime_from_date_parameter(end_date)

    daily_info = pd.read_sql_query(
        f"""SELECT * FROM daily_info 
        WHERE `Fecha UTC` BETWEEN '{start_date}' AND '{end_date}'
        """,
        engine,
    )

    return daily_info


create_daily_infos_table_node = node(
    create_daily_infos_table,
    inputs=[
        "raw_wind_data",
        "raw_solar_data",
        "params:start_date",
        "params:end_date",
    ],
    outputs="daily_info",
    name="create_daily_infos_table",
)

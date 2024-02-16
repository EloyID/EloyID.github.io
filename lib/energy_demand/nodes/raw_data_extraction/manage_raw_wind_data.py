from datetime import datetime, timedelta
from re import S

import pandas as pd
from ......src.energy_demand.sios_config import SIOS_CONFIG, SOLAR, WIND
import sqlalchemy
from kedro.pipeline import node

from energy_demand.const import PARAMS_DATE_PATTERN
from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.database.raw_solar import create_raw_solar_connection
from energy_demand.database.raw_wind import create_raw_wind_connection
from energy_demand.exceptions import raise_exception_if_any_na
from energy_demand.nodes.utils import extract_datetime_from_date_parameter


# Be careful is used in manage_raw_solar_data_node and manage_raw_wind_data_node
def manage_sios_data(start_date, end_date, archive):
    # establish a database connection
    connection = SIOS_CONFIG[archive]["create_connection"]()
    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)
    db_name = SIOS_CONFIG[archive]["raw_database_name"]

    # Check if the database has the corresponding data

    day_before_start_date = extract_datetime_from_date_parameter(
        start_date
    ) - timedelta(days=1)
    day_after_end_date = extract_datetime_from_date_parameter(end_date) + timedelta(
        days=1
    )

    day_before_start_str = day_before_start_date.strftime(PARAMS_DATE_PATTERN)
    day_after_end_str = day_after_end_date.strftime(PARAMS_DATE_PATTERN)
    two_days_before_start_str = (day_before_start_date - timedelta(days=1)).strftime(
        PARAMS_DATE_PATTERN
    )
    two_days_after_end_str = (day_after_end_date + timedelta(days=1)).strftime(
        PARAMS_DATE_PATTERN
    )

    data_datetimes = pd.read_sql_query(
        f"SELECT DISTINCT datetime_utc FROM {db_name} WHERE datetime_utc BETWEEN '{two_days_before_start_str}' AND '{two_days_after_end_str}'",
        engine,
    )
    data_datetimes = pd.to_datetime(data_datetimes["datetime_utc"], utc=True)

    # create a date range for every hour between start_date and end_date
    date_range = pd.date_range(
        start=day_before_start_date, end=day_after_end_date, freq="H", tz="UTC"
    )

    # check if any datetimes are missing from the data
    missing_datetimes = date_range[~date_range.isin(data_datetimes)]

    if not missing_datetimes.empty:
        # If all the data is not available, download the missing data using the API
        print(
            f"Downloading missing data from {archive} SIOS API for {len(missing_datetimes)} dates"
        )
        day_start_download = missing_datetimes.min().strftime(PARAMS_DATE_PATTERN)
        day_end_download = missing_datetimes.max().strftime(PARAMS_DATE_PATTERN)
        data = download_sios_data(day_start_download, day_end_download, archive)

        raise_exception_if_any_na(data)
        # Send it to the db
        print("Inserting data into db, it can take some minutes, please wait...")

        data_to_insert = data[
            pd.to_datetime(data["datetime_utc"], utc=True).isin(missing_datetimes)
        ]
        data_to_insert.to_sql(
            db_name,
            engine,
            if_exists="append",
            index=False,
        )

    # close the database connection
    connection.close()

    raw_sios_data = pd.read_sql_query(
        f"SELECT * FROM {db_name} WHERE datetime_utc BETWEEN '{day_before_start_str}' AND '{day_after_end_str}'",
        engine,
    )

    # Return the downloaded data + the already existing data in the db
    return raw_sios_data


def manage_raw_wind_data(start_date, end_date):
    return manage_sios_data(start_date, end_date, WIND)


manage_raw_wind_data_node = node(
    manage_raw_wind_data,
    inputs=["params:start_date", "params:end_date"],
    outputs="raw_wind_data",
    name="manage_raw_wind_data",
)


def manage_raw_solar_data(start_date, end_date):
    return manage_sios_data(start_date, end_date, SOLAR)


manage_raw_solar_data_node = node(
    manage_raw_solar_data,
    inputs=["params:start_date", "params:end_date"],
    outputs="raw_solar_data",
    name="manage_raw_solar_data",
)

def manage_raw_demand_
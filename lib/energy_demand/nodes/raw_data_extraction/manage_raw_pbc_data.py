from datetime import datetime

import pandas as pd
import sqlalchemy
from kedro.pipeline import node

from energy_demand.api import download_omie_data
from energy_demand.const import OMIE_DATE_PATTERN, SQL_OMIE_DATE_PATTERN
from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.database.raw_pbc import (
    create_raw_pbc_connection,
    insert_pbc_data_into_db,
)
from energy_demand.exceptions import raise_exception_if_any_na
from energy_demand.nodes.utils import extract_datetime_from_date_parameter


# TODO rename manage as download and insert into db
def manage_raw_pbc_data(start_date, end_date):
    # establish a database connection
    connection = create_raw_pbc_connection()
    cursor = connection.cursor()
    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)

    start_date = extract_datetime_from_date_parameter(start_date)
    end_date = extract_datetime_from_date_parameter(end_date)

    # create a date range for every day between start_date and end_date
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    # extract the date part from the 'Fecha' column and drop duplicates
    cursor.execute("SELECT DISTINCT `Fecha` FROM hades.raw_pbc")
    available_dates = cursor.fetchall()
    available_dates = [date[0] for date in available_dates]
    available_dates = pd.to_datetime(available_dates, format=OMIE_DATE_PATTERN)

    # check if any dates are missing from the data
    missing_dates = date_range[~date_range.isin(available_dates)]
    if not missing_dates.empty:
        print(f"Downloading missing data from OMIE API for {len(missing_dates)} dates")
        download_start_date = datetime.date(missing_dates.min())
        download_end_date = datetime.date(missing_dates.max())

        # If all the data is not available, download the missing data using the API
        data = download_omie_data(download_start_date, download_end_date)

        # Unidad is always empty
        raise_exception_if_any_na(data.drop("Unidad", axis="columns"))

        # Send it to the db
        print("Inserting data into db, it can take some minutes, please wait...")
        insert_pbc_data_into_db(data)

    # close the database connection
    connection.close()

    start_date_omie_format = start_date.strftime(OMIE_DATE_PATTERN)
    print(f"==>> start_date_omie_format: {start_date_omie_format}")
    end_date_omie_format = end_date.strftime(OMIE_DATE_PATTERN)
    print(f"==>> end_date_omie_format: {end_date_omie_format}")

    # Return the downloaded data + the already existing data in the db
    raw_pbc_data = pd.read_sql_query(
        f"""SELECT * FROM raw_pbc 
        WHERE STR_TO_DATE(Fecha, '{SQL_OMIE_DATE_PATTERN}') BETWEEN '{start_date}' AND '{end_date}'
        """,
        engine,
    )

    return raw_pbc_data


# create a node
manage_raw_pbc_data_node = node(
    manage_raw_pbc_data,
    inputs=["params:start_date", "params:end_date"],
    outputs="raw_pbc_data",
    name="manage_raw_pbc_data",
)

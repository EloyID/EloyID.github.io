from kedro.pipeline import node

from energy_demand.database.const import MYSQL_DATABASE_URI



import pandas as pd
import sqlalchemy


def extract_databases_to_parquet():
    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)
    merged_input_data = pd.read_sql("SELECT * FROM merged_input_data", engine)

    batched_input_data = pd.read_sql("SELECT * FROM batched_input_data", engine)

    daily_info = pd.read_sql("SELECT * FROM daily_info", engine)

    raw_pbc = pd.read_sql("SELECT * FROM raw_pbc", engine)

    raw_solar = pd.read_sql("SELECT * FROM raw_solar", engine)

    raw_wind = pd.read_sql("SELECT * FROM raw_wind", engine)

    return (
        merged_input_data,
        batched_input_data,
        daily_info,
        raw_pbc,
        raw_solar,
        raw_wind,
    )


extract_databases_to_parquet_node = node(
    extract_databases_to_parquet,
    inputs=None,
    outputs=[
        "merged_input_data_extract",
        "batched_input_data_extract",
        "daily_info_extract",
        "raw_pbc_extract",
        "raw_solar_extract",
        "raw_wind_extract",
    ],
    name="extract_databases_to_parquet",
)

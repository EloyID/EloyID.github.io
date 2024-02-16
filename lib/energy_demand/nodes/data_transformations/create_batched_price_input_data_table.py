from datetime import datetime

import numpy as np
import pandas as pd
import sqlalchemy
from kedro.pipeline import node

from energy_demand.const import DATABASE_DATE_PATTERN, PARAMS_DATE_PATTERN
from energy_demand.database.batched_price_input_data import (
    create_batched_price_input_data_connection,
)
from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.exceptions import raise_exception_if_any_na
from energy_demand.nodes.utils import (
    extract_datetime_from_date_parameter,
    interpolate_and_insert,
)


def create_batched_price_input_data_table(
    featured_merged_input_data, start_date, end_date, bid_type, batch_size
):
    # wandb.init(project="iit-energy-prediction")
    # wandb.log({"batch_size": batch_size})

    # Create a connection to the database
    connection = create_batched_price_input_data_connection()
    cursor = connection.cursor()
    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)
    # Execute a query to get the maximum value of 'Energía Compra/Venta Acumulada'
    cursor.execute(
        f"SELECT MAX(`Precio Compra/Venta`) FROM hades.merged_input_data WHERE `Tipo Oferta` = '{bid_type}'",
    )
    max_price = cursor.fetchone()[0]

    cursor.execute(
        f"SELECT MIN(`Precio Compra/Venta`) FROM hades.merged_input_data WHERE `Tipo Oferta` = '{bid_type}'",
    )
    min_price = cursor.fetchone()[0]
    batched_min_price = min(min_price - (min_price % batch_size), 0)

    batches = np.arange(batched_min_price, max_price + batch_size, batch_size)

    # Get the unique 'Fecha UTC' values
    cursor.execute(
        f"SELECT DISTINCT `Fecha UTC` FROM hades.merged_input_data WHERE `Tipo Oferta` = '{bid_type}' "
    )
    available_dates = cursor.fetchall()

    # Get the calculated 'Fecha UTC' values
    cursor.execute(
        f"SELECT DISTINCT `Fecha UTC` FROM hades.batched_price_input_data WHERE `Tipo Oferta` = '{bid_type}' "
    )
    calculated_dates = cursor.fetchall()

    # Get the calculated 'Fecha UTC' values
    cursor.execute(
        f"SELECT DISTINCT `Precio Compra/Venta` FROM hades.batched_price_input_data WHERE `Tipo Oferta` = '{bid_type}' "
    )
    calculated_price = cursor.fetchall()
    calculated_price = [x[0] for x in calculated_price]

    not_calculated_batches = list(set(batches) - set(calculated_price))
    not_calculated_batches.sort()
    if len(not_calculated_batches) != 0:
        for date in calculated_dates:
            date = date[0]
            # Download the data for the date into a pandas DataFrame
            interpolate_and_insert(
                x=not_calculated_batches,
                x_p="Precio Compra/Venta",
                fp="Energía Compra/Venta Acumulada",
                from_database="merged_input_data",
                to_database="batched_price_input_data",
                date=date,
                bid_type=bid_type,
            )

    # Process only the dates that are not already in the table
    not_calculated_dates = list(set(available_dates) - set(calculated_dates))
    for date in not_calculated_dates:
        date = date[0]
        # Download the data for the date into a pandas DataFrame
        interpolate_and_insert(
            x=batches,
            x_p="Precio Compra/Venta",
            fp="Energía Compra/Venta Acumulada",
            from_database="merged_input_data",
            to_database="batched_price_input_data",
            date=date,
            bid_type=bid_type,
        )

    connection.commit()

    # Close the connection
    connection.close()

    # Convert start_date and end_date to datetime
    start_date = extract_datetime_from_date_parameter(start_date)
    end_date = extract_datetime_from_date_parameter(end_date)

    # Create a connection to the database
    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)
    batches_str = ", ".join([str(batch) for batch in batches])

    # Write the SQL query
    query = f"""
    SELECT *
    FROM batched_price_input_data
    WHERE `Fecha UTC` >= '{start_date}'
    AND `Fecha UTC` <= '{end_date}'
    AND `Tipo Oferta` = '{bid_type}'
    AND `Precio Compra/Venta` IN ({batches_str})
    """

    batched_price_input_data = pd.read_sql(
        query,
        engine,
    )

    return batches, batched_price_input_data


# Define the Kedro node
create_batched_price_input_data_table_node = node(
    create_batched_price_input_data_table,
    inputs=[
        "featured_merged_input_data",
        "params:start_date",
        "params:end_date",
        "params:bid_type",
        "params:price_batch_size",
    ],
    outputs=["price_batches", "batched_price_input_data"],
    name="create_batched_price_input_data_table",
)

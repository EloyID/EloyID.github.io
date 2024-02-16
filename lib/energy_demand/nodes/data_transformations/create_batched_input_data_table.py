from datetime import datetime

import numpy as np
import pandas as pd
import sqlalchemy
from kedro.pipeline import node

from energy_demand.const import DATABASE_DATE_PATTERN, PARAMS_DATE_PATTERN
from energy_demand.database.batched_input_data import (
    create_batched_input_data_connection,
)
from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.exceptions import raise_exception_if_any_na
from energy_demand.nodes.utils import (
    extract_datetime_from_date_parameter,
    interpolate_and_insert,
)


def create_batched_input_data_table(
    featured_merged_input_data,
    start_date,
    end_date,
    bid_type,
    batch_size,
    min_energy_cumsum,
    max_energy_cumsum,
):
    # wandb.init(project="iit-energy-prediction")
    # wandb.log({"batch_size": batch_size})

    # Create a connection to the database
    connection = create_batched_input_data_connection()
    cursor = connection.cursor()
    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)

    batches = np.arange(min_energy_cumsum, max_energy_cumsum + batch_size, batch_size)

    # Get the unique 'Fecha UTC' values
    cursor.execute(
        f"SELECT DISTINCT `Fecha UTC` FROM hades.merged_input_data WHERE `Tipo Oferta` = '{bid_type}' "
    )
    available_dates = cursor.fetchall()

    # Get the calculated 'Fecha UTC' values
    cursor.execute(
        f"SELECT DISTINCT `Fecha UTC` FROM hades.batched_input_data WHERE `Tipo Oferta` = '{bid_type}'"
    )
    calculated_dates = cursor.fetchall()

    # Get the calculated 'Fecha UTC' values
    cursor.execute(
        f"SELECT DISTINCT `Energía Compra/Venta Acumulada` FROM hades.batched_input_data WHERE `Tipo Oferta` = '{bid_type}'"
    )
    calculated_energy_cumsum = cursor.fetchall()
    calculated_energy_cumsum = [x[0] for x in calculated_energy_cumsum]

    not_calculated_batches = list(set(batches) - set(calculated_energy_cumsum))
    not_calculated_batches.sort()
    # Process the calculated dates with existing batches not matching the new batches
    if len(not_calculated_batches) != 0:
        for date in calculated_dates:
            date = date[0]
            # Download the data for the date into a pandas DataFrame

            interpolate_and_insert(
                x=not_calculated_batches,
                x_p="Energía Compra/Venta Acumulada",
                fp="Precio Compra/Venta",
                from_database="merged_input_data",
                to_database="batched_input_data",
                date=date,
                bid_type=bid_type,
            )

    # Process the dates that are not at all in the table
    not_calculated_dates = list(set(available_dates) - set(calculated_dates))
    for date in not_calculated_dates:
        date = date[0]
        # Download the data for the date into a pandas DataFrame
        interpolate_and_insert(
            x=batches,
            x_p="Energía Compra/Venta Acumulada",
            fp="Precio Compra/Venta",
            from_database="merged_input_data",
            to_database="batched_input_data",
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
    FROM batched_input_data
    WHERE `Fecha UTC` >= '{start_date}'
    AND `Fecha UTC` <= '{end_date}'
    AND `Tipo Oferta` = '{bid_type}'
    AND `Energía Compra/Venta Acumulada` IN ({batches_str})
    AND `Energía Compra/Venta Acumulada` BETWEEN {min_energy_cumsum} AND {max_energy_cumsum}
    """

    batched_input_data = pd.read_sql(
        query,
        engine,
    )

    return batches, batched_input_data


# Define the Kedro node
create_batched_input_data_table_node = node(
    create_batched_input_data_table,
    inputs=[
        "featured_merged_input_data",
        "params:start_date",
        "params:end_date",
        "params:bid_type",
        "params:batch_size",
        "params:min_energy_cumsum",
        "params:max_energy_cumsum",
    ],
    outputs=["batches", "batched_input_data"],
    name="create_batched_input_data_table",
)

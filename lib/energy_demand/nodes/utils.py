from datetime import datetime

import numpy as np
import pandas as pd
import skfda
import sqlalchemy

from energy_demand.config import N_PCA_COMPONENTS
from energy_demand.const import (
    DATABASE_DATE_PATTERN,
    FPC_COLUMN_PATTERN,
    PARAMS_DATE_PATTERN,
)
from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.exceptions import raise_exception_if_any_na


def extract_datetime_from_date_parameter(date):
    """Extract datetime from date parameter

    Arguments
    ---------
    date : str
        Date string

    Returns
    -------
    datetime
    """
    return datetime.strptime(date, PARAMS_DATE_PATTERN).date()


def latin_numeric_notation_to_numeric(pandas_series):
    """Convert latin numeric notation to numeric
    Takes into account that the decimal separator is a comma and the
    thousands separator is a dot

    Arguments
    ---------
    pandas_series : pandas.Series
        Pandas series

    Returns
    -------
    pandas.Series
    """
    return pd.to_numeric(
        pandas_series.astype("str")
        .replace("\.", "", regex=True)
        .replace(",", ".", regex=True)
    )


def interpolate_and_insert(x, x_p, fp, from_database, to_database, date, bid_type):
    """Interpolate and insert values into a database

    Arguments
    ---------
    x : numpy.ndarray
        Array of x values
    x_p : str
        Name of the x column
    fp : str
        Name of the y column
    from_database : str
        Name of the database to read from
    to_database : str
        Name of the database to write to
    date : datetime.date
        Date of the data
    bid_type : str
        Type of bid
    """

    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)
    df = pd.read_sql(
        f"SELECT * FROM {from_database} WHERE `Fecha UTC` = '{date.strftime(DATABASE_DATE_PATTERN)}' AND `Tipo Oferta` = '{bid_type}' ORDER BY `{x_p}` ASC",
        engine,
        # sort values because the interpolation function needs the values to be sorted
    )

    # Group by 'Precio Compra/Venta' and keep only the row with the highest 'Energía Compra/Venta Acumulada' in each group
    # np.interp() does not work with duplicate values
    df = df.loc[df.groupby(x_p)[fp].idxmax()]

    interpolated_values = np.interp(
        x,
        df[x_p].values,
        df[fp].values,
    )

    inserting_values = pd.DataFrame(
        {
            "Fecha UTC": date,
            x_p: x,
            fp: interpolated_values,
            "Tipo Oferta": bid_type,
        }
    )

    raise_exception_if_any_na(inserting_values)

    inserting_values.to_sql(
        to_database,
        engine,
        if_exists="append",
        index=False,
    )


def get_fpca_values(
    fitted_fpca,
    batches,
    batched_data,
    pivot_values,
    pivot_columns,
    index_column="Fecha UTC",
):
    functional_components_column_names = [
        FPC_COLUMN_PATTERN.format(pc_number=i + 1) for i in range(N_PCA_COMPONENTS)
    ]

    pivotted_batched_input_data = batched_data.pivot_table(
        index=index_column,
        values=pivot_values,
        columns=pivot_columns,
        aggfunc="first",
    )

    fd = skfda.FDataGrid(
        data_matrix=pivotted_batched_input_data.values,
        grid_points=batches,
    )

    functional_principal_components = fitted_fpca.transform(fd)
    functional_principal_components = pd.DataFrame(
        functional_principal_components,
        columns=functional_components_column_names,
    )

    functional_principal_components[index_column] = pd.Series(
        pivotted_batched_input_data.index
    )

    return functional_principal_components

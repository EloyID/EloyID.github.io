import mysql.connector
import pandas as pd
import sqlalchemy
from mysql.connector import Error
from tqdm import tqdm

from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.database.utils import get_database_connection


def create_raw_pbc_connection():
    """create a database connection to a MySQL database"""
    conn = None
    try:
        conn = get_database_connection()
        if conn.is_connected():
            print(f"Successful connection with MySQL version {conn.get_server_info()}")

            # create the 'raw_pbc' table if it doesn't exist
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS raw_pbc (
                    Hora VARCHAR(2),
                    Fecha VARCHAR(20),
                    Pais CHAR(2),
                    Unidad VARCHAR(10),
                    `Tipo Oferta` CHAR(1),
                    `Energía Compra/Venta` VARCHAR(20),
                    `Precio Compra/Venta` VARCHAR(20),
                    `Ofertada (O)/Casada (C)` CHAR(1)
                )
            """
            )
    except Error as e:
        print(f"The error {e} occurred")
    return conn


def insert_pbc_data_into_db(data):
    engine = sqlalchemy.create_engine(MYSQL_DATABASE_URI)

    groups = data.groupby(["Fecha"])

    with tqdm(total=len(groups)) as pbar:
        for _, group in groups:
            group.to_sql(
                "raw_pbc",
                engine,
                if_exists="append",
                index=False,
                # method="multi",
            )
            pbar.update()

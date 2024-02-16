import mysql.connector
import pandas as pd
import sqlalchemy
from mysql.connector import Error

from energy_demand.database.const import MYSQL_DATABASE_URI
from energy_demand.database.utils import get_database_connection


def create_merged_input_data_connection():
    """create a database connection to a MySQL database"""
    conn = None
    try:
        conn = get_database_connection()
        if conn.is_connected():
            print(f"Successful connection with MySQL version {conn.get_server_info()}")

            # create the 'merged_input_data' table if it doesn't exist
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS merged_input_data (
                    `Tipo Oferta` CHAR(1),
                    `Energía Compra/Venta` FLOAT,
                    `Precio Compra/Venta` FLOAT,
                    `Ofertada (O)/Casada (C)` CHAR(1),
                    `Fecha UTC` DATETIME,
                    `Hora` INT,
                    `Día de la semana` INT,
                    `Predicción solar` FLOAT,
                    `Predicción eólica` FLOAT,
                    `Energía Compra/Venta Acumulada` FLOAT,
                    UNIQUE INDEX idx_pbc_all (`Fecha UTC`, `Tipo Oferta`, `Energía Compra/Venta Acumulada`)
                )
                """
            )
    except Error as e:
        print(f"The error {e} occurred")
    return conn

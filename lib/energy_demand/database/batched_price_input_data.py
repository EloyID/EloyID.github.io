import mysql.connector
from mysql.connector import Error

from energy_demand.database.utils import get_database_connection


def create_batched_price_input_data_connection():
    """create a database connection to a MySQL database"""
    conn = None
    try:
        conn = get_database_connection()
        if conn.is_connected():
            print(f"Successful connection with MySQL version {conn.get_server_info()}")

            # create the 'batched_input_data' table if it doesn't exist
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS batched_price_input_data (
                    `Tipo Oferta` CHAR(1),
                    `Precio Compra/Venta` FLOAT,
                    `Fecha UTC` DATETIME,
                    `Energía Compra/Venta Acumulada` FLOAT,
                    UNIQUE KEY idx_datetime_type_energy (`Fecha UTC`, `Tipo Oferta`, `Precio Compra/Venta`)
                )
                """
            )
    except Error as e:
        print(f"The error {e} occurred")
    return conn

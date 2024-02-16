import mysql.connector
import pandas as pd
from mysql.connector import Error

from energy_demand.database.utils import get_database_connection


def create_daily_info_connection():
    """create a database connection to a MySQL database"""
    conn = None
    try:
        conn = get_database_connection()
        if conn.is_connected():
            print(f"Successful connection with MySQL version {conn.get_server_info()}")

            # create the 'daily_info' table if it doesn't exist
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_info (
                    `Fecha UTC` DATETIME,
                    `Predicción solar` FLOAT,
                    `Predicción eólica` FLOAT,
                    `Día de la semana` INT,
                    Hora INT,
                    UNIQUE INDEX idx_date (`Fecha UTC`)
                )
            """
            )
    except Error as e:
        print(f"The error {e} occurred")
    return conn

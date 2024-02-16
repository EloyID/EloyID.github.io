import mysql.connector
from mysql.connector import Error

from energy_demand.database.const import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_USER,
)


def get_database_connection():
    conn = None
    try:
        conn = mysql.connector.connect(
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
        )

    except Error as e:
        print(f"The error {e} occurred")
    return conn

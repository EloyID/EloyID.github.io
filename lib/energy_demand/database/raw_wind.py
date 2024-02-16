from datetime import datetime, timedelta

import mysql.connector
import pandas as pd
from mysql.connector import Error

from energy_demand.const import PARAMS_DATE_PATTERN
from energy_demand.database.utils import get_database_connection


def create_raw_wind_connection():
    """create a database connection to a SQLite database"""
    try:
        conn = get_database_connection()

        if conn.is_connected():
            print("Successfully connected to MySQL")

            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS raw_wind (
                    value VARCHAR(30),
                    datetime VARCHAR(30),
                    datetime_utc VARCHAR(30),
                    tz_time VARCHAR(30),
                    geo_id VARCHAR(20),
                    geo_name VARCHAR(20),
                    UNIQUE KEY idx_datetime_utc (datetime_utc)
                )
            """
            )
    except Error as e:
        print(f"The error {e} occurred")

    return conn

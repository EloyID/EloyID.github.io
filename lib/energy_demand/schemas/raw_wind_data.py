from pandera import Column, DataFrameSchema, String

raw_wind_data = DataFrameSchema(
    {
        "value": Column(String, nullable=False),
        "datetime": Column(String, nullable=False),
        "datetime_utc": Column(String, nullable=False),
        "tz_time": Column(String, nullable=False),
        "geo_id": Column(String, nullable=False),
        "geo_name": Column(String, nullable=False),
    },
    unique=["datetime"],
    strict=True,
)

raw_solar_data = raw_wind_data

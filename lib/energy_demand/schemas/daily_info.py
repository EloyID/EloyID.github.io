from pandera import DataFrameSchema

from .standard_columns import standard_columns

daily_info = DataFrameSchema(
    {
        "Fecha UTC": standard_columns["Fecha UTC"],
        "Predicción solar": standard_columns["Predicción solar"],
        "Predicción eólica": standard_columns["Predicción eólica"],
        "Día de la semana": standard_columns["Día de la semana"],
        "Hora": standard_columns["Hora"],
    },
    unique=["Fecha UTC"],
    strict=True,
)

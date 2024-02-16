from pandera import DataFrameSchema

from .standard_columns import standard_columns

train_merged_input_data = DataFrameSchema(
    {
        "Fecha UTC": standard_columns["Fecha UTC"],
        "Predicción solar": standard_columns["Predicción solar"],
        "Predicción eólica": standard_columns["Predicción eólica"],
        "Precio Compra/Venta": standard_columns["Precio Compra/Venta"],
        "Energía Compra/Venta Acumulada": standard_columns[
            "Energía Compra/Venta Acumulada"
        ],
        "Día de la semana": standard_columns["Día de la semana"],
        "Hora": standard_columns["Hora"],
    },
    unique=["Fecha UTC", "Energía Compra/Venta Acumulada"],
    strict=True,
)

test_merged_input_data = train_merged_input_data

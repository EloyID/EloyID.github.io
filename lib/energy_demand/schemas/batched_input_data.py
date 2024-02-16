from pandera import DataFrameSchema

from .standard_columns import standard_columns

batched_input_data = DataFrameSchema(
    {
        "Tipo Oferta": standard_columns["Tipo Oferta ~ filtered"],
        "Precio Compra/Venta": standard_columns["Precio Compra/Venta"],
        "Fecha UTC": standard_columns["Fecha UTC"],
        "Energía Compra/Venta Acumulada": standard_columns[
            "Energía Compra/Venta Acumulada"
        ],
    },
    unique=["Fecha UTC", "Energía Compra/Venta Acumulada"],
    strict=True,
)

batched_raw_train_dataset = batched_input_data
batched_raw_test_dataset = batched_input_data

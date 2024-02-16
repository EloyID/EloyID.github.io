from pandera import Check, Column, DataFrameSchema, DateTime, Int, Timestamp

from .standard_columns import standard_columns

featured_merged_input_data_structure = {
    "Tipo Oferta": standard_columns["Tipo Oferta ~ filtered"],
    "Precio Compra/Venta": standard_columns["Precio Compra/Venta"],
    # I was having SchemaError: expected series 'Fecha UTC' to have type datetime64[ns], got datetime64[ns, UTC]
    "Fecha UTC": Column(DateTime, nullable=False, coerce=True),
    "Predicción solar": standard_columns["Predicción solar"],
    "Predicción eólica": standard_columns["Predicción eólica"],
    "Energía Compra/Venta": standard_columns["Energía Compra/Venta"],
    "Ofertada (O)/Casada (C)": standard_columns["Ofertada (O)/Casada (C)"],
    # I was having SchemaError: expected series 'Hora' to have type int64, got int32
    "Día de la semana": Column(Int, Check.in_range(0, 6), nullable=False, coerce=True),
    "Hora": Column(Int, Check.in_range(0, 23), nullable=False, coerce=True),
    "Energía Compra/Venta Acumulada": standard_columns[
        "Energía Compra/Venta Acumulada"
    ],
}


featured_merged_input_data = DataFrameSchema(
    featured_merged_input_data_structure,
    unique=["Fecha UTC", "Energía Compra/Venta Acumulada"],
    strict=True,
)

from pandera import Category, Check, Column, DataFrameSchema, String

from energy_demand.const import BID_TYPE_CATEGORIES

from .standard_columns import standard_columns

raw_pbc_data = DataFrameSchema(
    {
        "Hora": Column(String, nullable=False),
        "Fecha": Column(String, nullable=False),
        "Pais": Column(String, nullable=False),
        "Unidad": Column(String, nullable=True),
        "Tipo Oferta": standard_columns["Tipo Oferta"],
        "Energía Compra/Venta": Column(String, nullable=False),
        "Precio Compra/Venta": Column(String, nullable=False),
        "Ofertada (O)/Casada (C)": standard_columns["Ofertada (O)/Casada (C)"],
    },
    strict=True,
)

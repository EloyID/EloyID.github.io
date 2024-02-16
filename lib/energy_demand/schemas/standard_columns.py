from pandera import Category, Check, Column, DateTime, Float, Int

from energy_demand.const import BID_TYPE_CATEGORIES, MATCH_STATE_CATEGORIES

standard_columns = {
    "Precio Compra/Venta": Column(Float, [Check.in_range(-500, 3000)], nullable=False),
    "Energía Compra/Venta": Column(Float, Check.ge(0), nullable=False),
    "Ofertada (O)/Casada (C)": Column(
        Category,
        checks=[Check.isin(MATCH_STATE_CATEGORIES)],
        coerce=True,
        nullable=False,
    ),
    "Fecha UTC": Column(DateTime, nullable=False),
    "Predicción solar": Column(Float, Check.ge(0), nullable=False),
    "Predicción eólica": Column(Float, Check.ge(0), nullable=False),
    "Energía Compra/Venta Acumulada": Column(Float, Check.ge(0), nullable=False),
    # TODO adjust 0-6 or 1-7 depending on the case
    "Día de la semana": Column(Int, Check.in_range(0, 7), nullable=False),
    "Hora": Column(Int, Check.in_range(0, 23), nullable=False),
    "functional_principal_component": Column(Float, regex=True, nullable=False),
    "Tipo Oferta ~ filtered": Column(
        Category,
        checks=[
            Check.isin(BID_TYPE_CATEGORIES),
            # There should not be mixed C and V
            Check(lambda s: len(s.unique()) == 1, element_wise=False),
        ],
        coerce=True,
        nullable=False,
    ),
    "Tipo Oferta": Column(
        Category,
        checks=[
            Check.isin(BID_TYPE_CATEGORIES),
            # There should not be mixed C and V
        ],
        coerce=True,
        nullable=False,
    ),
}

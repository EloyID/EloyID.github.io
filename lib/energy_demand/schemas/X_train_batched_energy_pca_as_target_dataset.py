from pandera import DataFrameSchema

from .standard_columns import standard_columns

X_train_batched_energy_pca_as_target_dataset = DataFrameSchema(
    {
        "Fecha UTC": standard_columns["Fecha UTC"],
        "Fecha UTC + 1D": standard_columns["Fecha UTC"],
        "Predicción solar": standard_columns["Predicción solar"],
        "Predicción eólica": standard_columns["Predicción eólica"],
        "Día de la semana": standard_columns["Día de la semana"],
        "Hora": standard_columns["Hora"],
    },
    unique=["Fecha UTC", "Energía Compra/Venta Acumulada"],
    strict=True,
)

X_test_batched_energy_pca_as_target_dataset = (
    X_train_batched_energy_pca_as_target_dataset
)

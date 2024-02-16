from pandera import DataFrameSchema

from .standard_columns import standard_columns

y_train_batched_energy_pca_as_target_dataset = DataFrameSchema(
    {
        "functional_principal_component_.+": standard_columns[
            "functional_principal_component"
        ]
    },
    strict=True,
)

y_test_batched_energy_pca_as_target_dataset = (
    y_train_batched_energy_pca_as_target_dataset
)

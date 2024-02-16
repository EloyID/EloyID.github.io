from kedro.pipeline import node
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy import column


def preprocess_batched_energy_pca_as_target_dataset(
    X_train_batched_energy_pca_as_target_dataset,
    X_test_batched_energy_pca_as_target_dataset,
):
    X_train_dataset_filtered = X_train_batched_energy_pca_as_target_dataset.drop(
        ["Fecha UTC"], axis=1
    )

    categorical_columns = ["Día de la semana", "Hora"]
    numerical_columns = [
        "Predicción solar",
        "Predicción eólica",
    ]

    # create a pipeline for the categorical columns and the numerical columns
    categorical_pipeline = Pipeline(
        [
            ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    numerical_pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
        ]
    )

    # create a column transformer for the categorical and numerical pipelines
    column_transformer = ColumnTransformer(
        [
            ("categorical_pipeline", categorical_pipeline, categorical_columns),
            ("numerical_pipeline", numerical_pipeline, numerical_columns),
        ]
    )

    X_train_batched_energy_pca_as_target_dataset_preprocessed = (
        column_transformer.fit_transform(X_train_dataset_filtered)
    )

    X_test_batched_energy_pca_as_target_dataset = column_transformer.transform(
        X_test_batched_energy_pca_as_target_dataset.drop(["Fecha UTC"], axis=1)
    )

    return (
        X_train_batched_energy_pca_as_target_dataset_preprocessed,
        X_test_batched_energy_pca_as_target_dataset,
        column_transformer,
    )


preprocess_batched_energy_pca_as_target_dataset_node = node(
    preprocess_batched_energy_pca_as_target_dataset,
    inputs=[
        "X_train_batched_energy_pca_as_target_dataset",
        "X_test_batched_energy_pca_as_target_dataset",
    ],
    outputs=[
        "X_train_batched_energy_pca_as_target_dataset_preprocessed",
        "X_test_batched_energy_pca_as_target_dataset_preprocessed",
        "column_transformer_batched_energy_pca_as_target_dataset",
    ],
    name="preprocess_batched_energy_pca_as_target_dataset",
)

from kedro.pipeline import node
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def preprocess_price_pca_dataset(X_train_price_pca_dataset, X_test_price_pca_dataset):
    X_train_price_pca_dataset_filtered = X_train_price_pca_dataset.drop(
        ["Fecha UTC"], axis=1
    )

    categorical_columns = ["Día de la semana", "Hora"]
    numerical_columns = [
        "Predicción solar",
        "Predicción eólica",
        "Precio Compra/Venta",
        "functional_principal_component_1",
        "functional_principal_component_2",
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
    column_transformer_price_pca_dataset = ColumnTransformer(
        [
            ("categorical_pipeline", categorical_pipeline, categorical_columns),
            ("numerical_pipeline", numerical_pipeline, numerical_columns),
        ]
    )

    X_train_price_pca_dataset_preprocessed = (
        column_transformer_price_pca_dataset.fit_transform(
            X_train_price_pca_dataset_filtered
        )
    )

    X_test_price_pca_dataset_preprocessed = (
        column_transformer_price_pca_dataset.transform(
            X_test_price_pca_dataset.drop(["Fecha UTC"], axis=1)
        )
    )

    return (
        X_train_price_pca_dataset_preprocessed,
        X_test_price_pca_dataset_preprocessed,
        column_transformer_price_pca_dataset,
    )


preprocess_price_pca_dataset_node = node(
    preprocess_price_pca_dataset,
    inputs=["X_train_price_pca_dataset", "X_test_price_pca_dataset"],
    outputs=[
        "X_train_price_pca_dataset_preprocessed",
        "X_test_price_pca_dataset_preprocessed",
        "column_transformer_price_pca_dataset",
    ],
    name="preprocess_price_pca_dataset",
)

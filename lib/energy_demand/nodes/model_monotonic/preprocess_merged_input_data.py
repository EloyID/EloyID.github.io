from kedro.pipeline import node
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def preprocess_merged_input_data(train_merged_input_data, test_merged_input_data):
    X_train_merged_input_data = train_merged_input_data.drop(
        ["Precio Compra/Venta"], axis=1
    )
    y_train_merged_input_data = train_merged_input_data["Precio Compra/Venta"]

    X_test_merged_input_data = test_merged_input_data.drop(
        ["Precio Compra/Venta"], axis=1
    )
    y_test_merged_input_data = test_merged_input_data["Precio Compra/Venta"]

    categorical_columns = ["Día de la semana", "Hora"]
    numerical_columns = [
        "Predicción solar",
        "Predicción eólica",
        "Energía Compra/Venta Acumulada",
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

    X_train_merged_input_data_preprocessed = column_transformer.fit_transform(
        X_train_merged_input_data.drop(
            [
                "Fecha UTC",
            ],
            axis=1,
        )
    )

    X_test_merged_input_data_preprocessed = column_transformer.transform(
        X_test_merged_input_data.drop(
            [
                "Fecha UTC",
            ],
            axis=1,
        )
    )

    return (
        X_train_merged_input_data,
        y_train_merged_input_data,
        X_test_merged_input_data,
        y_test_merged_input_data,
        X_train_merged_input_data_preprocessed,
        X_test_merged_input_data_preprocessed,
        column_transformer,
    )


preprocess_merged_input_data_node = node(
    preprocess_merged_input_data,
    inputs=[
        "train_merged_input_data",
        "test_merged_input_data",
    ],
    outputs=[
        "X_train_merged_input_data",
        "y_train_merged_input_data",
        "X_test_merged_input_data",
        "y_test_merged_input_data",
        "X_train_merged_input_data_preprocessed",
        "X_test_merged_input_data_preprocessed",
        "column_transformer_merged_input_data",
    ],
    name="preprocess_merged_input_data",
)

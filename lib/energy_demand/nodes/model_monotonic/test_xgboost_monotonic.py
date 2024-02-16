from kedro.pipeline import node


def test_xgboost_monotonic(
    trained_xgboost_monotonic,
    X_test_merged_input_data,
    column_transformer_merged_input_data,
):
    X_test_merged_input_data_preprocessed = X_test_merged_input_data.drop(
        ["Fecha UTC"], axis=1
    )
    X_test_merged_input_data_preprocessed = (
        column_transformer_merged_input_data.transform(X_test_merged_input_data)
    )
    y_test_merged_input_data_predicted = trained_xgboost_monotonic.predict(
        X_test_merged_input_data_preprocessed
    )

    return y_test_merged_input_data_predicted


test_xgboost_monotonic_node = node(
    test_xgboost_monotonic,
    inputs=[
        "trained_xgboost_monotonic",
        "X_test_merged_input_data",
        "column_transformer_merged_input_data",
    ],
    outputs="y_test_merged_input_data_predicted",
    name="test_xgboost_monotonic",
)

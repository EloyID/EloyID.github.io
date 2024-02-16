from kedro.pipeline import node


def test_xgboost_price_pca_monotonic(
    trained_xgboost_price_pca_monotonic,
    X_test_price_pca_dataset_preprocessed,
):
    y_test_price_pca_dataset_predicted = trained_xgboost_price_pca_monotonic.predict(
        X_test_price_pca_dataset_preprocessed
    )

    return y_test_price_pca_dataset_predicted


test_xgboost_price_pca_monotonic_node = node(
    test_xgboost_price_pca_monotonic,
    inputs=[
        "trained_xgboost_price_pca_monotonic",
        "X_test_price_pca_dataset_preprocessed",
    ],
    outputs="y_test_price_pca_dataset_predicted",
    name="test_xgboost_price_pca_monotonic",
)

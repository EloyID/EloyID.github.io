from kedro.pipeline import node
from xgboost import XGBRegressor

from energy_demand.const import PRICE_PIPELINE_NAME


def train_xgboost_price_pca_monotonic(
    bid_type,
    X_train_price_pca_dataset_preprocessed,
    y_train_price_pca_dataset,
    column_transformer_price_pca_dataset,
):
    monotonic_value = -1 if bid_type == "C" else 1
    monotonic_condition = tuple(
        0 if column != PRICE_PIPELINE_NAME else monotonic_value
        for column in column_transformer_price_pca_dataset.get_feature_names_out()
    )

    xgbm = XGBRegressor(
        objective="reg:squarederror",
        seed=2022,
        monotone_constraints=monotonic_condition,
    )
    xgbm.fit(X_train_price_pca_dataset_preprocessed, y_train_price_pca_dataset)
    y_train_price_pca_dataset_predicted = xgbm.predict(
        X_train_price_pca_dataset_preprocessed
    )

    return xgbm, y_train_price_pca_dataset_predicted


train_xgboost_price_pca_monotonic_node = node(
    train_xgboost_price_pca_monotonic,
    inputs=[
        "params:bid_type",
        "X_train_price_pca_dataset_preprocessed",
        "y_train_price_pca_dataset",
        "column_transformer_price_pca_dataset",
    ],
    outputs=[
        "trained_xgboost_price_pca_monotonic",
        "y_train_price_pca_dataset_predicted",
    ],
    name="train_xgboost_price_pca_monotonic",
)

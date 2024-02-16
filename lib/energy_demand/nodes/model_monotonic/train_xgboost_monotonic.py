from energy_demand.const import (
    ENERGY_CUMSUM_PIPELINE_NAME,
)
from kedro.pipeline import node
from xgboost import XGBRegressor


def train_xgboost_monotonic(
    bid_type,
    X_train_merged_input_data_preprocessed,
    y_train_merged_input_data,
    column_transformer_merged_input_data,
):
    monotonic_value = -1 if bid_type == "C" else 1
    monotonic_condition = tuple(
        0 if column != ENERGY_CUMSUM_PIPELINE_NAME else monotonic_value
        for column in column_transformer_merged_input_data.get_feature_names_out()
    )

    xgbm = XGBRegressor(
        objective="reg:squarederror",
        seed=2022,
        monotone_constraints=monotonic_condition,
    )
    xgbm.fit(X_train_merged_input_data_preprocessed, y_train_merged_input_data)
    y_train_merged_input_data_predicted = xgbm.predict(
        X_train_merged_input_data_preprocessed
    )

    return xgbm, y_train_merged_input_data_predicted


train_xgboost_monotonic_node = node(
    train_xgboost_monotonic,
    inputs=[
        "params:bid_type",
        "X_train_merged_input_data_preprocessed",
        "y_train_merged_input_data",
        "column_transformer_merged_input_data",
    ],
    outputs=[
        "trained_xgboost_monotonic",
        "y_train_merged_input_data_predicted",
    ],
    name="train_xgboost_monotonic",
)

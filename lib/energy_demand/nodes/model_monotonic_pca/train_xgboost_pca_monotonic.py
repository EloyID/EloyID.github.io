from kedro.pipeline import node


from xgboost import XGBRegressor

from energy_demand.const import ENERGY_CUMSUM_PIPELINE_NAME


def train_xgboost_pca_monotonic(
    bid_type,
    X_train_dataset_preprocessed,
    y_train_dataset,
    column_transformer_pca_dataset,
):
    monotonic_value = -1 if bid_type == "C" else 1
    monotonic_condition = tuple(
        0 if column != ENERGY_CUMSUM_PIPELINE_NAME else monotonic_value
        for column in column_transformer_pca_dataset.get_feature_names_out()
    )

    xgbm = XGBRegressor(
        objective="reg:squarederror",
        seed=2022,
        monotone_constraints=monotonic_condition,
    )
    xgbm.fit(X_train_dataset_preprocessed, y_train_dataset)
    y_train_dataset_predicted = xgbm.predict(X_train_dataset_preprocessed)

    return xgbm, y_train_dataset_predicted


train_xgboost_pca_monotonic_node = node(
    train_xgboost_pca_monotonic,
    inputs=[
        "params:bid_type",
        "X_train_dataset_preprocessed",
        "y_train_dataset",
        "column_transformer_pca_dataset",
    ],
    outputs=["trained_xgboost_pca_monotonic", "y_train_dataset_predicted"],
    name="train_xgboost_pca_monotonic",
)

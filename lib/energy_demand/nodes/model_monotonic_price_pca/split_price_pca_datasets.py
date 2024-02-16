from kedro.pipeline import node


def split_price_pca_datasets(
    batched_price_input_data,
    train_dates,
    test_dates,
):
    batched_price_raw_train_dataset = batched_price_input_data[
        batched_price_input_data["Fecha UTC"].isin(train_dates)
    ]
    batched_price_raw_test_dataset = batched_price_input_data[
        batched_price_input_data["Fecha UTC"].isin(test_dates)
    ]

    return (
        batched_price_raw_train_dataset,
        batched_price_raw_test_dataset,
    )


split_price_pca_datasets_node = node(
    split_price_pca_datasets,
    inputs=[
        "batched_price_input_data",
        "train_dates",
        "test_dates",
    ],
    outputs=[
        "batched_price_raw_train_dataset",
        "batched_price_raw_test_dataset",
    ],
    name="split_price_pca_datasets",
)

from kedro.pipeline import node


def split_pca_datasets(
    batched_input_data,
    train_dates,
    test_dates,
):
    batched_raw_train_dataset = batched_input_data[
        batched_input_data["Fecha UTC"].isin(train_dates)
    ]
    batched_raw_test_dataset = batched_input_data[
        batched_input_data["Fecha UTC"].isin(test_dates)
    ]
    return (
        batched_raw_train_dataset,
        batched_raw_test_dataset,
    )


split_pca_datasets_node = node(
    split_pca_datasets,
    inputs=[
        "batched_input_data",
        "train_dates",
        "test_dates",
    ],
    outputs=[
        "batched_raw_train_dataset",
        "batched_raw_test_dataset",
    ],
    name="split_pca_datasets",
)

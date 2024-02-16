from kedro.pipeline import node
from sklearn.model_selection import train_test_split

from energy_demand.config import TEST_SIZE


def split_datasets(merged_input_data, daily_info):
    unique_dates = merged_input_data["Fecha UTC"].unique()

    (
        train_dates,
        test_dates,
    ) = train_test_split(unique_dates, test_size=TEST_SIZE, shuffle=False)

    merged_input_data = merged_input_data.drop(
        ["Energía Compra/Venta", "Ofertada (O)/Casada (C)", "Tipo Oferta"], axis=1
    )
    train_merged_input_data = merged_input_data[
        merged_input_data["Fecha UTC"].isin(train_dates)
    ]
    test_merged_input_data = merged_input_data[
        merged_input_data["Fecha UTC"].isin(test_dates)
    ]

    train_daily_info = daily_info[daily_info["Fecha UTC"].isin(train_dates)]
    test_daily_info = daily_info[daily_info["Fecha UTC"].isin(test_dates)]

    return (
        train_dates,
        test_dates,
        train_merged_input_data,
        test_merged_input_data,
        train_daily_info,
        test_daily_info,
    )


split_datasets_node = node(
    split_datasets,
    inputs=["featured_merged_input_data", "daily_info"],
    outputs=[
        "train_dates",
        "test_dates",
        "train_merged_input_data",
        "test_merged_input_data",
        "train_daily_info",
        "test_daily_info",
    ],
    name="split_datasets",
)

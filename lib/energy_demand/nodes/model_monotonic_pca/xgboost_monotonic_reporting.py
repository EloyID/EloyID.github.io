import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from kedro.pipeline import node
from matplotlib import cm
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ATTENTION! used in two different nodes, so if you change it, be careful
def xgboost_monotonic_reporting(
    X_train, y_train, y_train_pred, X_test, y_test, y_test_pred
):
    y_train_pred = pd.Series(y_train_pred, index=y_train.index)
    y_test_pred = pd.Series(y_test_pred, index=y_test.index)

    examples_length = 3
    colors = cm.viridis(np.linspace(0, 1, examples_length))

    X_train_dates = X_train["Fecha UTC"].unique()
    X_test_dates = X_test["Fecha UTC"].unique()

    # Create a plot with seven subplots
    fig, axs = plt.subplots(10, figsize=(10, 60))

    # First subplot
    axs[0].plot(X_train_dates, ["train"] * len(X_train_dates), color="blue")
    axs[0].plot(X_test_dates, ["test"] * len(X_test_dates), color="red")
    axs[0].set_title("Train and Test Data")
    axs[0].legend(["Train", "Test"])

    # Second subplot
    example_dates = X_train["Fecha UTC"].unique()[:examples_length]
    for i, date in enumerate(example_dates):
        data = X_train[X_train["Fecha UTC"] == date].sort_values(
            "Energía Compra/Venta Acumulada"
        )
        axs[1].plot(
            data["Energía Compra/Venta Acumulada"],
            y_train[data.index],
            color=colors[i],
        )
        axs[1].plot(
            data["Energía Compra/Venta Acumulada"],
            y_train_pred[data.index],
            color=colors[i],
            linestyle="dotted",
        )
    axs[1].set_title("Train Data Examples")
    axs[1].legend(["Actual", "Predicted"])

    for date, group in X_train.groupby("Fecha UTC"):
        group.sort_values("Energía Compra/Venta Acumulada", inplace=True)

        # Third subplot
        axs[2].plot(
            group["Energía Compra/Venta Acumulada"],
            y_train[group.index],
        )
        axs[2].set_title("Train Data")
        axs[2].legend(["Actual"])

        # Fourth subplot
        axs[3].plot(
            group["Energía Compra/Venta Acumulada"],
            y_train_pred[group.index],
            linestyle="dotted",
        )
        axs[3].set_title("Train Data Predicted")
        axs[3].legend(["Predicted"])

        # Fourth subplot
        axs[4].plot(
            group["Energía Compra/Venta Acumulada"],
            y_train_pred[group.index] - y_train[group.index],
        )
        axs[4].set_title("Train Data Predicted residuals")
        axs[4].legend(["Residual"])

    # Fifth subplot
    example_dates = X_test["Fecha UTC"].unique()[:examples_length]
    for i, date in enumerate(example_dates):
        data = X_test[X_test["Fecha UTC"] == date].sort_values(
            "Energía Compra/Venta Acumulada"
        )
        axs[5].plot(
            data["Energía Compra/Venta Acumulada"],
            y_test[data.index],
            color=colors[i],
        )
        axs[5].plot(
            data["Energía Compra/Venta Acumulada"],
            y_test_pred[data.index],
            color=colors[i],
            linestyle="dotted",
        )
    axs[5].set_title("Test Data Examples")
    axs[5].legend(["Actual", "Predicted"])

    for date, group in X_test.groupby("Fecha UTC"):
        group.sort_values("Energía Compra/Venta Acumulada", inplace=True)

        # Sixth subplot
        axs[6].plot(
            group["Energía Compra/Venta Acumulada"],
            y_test[group.index],
        )
        axs[6].set_title("Test Data")
        axs[6].legend(["Actual"])

        # Seventh subplot
        axs[7].plot(
            group["Energía Compra/Venta Acumulada"],
            y_test_pred[group.index],
            linestyle="dotted",
        )
        axs[7].set_title("Test Data Predicted")
        axs[7].legend(["Predicted"])

        axs[8].plot(
            group["Energía Compra/Venta Acumulada"],
            y_test_pred[group.index] - y_test[group.index],
        )
        axs[8].set_title("Test Data Predicted residuals")
        axs[8].legend(["Residual"])

    train_mae = mean_absolute_error(y_train, y_train_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)

    train_rmse = mean_squared_error(y_train, y_train_pred, squared=False)
    test_rmse = mean_squared_error(y_test, y_test_pred, squared=False)

    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    # Create a table comparing train and test metrics
    metrics_data = [
        ["MAE", train_mae, test_mae],
        ["RMSE", train_rmse, test_rmse],
        ["R2", train_r2, test_r2],
    ]
    table = axs[9].table(
        cellText=metrics_data, colLabels=["Metric", "Train", "Test"], loc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    return plt


# Kedro node
xgboost_monotonic_reporting_node = node(
    xgboost_monotonic_reporting,
    inputs=[
        "X_train_merged_input_data",
        "y_train_merged_input_data",
        "y_train_merged_input_data_predicted",
        "X_test_merged_input_data",
        "y_test_merged_input_data",
        "y_test_merged_input_data_predicted",
    ],
    outputs="xgboost_monotonic_reporting_plots",
    name="xgboost_monotonic_reporting",
)

# Kedro node
xgboost_monotonic_pca_reporting_node = node(
    xgboost_monotonic_reporting,
    inputs=[
        "X_train_dataset",
        "y_train_dataset",
        "y_train_dataset_predicted",
        "X_test_dataset",
        "y_test_dataset",
        "y_test_dataset_predicted",
    ],
    outputs="xgboost_monotonic_pca_reporting_plots",
    name="xgboost_monotonic_pca_reporting",
)


# Kedro node
xgboost_batched_energy_pca_as_target_reporting_node = node(
    xgboost_monotonic_reporting,
    inputs=[
        "X_train_dataset",
        "y_train_dataset",
        "y_train_batched_energy_pca_as_target_dataset_predicted_reconstructed",
        "X_test_dataset",
        "y_test_dataset",
        "y_test_batched_energy_pca_as_target_dataset_predicted_reconstructed",
    ],
    outputs="xgboost_batched_energy_pca_as_target_reporting_plots",
    name="xgboost_batched_energy_pca_as_target_reporting",
)

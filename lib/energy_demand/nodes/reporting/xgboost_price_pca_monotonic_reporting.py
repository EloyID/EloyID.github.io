from operator import index

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from kedro.pipeline import node
from matplotlib import cm
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ATTENTION! used in two different nodes, so if you change it, be careful
def xgboost_monotonic_price_pca_reporting(
    X_train, y_train, y_train_pred, X_test, y_test, y_test_pred
):
    y_train_pred = pd.Series(y_train_pred, index=y_train.index)
    y_test_pred = pd.Series(y_test_pred, index=y_test.index)

    # To calculate the error metrics of the price, we are interpolating the 'real' price
    # for the predicted energy values
    X_train_price_inferred = pd.Series(np.nan, index=y_train.index)
    X_test_price_inferred = pd.Series(np.nan, index=y_test.index)

    examples_length = 3
    colors = cm.viridis(np.linspace(0, 1, examples_length))

    X_train_dates = X_train["Fecha UTC"].unique()
    X_test_dates = X_test["Fecha UTC"].unique()

    # Create a plot with seven subplots
    fig, axs = plt.subplots(15, figsize=(10, 80))

    # First subplot
    axs[0].plot(X_train_dates, ["train"] * len(X_train_dates), color="blue")
    axs[0].plot(X_test_dates, ["test"] * len(X_test_dates), color="red")
    axs[0].set_title("Train and Test Data")
    axs[0].legend(["Train", "Test"])

    # Second subplot
    example_dates = X_train["Fecha UTC"].unique()[:examples_length]
    for i, date in enumerate(example_dates):
        y_data = y_train[X_train[X_train["Fecha UTC"] == date].index].sort_values()
        data = X_train.loc[y_data.index]

        axs[1].plot(
            y_data,
            data["Precio Compra/Venta"],
            color=colors[i],
        )
        axs[1].plot(
            y_train_pred[y_data.index],
            data["Precio Compra/Venta"],
            color=colors[i],
            linestyle="dotted",
        )
    axs[1].set_title("Train Data Examples")
    axs[1].legend(["Actual", "Predicted"])

    for date, group in X_train.groupby("Fecha UTC"):
        y_data = y_train[group.index].sort_values()
        group = group.loc[y_data.index]

        # Third subplot
        axs[2].plot(
            y_data,
            group["Precio Compra/Venta"],
        )

        # Fourth subplot
        axs[3].plot(
            y_train_pred[y_data.index],
            group["Precio Compra/Venta"],
            linestyle="dotted",
        )

        # Fourth subplot
        axs[4].plot(
            y_train_pred[y_data.index] - y_data,
            group["Precio Compra/Venta"],
        )

        X_train_price_inferred[y_data.index] = np.interp(
            y_train_pred[y_data.index], y_data, group["Precio Compra/Venta"]
        )

        axs[5].plot(
            y_train_pred[y_data.index],
            X_train_price_inferred[y_data.index],
            linestyle="dashed",
        )

        axs[6].plot(
            y_data,
            X_train_price_inferred[y_data.index] - group["Precio Compra/Venta"],
        )

    axs[2].set_title("Train Data")
    axs[2].legend(["Actual"])
    axs[3].set_title("Train Data Predicted")
    axs[3].legend(["Predicted"])
    axs[4].set_title("Train Data price predicted residuals")
    axs[4].legend(["Residual"])
    axs[5].set_title("Train Data actual price interpolated for predicted energy values")
    axs[5].legend(["Interpolated"])
    axs[6].set_title(
        "Train Data price interpolated for predicted energy values residuals"
    )
    axs[6].legend(["Residual"])

    # Fifth subplot
    example_dates = X_test["Fecha UTC"].unique()[:examples_length]
    for i, date in enumerate(example_dates):
        y_data = y_test[X_test[X_test["Fecha UTC"] == date].index].sort_values()
        data = X_test.loc[y_data.index]

        axs[7].plot(
            y_data,
            data["Precio Compra/Venta"],
            color=colors[i],
        )
        axs[7].plot(
            y_test_pred[y_data.index],
            data["Precio Compra/Venta"],
            color=colors[i],
            linestyle="dotted",
        )
    axs[7].set_title("Test Data Examples")
    axs[7].legend(["Actual", "Predicted"])

    for date, group in X_test.groupby("Fecha UTC"):
        y_data = y_test[group.index].sort_values()
        group = group.loc[y_data.index]

        # Third subplot
        axs[8].plot(
            y_data,
            group["Precio Compra/Venta"],
        )

        # Fourth subplot
        axs[9].plot(
            y_test_pred[y_data.index],
            group["Precio Compra/Venta"],
            linestyle="dotted",
        )

        # Fourth subplot
        axs[10].plot(
            y_test_pred[y_data.index] - y_data,
            group["Precio Compra/Venta"],
        )

        X_test_price_inferred[y_data.index] = np.interp(
            y_test_pred[y_data.index], y_data, group["Precio Compra/Venta"]
        )

        axs[11].plot(
            y_test_pred[y_data.index],
            X_test_price_inferred[y_data.index],
            linestyle="dashed",
        )

        axs[12].plot(
            y_data,
            X_test_price_inferred[y_data.index] - group["Precio Compra/Venta"],
        )

    axs[8].set_title("Test Data")
    axs[8].legend(["Actual"])
    axs[9].set_title("Test Data Predicted")
    axs[9].legend(["Predicted"])
    axs[10].set_title("Test Data Predicted residuals")
    axs[10].legend(["Residual"])
    axs[11].set_title("Test Data actual price interpolated for predicted energy values")
    axs[11].legend(["Interpolated"])
    axs[12].set_title(
        "Test Data price interpolated for predicted energy values residuals"
    )
    axs[12].legend(["Residual"])

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
    table = axs[13].table(
        cellText=metrics_data, colLabels=["Metric", "Train", "Test"], loc="center"
    )
    axs[13].set_title("Metrics comparison for energy quantity prediction")

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    interpolated_train_mae = mean_absolute_error(
        X_train["Precio Compra/Venta"], X_train_price_inferred
    )
    interpolated_test_mae = mean_absolute_error(
        X_test["Precio Compra/Venta"], X_test_price_inferred
    )

    interpolated_train_rmse = mean_squared_error(
        X_train["Precio Compra/Venta"], X_train_price_inferred, squared=False
    )
    interpolated_test_rmse = mean_squared_error(
        X_test["Precio Compra/Venta"], X_test_price_inferred, squared=False
    )

    interpolated_train_r2 = r2_score(
        X_train["Precio Compra/Venta"], X_train_price_inferred
    )
    interpolated_test_r2 = r2_score(
        X_test["Precio Compra/Venta"], X_test_price_inferred
    )

    # Create a table comparing train and test metrics
    interpolated_metrics_data = [
        ["MAE", interpolated_train_mae, interpolated_test_mae],
        ["RMSE", interpolated_train_rmse, interpolated_test_rmse],
        ["R2", interpolated_train_r2, interpolated_test_r2],
    ]

    interpolated_table = axs[14].table(
        cellText=interpolated_metrics_data,
        colLabels=["Metric", "Train", "Test"],
        loc="center",
    )

    axs[14].set_title("Metrics comparison for price prediction")
    interpolated_table.auto_set_font_size(False)
    interpolated_table.set_fontsize(10)
    interpolated_table.scale(1, 1.5)

    return plt


# Kedro node

xgboost_monotonic_price_pca_reporting_node = node(
    xgboost_monotonic_price_pca_reporting,
    inputs=[
        "X_train_price_pca_dataset",
        "y_train_price_pca_dataset",
        "y_train_price_pca_dataset_predicted",
        "X_test_price_pca_dataset",
        "y_test_price_pca_dataset",
        "y_test_price_pca_dataset_predicted",
    ],
    outputs="xgboost_monotonic_price_pca_reporting_plots",
    name="xgboost_monotonic_price_pca_reporting",
)

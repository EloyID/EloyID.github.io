import numpy as np
import pandas as pd


def reconstruct_data_from_pcas(
    fitted_fpca,
    X_batched_energy_pca_as_target_dataset,
    y_batched_energy_pca_as_target_dataset_predicted,
    original_dataset,
    date_column="Fecha UTC",
):
    batched_energy_pca_as_target_dataset_predicted_reconstructed = (
        fitted_fpca.inverse_transform(y_batched_energy_pca_as_target_dataset_predicted)
    )

    y_batched_energy_pca_as_target_dataset_predicted_reconstructed = pd.Series(
        np.zeros(len(original_dataset)),
        name="Precio Compra/Venta",
        index=original_dataset.index,
    )

    for idx, date in enumerate(X_batched_energy_pca_as_target_dataset[date_column]):
        date_merged_input_data = original_dataset[original_dataset["Fecha UTC"] == date]

        batched_energy_pca_as_target_dataset_predicted_reconstructed_y_points = (
            batched_energy_pca_as_target_dataset_predicted_reconstructed.data_matrix[
                idx
            ].flatten()
        )

        y_batched_energy_pca_as_target_dataset_predicted_reconstructed.loc[
            date_merged_input_data.index
        ] = np.interp(
            date_merged_input_data["Energía Compra/Venta Acumulada"],
            batched_energy_pca_as_target_dataset_predicted_reconstructed.grid_points[0],
            batched_energy_pca_as_target_dataset_predicted_reconstructed_y_points,
        )

    y_batched_energy_pca_as_target_dataset_predicted_reconstructed.dropna(inplace=True)

    return y_batched_energy_pca_as_target_dataset_predicted_reconstructed

from .batched_input_data import (
    batched_input_data,
    batched_raw_test_dataset,
    batched_raw_train_dataset,
)
from .daily_info import daily_info
from .featured_merged_input_data import featured_merged_input_data
from .raw_pbc_data import raw_pbc_data
from .raw_wind_data import raw_solar_data, raw_wind_data
from .train_merged_input_data import test_merged_input_data, train_merged_input_data
from .X_train_batched_energy_pca_as_target_dataset import (
    X_test_batched_energy_pca_as_target_dataset,
    X_train_batched_energy_pca_as_target_dataset,
)
from .y_train_batched_energy_pca_as_target_dataset import (
    y_test_batched_energy_pca_as_target_dataset,
    y_train_batched_energy_pca_as_target_dataset,
)

schemas_context = {
    "X_train_batched_energy_pca_as_target_dataset": X_train_batched_energy_pca_as_target_dataset,
    "y_train_batched_energy_pca_as_target_dataset": y_train_batched_energy_pca_as_target_dataset,
    "X_test_batched_energy_pca_as_target_dataset": X_test_batched_energy_pca_as_target_dataset,
    "y_test_batched_energy_pca_as_target_dataset": y_test_batched_energy_pca_as_target_dataset,
    "batched_input_data": batched_input_data,
    "batched_raw_train_dataset": batched_raw_train_dataset,
    "batched_raw_test_dataset": batched_raw_test_dataset,
    "featured_merged_input_data": featured_merged_input_data,
    "test_merged_input_data": test_merged_input_data,
    "train_merged_input_data": train_merged_input_data,
    "daily_info": daily_info,
    "raw_solar_data": raw_solar_data,
    "raw_wind_data": raw_wind_data,
    "raw_pbc_data": raw_pbc_data,
}

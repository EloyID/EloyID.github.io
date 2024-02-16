from kedro.pipeline import Pipeline

from .nodes import (  # batch_energy_cumsum_node,
    build_batched_energy_pca_as_target_dataset_node,
    build_pca_dataset_node,
    build_price_pca_dataset_node,
    create_batched_input_data_table_node,
    create_batched_input_data_table_plot_node,
    create_batched_price_input_data_table_node,
    create_batched_price_input_data_table_plot_node,
    create_daily_infos_table_node,
    data_pca_node,
    end_of_data_extraction_node,
    extract_databases_to_parquet_node,
    manage_raw_pbc_data_node,
    manage_raw_solar_data_node,
    manage_raw_wind_data_node,
    preprocess_batched_energy_pca_as_target_dataset_node,
    preprocess_merged_input_data_node,
    preprocess_pca_dataset_node,
    preprocess_price_pca_dataset_node,
    price_data_pca_node,
    split_datasets_node,
    split_pca_datasets_node,
    split_price_pca_datasets_node,
    test_xgboost_batched_energy_pca_as_target_node,
    test_xgboost_monotonic_node,
    test_xgboost_pca_monotonic_node,
    test_xgboost_price_pca_monotonic_node,
    train_xgboost_batched_energy_pca_as_target_node,
    train_xgboost_monotonic_node,
    train_xgboost_pca_monotonic_node,
    train_xgboost_price_pca_monotonic_node,
    transform_pbc_node,
    xgboost_batched_energy_pca_as_target_reporting_node,
    xgboost_monotonic_pca_reporting_node,
    xgboost_monotonic_price_pca_reporting_node,
    xgboost_monotonic_reporting_node,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            manage_raw_pbc_data_node,
            manage_raw_solar_data_node,
            manage_raw_wind_data_node,
            create_daily_infos_table_node,
            transform_pbc_node,
            end_of_data_extraction_node,
            # xgboost without pca
            preprocess_merged_input_data_node,
            train_xgboost_monotonic_node,
            test_xgboost_monotonic_node,
            # xgboost with pca
            create_batched_input_data_table_node,
            create_batched_price_input_data_table_plot_node,
            split_pca_datasets_node,
            data_pca_node,
            build_pca_dataset_node,
            split_datasets_node,
            split_price_pca_datasets_node,
            preprocess_pca_dataset_node,
            train_xgboost_pca_monotonic_node,
            test_xgboost_pca_monotonic_node,
            # xgboost with pca price
            price_data_pca_node,
            build_price_pca_dataset_node,
            preprocess_price_pca_dataset_node,
            train_xgboost_price_pca_monotonic_node,
            test_xgboost_price_pca_monotonic_node,
            # xgboost with pca energy as target
            build_batched_energy_pca_as_target_dataset_node,
            preprocess_batched_energy_pca_as_target_dataset_node,
            train_xgboost_batched_energy_pca_as_target_node,
            test_xgboost_batched_energy_pca_as_target_node,
            xgboost_batched_energy_pca_as_target_reporting_node,
            # reporting
            create_batched_input_data_table_plot_node,
            xgboost_monotonic_reporting_node,
            xgboost_monotonic_pca_reporting_node,
            create_batched_price_input_data_table_node,
            xgboost_monotonic_price_pca_reporting_node,
            # other nodes...
        ]
    )


def create_extract_databases_to_parquet_pipeline(**kwargs):
    return Pipeline(
        [
            extract_databases_to_parquet_node,
            # other nodes...
        ]
    )

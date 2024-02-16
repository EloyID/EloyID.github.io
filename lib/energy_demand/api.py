import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests

from energy_demand.const import PARAMS_DATE_PATTERN
from energy_demand.nodes.utils import extract_datetime_from_date_parameter

SIOS_URL_PATTERN = "https://api.esios.ree.es/indicators/{archive_id}"
PBC_URL_PATTERN = "https://www.omie.es/es/file-download?parents%5B0%5D=curva_pbc&filename=curva_pbc_{yymmdd}.1"
YYMMDD_FORMAT = "%Y%m%d"

SOLAR = "Solar"
WIND = "Eólica"
SOLAR_ARCHIVE_ID = 1779
WIND_ARCHIVE_ID = 1777

SIOS_TOKEN = os.environ.get("SIOS_TOKEN")
SIOS_HEADERS = {
    "Accept": "application/json; application/vnd.esios-api-v1+json",
    "Content-Type": "application/json",
    "x-api-key": f"{SIOS_TOKEN}",
}


def download_omie_data(start_date, end_date):
    dates = [
        start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)
    ]

    downloaded_dates = 0

    def download_and_format_omie_data(date):
        url = PBC_URL_PATTERN.format(yymmdd=date.strftime(YYMMDD_FORMAT))
        raw_data = pd.read_csv(url, sep=";", header=1, encoding="latin-1")
        raw_data = raw_data[~raw_data.isna().all(axis=1)]
        nonlocal downloaded_dates
        downloaded_dates += 1
        if downloaded_dates % 10 == 0:
            print(f"Downloaded {downloaded_dates} dates out of {len(dates)}")

        return raw_data

    with ThreadPoolExecutor(max_workers=None) as executor:
        dataframes = list(executor.map(download_and_format_omie_data, dates))

    print(f"Downloaded {len(dates)} dates info")
    pbc_full_raw_data = (
        pd.concat(dataframes, ignore_index=True)
        .drop(columns=["Unnamed: 8"])
        .replace([np.nan], [None])
    )
    return pbc_full_raw_data


def download_sios_data(start_date, end_date, archive):
    archive_id = SOLAR_ARCHIVE_ID if archive == SOLAR else WIND_ARCHIVE_ID
    # the timedelta is to make sure we get all the data we need since
    # utc is a mess
    day_before_start_date = (
        extract_datetime_from_date_parameter(start_date) - timedelta(days=1)
    ).strftime(PARAMS_DATE_PATTERN)
    day_after_end_date = (
        extract_datetime_from_date_parameter(end_date) + timedelta(days=1)
    ).strftime(PARAMS_DATE_PATTERN)
    response = requests.get(
        url=SIOS_URL_PATTERN.format(archive_id=archive_id),
        headers=SIOS_HEADERS,
        params={
            "start_date": day_before_start_date,
            "end_date": day_after_end_date,
        },
        timeout=10,
    ).json()

    data = pd.DataFrame.from_dict(response["indicator"]["values"])
    return data

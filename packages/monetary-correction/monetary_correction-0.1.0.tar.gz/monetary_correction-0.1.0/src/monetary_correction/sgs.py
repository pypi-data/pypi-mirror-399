#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: sgs.py
#  Version: 0.0.1
#
#  Summary: Monetary Correction
#           A simple, robust Python library to deflate nominal Brazilian
#           Reais using official price indexes from the Brazilian Central
#           Bank's SGS API.
#
#  Author: Alexsander Lopes Camargos
#  Author-email: alexcamargos@gmail.com
#
#  License: MIT
# ------------------------------------------------------------------------------

from datetime import date
from functools import lru_cache
from typing import cast

import polars as pl
from grabharvester.interfaces import FileOperationError, NetworkDownloadError

import src.monetary_correction.config as Cfg
from src.monetary_correction.utils import get_downloader, get_temp_file_path


@lru_cache(maxsize=32)
def _fetch_sgs_data(series_id: int,
                    start_date: str,
                    end_date: str) -> pl.DataFrame:
    """Fetch SGS data for a given series ID and date range.

    Args:
        series_id (int): The SGS series ID.
        start_date (str): The start date in 'DD/MM/YYYY' format.
        end_date (str): The end date in 'DD/MM/YYYY' format.

    Returns:
        pl.DataFrame: DataFrame containing the SGS data.

    Raises:
        RuntimeError: If there is an error during data download or processing.
    """

    url = Cfg.SGS_BASE_URL.format(series_id=series_id,
                                  start_date=start_date,
                                  end_date=end_date)

    # Use a unique temporary file to avoid race conditions in concurrent environments.
    temp_path = get_temp_file_path(prefix="sgs_data")

    try:
        response = get_downloader().download_file(url, temp_path)

        data = pl.read_json(response)
        data = data.select(
            [
                pl.col('data').str.strptime(pl.Date, '%d/%m/%Y').alias('date'),
                pl.col('valor').cast(pl.Float64).alias('value')
            ]
        )
        data = data.sort('date')

        return data
    except (NetworkDownloadError, FileOperationError) as error:
        raise RuntimeError(f'Failed to download SGS data: {error}') from error
    finally:
        if temp_path.exists():
            temp_path.unlink()


def fetch_index_values(dates: pl.Series,
                       series_id: int) -> pl.DataFrame:
    """Fetch index values from SGS for given dates and series ID.

    Args:
        dates (pl.Series): Series of dates for which to fetch index values.
        series_id (int): The SGS series ID.

    Returns:
        pl.Series: Series of index values.
    """

    start_date = cast(date, dates.min()).strftime('%d/%m/%Y')
    end_date = cast(date, dates.max()).strftime('%d/%m/%Y')

    return _fetch_sgs_data(series_id, start_date, end_date)

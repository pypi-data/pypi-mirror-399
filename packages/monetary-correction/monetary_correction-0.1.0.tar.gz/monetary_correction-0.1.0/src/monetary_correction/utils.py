#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: utils.py
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

import tempfile
import uuid
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

import polars as pl
from grabharvester.downloader import DownloadService


def to_series(value: list | str | float | Decimal | int | pl.Series,
              name: str) -> pl.Series:
    """Convert input to Polars Series.

    Args:
        value (list | str | float | Decimal | int | pl.Series): The input value(s).
        name (str): The name of the input.

    Returns:
        pl.Series: The converted Polars Series.

    Raises:
        ValueError: If the input type is not supported.
    """

    if isinstance(value, (str, float, int, Decimal)):
        return pl.Series([value])
    elif isinstance(value, list):
        return pl.Series(value)
    elif isinstance(value, pl.Series):
        return value

    raise ValueError(f'Invalid input type for {name} parameter')


def validate_series_length(series: pl.Series,
                           length: int,
                           name: str) -> pl.Series:
    """Validate and broadcast series to the target length.

    Args:
        series (pl.Series): The input series.
        length (int): The target length.
        name (str): The name of the input series.

    Returns:
        pl.Series: The validated and broadcasted series.

    Raises:
        ValueError: If the series length does not match the target length.
    """

    if len(series) == 1 and length > 1:
        return pl.Series([series[0]] * length)

    if len(series) != length:
        raise ValueError(f'Length mismatch for {name}: expected {length}, got {len(series)}')

    return series


@lru_cache(maxsize=1)
def get_downloader() -> DownloadService:
    """Get a singleton instance of DownloadService.

    Returns:
        DownloadService: The download service instance.
    """
    return DownloadService()


def get_temp_file_path(prefix: str = 'data',
                       suffix: str = '.json') -> Path:
    """Generate a unique temporary file path.

    Args:
        prefix (str): The prefix for the filename.
        suffix (str): The suffix for the filename.

    Returns:
        Path: The path to the temporary file.
    """

    return Path(tempfile.gettempdir()) / f'{prefix}_{uuid.uuid4()}{suffix}'

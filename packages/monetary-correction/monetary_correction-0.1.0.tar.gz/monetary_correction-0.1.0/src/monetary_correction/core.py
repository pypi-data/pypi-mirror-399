#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: core.py
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

from decimal import Decimal

import polars as pl

import src.monetary_correction.config as Cfg
from src.monetary_correction.domain import extract_monetary_factors
from src.monetary_correction.sgs import fetch_index_values
from src.monetary_correction.utils import to_series, validate_series_length


def monetary_correction(nominal_value: list[float] | list[Decimal] | float | Decimal | pl.Series,
                        nominal_date: list[str] | str | pl.Series,
                        real_date: list[str] | str | pl.Series,
                        index_name: str) -> list[float] | list[Decimal] | float | Decimal | pl.Series:
    """Perform monetary correction on a nominal value using specified price index.

    Args:
        nominal_value (list[float] | list[Decimal] | float | Decimal | pl.Series): The nominal value(s) to be corrected.
        nominal_date (list[str] | str | pl.Series): The date(s) corresponding to the nominal value(s).
        real_date (list[str] | str | pl.Series): The date(s) to which the nominal value(s) will be corrected.
        index_name (str): The price index name to be used for correction.

    Returns:
        list[float] | list[Decimal] | float | Decimal | pl.Series: The corrected nominal value(s).

    Raises:
        ValueError: If input lengths are inconsistent or date formats are incorrect.
        RuntimeError: If there is an error during data download or processing.
    """

    # Convert inputs to Polars Series for uniform processing.
    nominal_value_series = to_series(nominal_value, 'nominal_value')
    nominal_date_series = to_series(nominal_date, 'nominal_date')
    real_date_series = to_series(real_date, 'real_date')
    index_name_series = to_series(index_name, 'index_name')

    # Determine target length for broadcasting inputs.
    target_len = max(len(nominal_value_series),
                     len(nominal_date_series),
                     len(real_date_series),
                     len(index_name_series))

    # Validate and broadcast all series to target length.
    nominal_value_series = validate_series_length(nominal_value_series,
                                                  target_len,
                                                  'nominal_value')
    nominal_date_series = validate_series_length(nominal_date_series,
                                                 target_len,
                                                 'nominal_date')
    real_date_series = validate_series_length(real_date_series,
                                              target_len,
                                              'real_date')
    index_name_series = validate_series_length(index_name_series,
                                               target_len,
                                              'index_name')

    # Normalize real_dates to month start.
    try:
        real_date_series = real_date_series.str.strptime(pl.Date, format='%m/%Y')
        real_date_adjusted = real_date_series.dt.month_start()
    except ValueError as error:
        raise ValueError("Real date must be in 'MM/YYYY' format") from error

    # Normalize nominal_dates to month start.
    try:
        nominal_date_series = nominal_date_series.str.strptime(pl.Date, format="%m/%Y")
        nominal_date_adjusted = nominal_date_series.dt.month_start()
    except ValueError as error:
        raise ValueError("Nominal dates must be in 'MM/YYYY' format") from error

    # Fetch index values for the entire range needed; concat dates to find the
    # min/max range required for the SGS query
    all_dates = pl.concat([nominal_date_adjusted, real_date_adjusted])
    series_id = Cfg.Indices[index_name_series[0].upper()].value

    index_data = fetch_index_values(all_dates, series_id)

    # Calculate Cumulative Index from Monthly Percentages.
    # Formula: Cumulative Factor = Product(1 + value/100)
    index_data = index_data.sort("date").with_columns(
        (1 + pl.col("value") / 100).cum_prod().alias("cum_factor")
    )

    # Shift cum_factor to allow including the inflation of the month itself when dividing.
    # normalized = cum_factor / shifted_cum_factor_of_start
    index_data = index_data.with_columns(
        pl.col("cum_factor").shift(1, fill_value=1.0).alias("shifted_cum_factor")
    )

    # For Nominal Date: Use shifted_cum_factor to INCLUDE that month's inflation in the interval
    factor_nominal = extract_monetary_factors(nominal_date_adjusted,
                                              index_data,
                                              'shifted_cum_factor')

    # For Real Date: Use cum_factor to INCLUDE up to that month (or exclude? Standard is to include up to last)
    factor_real = extract_monetary_factors(real_date_adjusted,
                                           index_data,
                                           'cum_factor')

    # Calculate final correction factor; if data is missing for a date,
    # this will result in null, which is correct behavior for safety.
    correction_factor = factor_real / factor_nominal

    return nominal_value_series * correction_factor

#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: domain.py
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

import polars as pl


def extract_monetary_factors(dates: pl.Series,
                             index_data: pl.DataFrame,
                             col_name: str) -> pl.Series:
    """Extract monetary factors for given dates.

    Args:
        dates (pl.Series): Series of dates for which to extract factors.
        index_data (pl.DataFrame): The DataFrame containing the index values.
        col_name (str): The name of the column to extract.

    Returns:
        pl.Series: Series of monetary factors.
    """

    df_dates = pl.DataFrame(
        {
            'date': dates,
            'idx': pl.arange(0, len(dates), eager=True)
        }
    )

    # Left join to keep original order and size of dates.
    joined = df_dates.join(index_data, on='date', how='left').sort('idx')

    return joined[col_name]

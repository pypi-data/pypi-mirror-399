#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: __init__.py
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

from .core import monetary_correction


__all__ = [
    "monetary_correction"
]

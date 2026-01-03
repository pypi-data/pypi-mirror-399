#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: config.py
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

from enum import IntEnum


# SGS Base URL
SGS_BASE_URL: str = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados?formato=json&dataInicial={start_date}&dataFinal={end_date}'


class Indices(IntEnum):
    """Series Codes for SGS."""

    # IPCA (int): Índice Nacional de Preços ao Consumidor Amplo (IPCA)
    IPCA = 433
    # IGPM (int): Índice Geral de Preços ao Consumidor Amplo (IGPM)
    IGPM = 189
    # IGPDI (int): Índice Geral de Preços - Disponibilidade Interna (IGP-DI)
    IGPDI = 190
    # IPC-FGV (int): Índice de Preços ao Consumidor - Fundação Getúlio Vargas (IPC-FGV)
    IPC = 191 
    # INPC (int): Índice Nacional de Preços ao Consumidor (INPC)
    INPC = 188


__all__ = ['SGS_BASE_URL', 'Indices']

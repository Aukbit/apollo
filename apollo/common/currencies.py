#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# ----------------
# Settings for currency
# ----------------
# Using Babel's currency formatting
# http://babel.pocoo.org/docs/api/numbers/#babel.numbers.format_currency
# ----------------

GBP = 1, 'GBP', '£', 'British Pound'
EUR = 2, 'EUR', '€', 'Euro'
USD = 3, 'USD', '$', 'US Dollar'

CURRENCIES_STRING_MAP = {
    GBP[1]: GBP[0],
    EUR[1]: EUR[0],
    USD[1]: USD[0]
}

CURRENCIES_CHOICES = frozenset(CURRENCIES_STRING_MAP.values())
CURRENCIES_STRING_CHOICES = frozenset(CURRENCIES_STRING_MAP.keys())
CURRENCIES_MAP = dict(zip(CURRENCIES_STRING_MAP.values(), CURRENCIES_STRING_MAP.keys()))

CURRENCIES_SYMBOL_MAP = {
    GBP[2]: GBP[0],
    EUR[2]: EUR[0],
    USD[2]: USD[0]
}

# Defaults
DEFAULT_CURRENCY = GBP

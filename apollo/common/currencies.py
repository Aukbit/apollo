# ================
# Settings for currency
# ================
# Using Babel's currency formatting
# http://babel.pocoo.org/docs/api/numbers/#babel.numbers.format_currency
# ================



GBP = 'GBP'
EUR = 'EUR'
USD = 'USD'
CURRENCY_CHOICES = (
    (GBP, 'British Pounds'),
    (EUR, 'Euros'),
    (USD, 'US Dollar'),
)
CURRENCY_CHOICES_LIST = [GBP, EUR, USD]

DEFAULT_CURRENCY = GBP
DEFAULT_CURRENCY_FORMAT = None
DEFAULT_CURRENCY_LOCALE = 'en_GB'

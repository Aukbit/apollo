
TRANSFER_PENDING = 10, 'pending'
TRANSFER_IN_TRANSIT = 20, 'in_transit'
TRANSFER_PAID = 30, 'transferred'
TRANSFER_CANCELLED = 50, 'cancelled'
TRANSFER_FAILED = 60, 'failed'


TRANSFER_STATUS_STRING_MAP = {
    TRANSFER_PENDING[1]: TRANSFER_PENDING[0],
    TRANSFER_PAID[1]: TRANSFER_PAID[0],
    TRANSFER_CANCELLED[1]: TRANSFER_CANCELLED[0],
    TRANSFER_FAILED[1]: TRANSFER_FAILED[0]
}

TRANSFER_STATUS_CHOICES = frozenset(TRANSFER_STATUS_STRING_MAP.values())
TRANSFER_STATUS_STRING_CHOICES = frozenset(TRANSFER_STATUS_STRING_MAP.keys())
TRANSFER_STATUS_MAP = dict(zip(TRANSFER_STATUS_STRING_MAP.values(), TRANSFER_STATUS_STRING_MAP.keys()))

# **************
# TRANSITIONS
# **************

"""
TT_PAID
Transfer paid
"""
TT_PAID = {
    'trigger': 'go_transfer',
    'source': [TRANSFER_PENDING[1]],
    'dest': TRANSFER_PAID[1],
    'prepare': ['create_debit_account_transaction', 'create_credit_account_transaction'],
    'conditions': ['has_succeeded'],
    'before': [],
    'after': []
}

"""
TT_REQUEST_FAILURE
Transfer failed
"""
TT_FAILURE = {
    'trigger': 'go_transfer',
    'source': TRANSFER_PENDING[1],
    'dest': TRANSFER_FAILED[1],
    'conditions': [],
    'unless': ['has_succeeded'],
    'before': [],
    'after': []
}


TRANSFER_STATE_TRANSITIONS = [TT_PAID,
                              TT_FAILURE]

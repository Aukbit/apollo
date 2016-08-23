
TRANSACTION_PENDING = 1, 'pending'
TRANSACTION_AVAILABLE = 2, 'available'


TRANSACTION_STATUS_STRING_MAP = {
    TRANSACTION_PENDING[1]: TRANSACTION_PENDING[0],
    TRANSACTION_AVAILABLE[1]: TRANSACTION_AVAILABLE[0]
}

TRANSACTION_STATUS_CHOICES = frozenset(TRANSACTION_STATUS_STRING_MAP.values())
TRANSACTION_STATUS_STRING_CHOICES = frozenset(TRANSACTION_STATUS_STRING_MAP.keys())
TRANSACTION_STATUS_MAP = dict(zip(TRANSACTION_STATUS_STRING_MAP.values(), TRANSACTION_STATUS_STRING_MAP.keys()))

# --------------
# Transitions
# --------------

"""
TT_AVAILABLE
Transaction available
"""
TT_AVAILABLE = {
    'trigger': 'go_available',
    'source': [TRANSACTION_PENDING[1]],
    'dest': TRANSACTION_AVAILABLE[1],
    'prepare': ['execute_operation'],
    'conditions': ['has_operation_succeed'],
    'before': [],
    'after': []
}

TRANSACTION_STATE_TRANSITIONS = [TT_AVAILABLE]

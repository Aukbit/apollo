TRANSFER_CREATED = 10, 'created'
TRANSFER_PENDING = 20, 'pending'
TRANSFER_SUCCEED = 50, 'succeed'
TRANSFER_CANCELLED = 80, 'cancelled'
TRANSFER_FAILED = 90, 'failed'


TRANSFER_STATUS_STRING_MAP = {
    TRANSFER_CREATED[1]: TRANSFER_CREATED[0],
    TRANSFER_PENDING[1]: TRANSFER_PENDING[0],
    TRANSFER_SUCCEED[1]: TRANSFER_SUCCEED[0],
    TRANSFER_CANCELLED[1]: TRANSFER_CANCELLED[0],
    TRANSFER_FAILED[1]: TRANSFER_FAILED[0]
}

TRANSFER_STATUS_CHOICES = frozenset(TRANSFER_STATUS_STRING_MAP.values())
TRANSFER_STATUS_STRING_CHOICES = frozenset(TRANSFER_STATUS_STRING_MAP.keys())
TRANSFER_STATUS_MAP = dict(zip(TRANSFER_STATUS_STRING_MAP.values(), TRANSFER_STATUS_STRING_MAP.keys()))

# --------------
# Transitions
# --------------

"""
TT_PREPARE
Transfer prepare transactions
"""
TT_PREPARE = {
    'trigger': 'go_prepare',
    'source': [TRANSFER_CREATED[1]],
    'dest': TRANSFER_PENDING[1],
    'prepare': ['create_debit_account_transaction',
                'create_credit_account_transaction'],
    'conditions': [],
    'unless': [],
    'before': [],
    'after': []
}

"""
TT_EXECUTE_SUCCEED
Transfer failed
"""
TT_EXECUTE_SUCCEED = {
    'trigger': 'go_execute',
    'source': [TRANSFER_PENDING[1]],
    'dest': TRANSFER_SUCCEED[1],
    'prepare': ['execute_operation'],
    'conditions': ['has_transactions_succeed'],
    'unless': [],
    'before': [],
    'after': []
}

"""
TT_EXECUTE_FAILURE
Transfer failed
"""
TT_EXECUTE_FAILURE = {
    'trigger': 'go_execute',
    'source': TRANSFER_PENDING[1],
    'dest': TRANSFER_FAILED[1],
    'prepare': [],
    'conditions': ['has_failure_code'],
    'unless': ['has_transactions_succeed'],
    'before': [],
    'after': []
}

"""
TT_CANCEL
Transfer cancelled
"""
TT_CANCEL = {
    'trigger': 'go_cancel',
    'source': [TRANSFER_PENDING[1]],
    'dest': TRANSFER_CANCELLED[1],
    'conditions': [],
    'unless': [],
    'before': [],
    'after': []
}

TRANSFER_STATE_TRANSITIONS = [TT_PREPARE,
                              TT_EXECUTE_SUCCEED,
                              TT_EXECUTE_FAILURE,
                              TT_CANCEL]



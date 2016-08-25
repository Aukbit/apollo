TRANSFER_CREATED = 10, 'created'
TRANSFER_SEALED = 20, 'sealed'
TRANSFER_SUCCEED = 50, 'succeed'
TRANSFER_CANCELLED = 80, 'cancelled'
TRANSFER_FAILED = 90, 'failed'


TRANSFER_STATUS_STRING_MAP = {
    TRANSFER_CREATED[1]: TRANSFER_CREATED[0],
    TRANSFER_SEALED[1]: TRANSFER_SEALED[0],
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
TT_SIGN_AND_SEAL
Transfer prepare transactions
"""
TT_PREPARE = {
    'trigger': 'go_sign_and_seal',
    'source': [TRANSFER_CREATED[1]],
    'dest': TRANSFER_SEALED[1],
    'prepare': ['set_account_signature', 'set_destination_signature'],
    'conditions': ['has_valid_account_signature', 'has_valid_destination_signature'],
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
    'source': [TRANSFER_SEALED[1]],
    'dest': TRANSFER_SUCCEED[1],
    'prepare': ['execute_operation'],
    'conditions': ['has_transaction_account_succeed', 'has_transaction_destination_succeed'],
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
    'source': TRANSFER_SEALED[1],
    'dest': TRANSFER_FAILED[1],
    'prepare': [],
    'conditions': ['has_failure_code'],
    'unless': ['has_transaction_account_succeed', 'has_transaction_destination_succeed'],
    'before': [],
    'after': []
}

"""
TT_CANCEL
Transfer cancelled
"""
TT_CANCEL = {
    'trigger': 'go_cancel',
    'source': [TRANSFER_CREATED[1]],
    'dest': TRANSFER_CANCELLED[1],
    'prepare': ['set_user', 'set_reason', 'execute_cancel'],
    'conditions': ['has_cancel_fields'],
    'unless': [],
    'before': [],
    'after': []
}

TRANSFER_STATE_TRANSITIONS = [TT_PREPARE,
                              TT_EXECUTE_SUCCEED,
                              TT_EXECUTE_FAILURE,
                              TT_CANCEL]



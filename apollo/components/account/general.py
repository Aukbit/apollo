
TRANSACTION_CREATED = 10, 'created'
TRANSACTION_SEALED = 20, 'sealed'
TRANSACTION_SUCCEED = 50, 'succeed'
TRANSACTION_CANCELLED = 80, 'cancelled'
TRANSACTION_FAILED = 90, 'failed'

TRANSACTION_STATUS_STRING_MAP = {
    TRANSACTION_CREATED[1]: TRANSACTION_CREATED[0],
    TRANSACTION_SEALED[1]: TRANSACTION_SEALED[0],
    TRANSACTION_SUCCEED[1]: TRANSACTION_SUCCEED[0],
    TRANSACTION_CANCELLED[1]: TRANSACTION_CANCELLED[0],
    TRANSACTION_FAILED[1]: TRANSACTION_FAILED[0]
}

TRANSACTION_STATUS_CHOICES = frozenset(TRANSACTION_STATUS_STRING_MAP.values())
TRANSACTION_STATUS_STRING_CHOICES = frozenset(TRANSACTION_STATUS_STRING_MAP.keys())
TRANSACTION_STATUS_MAP = dict(zip(TRANSACTION_STATUS_STRING_MAP.values(), TRANSACTION_STATUS_STRING_MAP.keys()))

# --------------
# Transitions
# --------------

"""
TT_SIGN_AND_SEAL
Transaction sign and seal
"""
TT_SIGN_AND_SEAL = {
    'trigger': 'go_sign_and_seal',
    'source': [TRANSACTION_CREATED[1],
               TRANSACTION_FAILED[1]],
    'dest': TRANSACTION_SEALED[1],
    'prepare': [],
    'conditions': ['has_valid_signature'],
    'unless': [],
    'before': [],
    'after': []
}

"""
TT_SIGN_AND_SEAL_FAILURE
Transaction failure
"""
TT_SIGN_AND_SEAL_FAILURE = {
    'trigger': 'go_sign_and_seal',
    'source': [TRANSACTION_CREATED[1]],
    'dest': TRANSACTION_FAILED[1],
    'prepare': [],
    'conditions': ['has_failure_code'],
    'unless': ['has_valid_signature'],
    'before': [],
    'after': []
}

"""
TT_EXECUTE_SUCCEED
Transaction done and succeed
"""
TT_EXECUTE_SUCCEED = {
    'trigger': 'go_execute',
    'source': [TRANSACTION_SEALED[1]],
    'dest': TRANSACTION_SUCCEED[1],
    'prepare': ['execute_operation'],
    'conditions': ['has_operation_succeed'],
    'unless': [],
    'before': [],
    'after': []
}

"""
TT_EXECUTE
Transaction failure
"""
TT_EXECUTE_FAILURE = {
    'trigger': 'go_execute',
    'source': [TRANSACTION_SEALED[1]],
    'dest': TRANSACTION_FAILED[1],
    'prepare': [],
    'conditions': ['has_failure_code'],
    'unless': ['has_operation_succeed'],
    'before': [],
    'after': []
}

"""
TT_CANCEL
Transaction cancel
"""
TT_CANCEL = {
    'trigger': 'go_cancel',
    'source': [TRANSACTION_CREATED[1]],
    'dest': TRANSACTION_CANCELLED[1],
    'prepare': [],
    'conditions': ['has_cancel_reason'],
    'unless': [],
    'before': [],
    'after': []
}

TRANSACTION_STATE_TRANSITIONS = [TT_SIGN_AND_SEAL,
                                 TT_SIGN_AND_SEAL_FAILURE,
                                 TT_EXECUTE_SUCCEED,
                                 TT_EXECUTE_FAILURE,
                                 TT_CANCEL]

# --------------
# Failure codes
# --------------

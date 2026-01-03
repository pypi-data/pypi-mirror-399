# Default lock timeout in seconds, to avoid permanent locks
DEFAULT_LOCK_TIMEOUT = 10
SPIN_GAP = 0.01


class LockError(Exception):
    """Raised when error connecting to redis"""

    pass


class LockTimeout(Exception):
    """Raised when lock acquisition times out"""

    pass

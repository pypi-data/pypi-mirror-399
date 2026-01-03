# Default lock timeout in seconds, to avoid permanent locks
DEFAULT_LOCK_TIMEOUT = 10


class MutexOccupiedError(Exception):
    """Raised when trying to acquire a lock that is already held by another owner."""

    pass

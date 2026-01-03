from redis.asyncio import ConnectionPool
import sys
from .mutex import DMutex
import asyncio
from .consts import LockError, LockTimeout

__all__ = ["RDLockFactory", "LockError", "LockTimeout"]


class RDLockFactory:
    __redis_pool: ConnectionPool

    def __init__(self, redis_url: str):
        self.__redis_pool = ConnectionPool.from_url(
            redis_url, decode_responses=True, protocol=3
        )

    def __del__(self):
        try:
            # If there's a running event loop, use it to close the pool
            loop = asyncio.get_event_loop()
            loop.create_task(self.__redis_pool.aclose())
        except RuntimeError:
            pass

    def get_mutex(
        self, name: str, owner: str | None = None, timeout: float = sys.float_info.max
    ) -> DMutex:
        """
        Acuires a distributed mutex lock.
        It will fail if it has some error when communicating with Redis server.

        Exceptions:
            LockError: error communicating with Redis.
        """
        return DMutex(
            name,
            owner,
            timeout,
            self.__redis_pool,
        )

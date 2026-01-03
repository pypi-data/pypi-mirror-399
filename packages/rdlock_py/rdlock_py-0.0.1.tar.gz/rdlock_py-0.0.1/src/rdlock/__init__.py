from redis.asyncio import ConnectionPool
from .mutex import DMutex
import asyncio
from .consts import MutexOccupiedError

__all__ = ["RDLockFactory", "MutexOccupiedError"]


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

    def get_mutex(self, name: str, owner: str | None = None) -> DMutex:
        """
        Acuires a distributed mutex lock.
        It will fail soon if another owner has already acquired the lock, throwing a MutexOccupiedError.
        """
        return DMutex(
            name,
            owner,
            self.__redis_pool,
        )

from redis.asyncio import ConnectionPool
from redis.asyncio.client import StrictRedis
from redis import RedisError
import asyncio
import uuid
from .consts import DEFAULT_LOCK_TIMEOUT, LockError, SPIN_GAP, LockTimeout


class DMutex:
    __name: str
    __owner: str
    __timeout_s: float
    __redis_pool: ConnectionPool
    __client: StrictRedis | None
    __refresh_task: asyncio.Task | None

    def __init__(
        self,
        name: str,
        owner: str | None,
        timeout_s: float,
        pool: ConnectionPool,
    ):
        self.__name = name
        self.__owner = owner if owner is not None else uuid.uuid4().hex
        self.__timeout_s = timeout_s
        self.__redis_pool = pool
        self.__client = None
        self.__refresh_task = None

    async def __refresh_lock(self):
        try:
            while self.__client is not None:
                await self.__client.expire(self.__name, DEFAULT_LOCK_TIMEOUT)
                await asyncio.sleep(1)
        except Exception:
            pass

    async def __aenter__(self):
        """
        Acquire the mutex lock.
        """
        if self.__client is None:
            self.__client = StrictRedis(connection_pool=self.__redis_pool)

        # set the lock with expiration
        while self.__timeout_s > 0:
            results: list[int] = []

            try:
                async with self.__client.pipeline(transaction=True) as pipe:
                    pipe.setnx(self.__name, self.__owner)
                    pipe.expire(self.__name, DEFAULT_LOCK_TIMEOUT)
                    results = await pipe.execute()
            except RedisError:
                raise LockError()

            if results[0] == 0:
                await asyncio.sleep(SPIN_GAP)
                self.__timeout_s -= SPIN_GAP
                continue
            else:
                break

        if self.__timeout_s <= 0:
            raise LockTimeout()

        # setup auto-refresh task
        if self.__refresh_task is not None:
            self.__refresh_task.cancel()
            self.__refresh_task = None
        self.__refresh_task = asyncio.create_task(self.__refresh_lock())

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__client:
            # delete the key
            await self.__client.delete(self.__name)

            await self.__client.aclose()
            self.__client = None

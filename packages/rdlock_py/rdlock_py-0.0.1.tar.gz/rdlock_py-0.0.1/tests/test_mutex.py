from rdlock import RDLockFactory, MutexOccupiedError
import asyncio


def test_mutex():
    factory = RDLockFactory("redis://:13717421@localhost:30000/0")

    # Test acquiring a mutex to add
    sum = 0

    async def job():
        while True:
            try:
                async with factory.get_mutex("test_mutex"):
                    nonlocal sum
                    sum += 1
                    break
            except MutexOccupiedError:
                await asyncio.sleep(0.01)

    jobs = map(lambda _: job(), range(100))

    async def run():
        await asyncio.gather(*jobs)

    asyncio.run(run())
    assert sum == 100

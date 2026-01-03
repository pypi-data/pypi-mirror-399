from rdlock import RDLockFactory
import asyncio


def test_mutex():
    factory = RDLockFactory("redis://:13717421@localhost:30000/0")

    # Test acquiring a mutex to add
    sum = 0

    async def job():
        async with factory.get_mutex("test_mutex", "114514", 2.0):
            nonlocal sum
            sum += 1

    jobs = map(lambda _: job(), range(100))

    async def run():
        await asyncio.gather(*jobs)

    asyncio.run(run())
    assert sum == 100

# Redis based distributed lock

This is a simple distributed lock based on redis. It needs asyncio, otherwise it will not work!

You can install it simply with `pip install rdlock_py`

## Usage

1, setup a redis client factory.

2, get a mutex and manage it with the context manager.

``` python
from rdlock import RDLockFactory, MutexOccupiedError

factory = RDLockFactory("redis://:13717421@localhost:30000/0")

while True:
    try:
        async with factory.get_mutex("test_mutex"):
            # do your work here
            break
    except MutexOccupiedError:
        # spin yourself
        await asyncio.sleep(0.01)
```

## Test

Use the `uv run pytest` will automatically test all cases.
# Redis based distributed lock

This is a simple distributed lock based on redis. It needs asyncio, otherwise it will not work!

You can install it simply with `pip install rdlock_py`

## Usage

1, setup a redis client factory.

2, get a mutex and manage it with the context manager.

``` python
from rdlock import RDLockFactory, LockError, LockTimeout

factory = RDLockFactory("redis://:13717421@localhost:30000/0")

try:
    async with factory.get_mutex("test_mutex", "my_owner", 1.0):
        # do your work here
        pass
except LockTimeout:
    print("failed to get lock in several seconds...")
except LockError:
    print("Something wrong when communicating with redis")
```

## Test

Use the `uv run pytest` will automatically test all cases.
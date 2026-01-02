# betterlist

`betterlist` is a tiny library that materializes iterables like `list()`, but can cache the result.

## Primary API

```python
import betterlist

xs = betterlist[range(5)]           # -> [0, 1, 2, 3, 4]
ys = betterlist[(x*x for x in xs)]  # -> [0, 1, 4, 9, 16]

# listplus

`listplus.listp()` is `list()`-compatible, but can cache materialized results.

## Usage

```python
from listplus import listp, cached

xs = listp(cached("users:v1", (x for x in range(10))))
ys = listp(cached(("expensive", 123), some_generator()))
```
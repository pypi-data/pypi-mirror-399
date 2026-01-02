from __future__ import annotations

from .core import CacheableIterable, cached, listp
from .config import configure, configured, get_config


class _BetterListFacade:
    """
    Enables:
        import betterlist
        xs = betterlist[iterable]

    Also:
        xs = betterlist(iterable)
        betterlist.cached(...)
        betterlist.configure(...)
    """

    __slots__ = (
        "listp",
        "cached",
        "CacheableIterable",
        "configure",
        "configured",
        "get_config",
    )

    def __init__(self):
        # Attach helpers as attributes on the facade
        self.listp = listp
        self.cached = cached
        self.CacheableIterable = CacheableIterable
        self.configure = configure
        self.configured = configured
        self.get_config = get_config

    def __getitem__(self, iterable):
        return self.listp(iterable)

    def __call__(self, iterable=()):
        return self.listp(iterable)

    def __repr__(self) -> str:
        return "<betterlist.list+>"


# Replace the module object with an indexable facade instance.
import sys as _sys

_sys.modules[__name__] = _BetterListFacade()

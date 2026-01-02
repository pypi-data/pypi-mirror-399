from __future__ import annotations

from .core import CacheableIterable, cached, listp
from .config import configure, configured, get_config


class _BetterListFacade:
    """
    Enables syntax:
        import betterlist
        xs = betterlist[iterable]

    Also supports:
        xs = betterlist(iterable)   # optional convenience
    """

    __slots__ = ()

    def __getitem__(self, iterable):
        return listp(iterable)

    def __call__(self, iterable=()):
        return listp(iterable)

    def __repr__(self) -> str:
        return "<betterlist.list+>"


# Replace the module object with an indexable facade instance.
# This keeps "import betterlist; betterlist[...]" ergonomic.
import sys as _sys

_facade = _BetterListFacade()
_facade.listp = listp
_facade.cached = cached
_facade.CacheableIterable = CacheableIterable
_facade.configure = configure
_facade.configured = configured
_facade.get_config = get_config

_sys.modules[__name__] = _facade

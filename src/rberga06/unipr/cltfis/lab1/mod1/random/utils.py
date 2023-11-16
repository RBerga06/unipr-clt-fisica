#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pointer-like data type."""
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, Self, override


@dataclass(slots=True)
class Signal[*Ts]:
    """A Python signal."""
    slots: list[Callable[[*Ts], Any]] = field(default_factory=list)

    def emit(self, *args: *Ts) -> None:
        for slot in self.slots:
            slot(*args)

    def connect(self, slot: Callable[[*Ts], Any], /) -> None:
        self.slots.append(slot)


# --- Object wrappers ---

class Get[X](Protocol):
    """A Python object wrapper with a `get(...)` method."""
    def get(self, /) -> X: ...


@dataclass(slots=True)
class Mut[X](Get[X]):
    """A mutable reference/pointer to a Python object."""
    _: X

    @override
    def get(self, /) -> X:
        return self._

    def set(self, _: X, /) -> None:
        self._ = _


@dataclass(slots=True, frozen=True)
class Const[X](Get[X]):
    """A constant Python object"""
    _: X

    @override
    def get(self, /) -> X:
        return self._


@dataclass(slots=True, frozen=True)
class Dyn[X](Get[X]):
    """A dynamic (computed) Python object."""
    f: Callable[[], X]

    @override
    def get(self) -> X:
        return self.f()


@dataclass(slots=True)
class Lazy[X](Get[X]):
    """A lazy (computed & cached) Python object."""
    f: Callable[[], X]
    cache: X | None = field(default=None, init=False)

    @override
    def get(self, /) -> X:
        if self.cache is None:
            self.cache = self.f()
        return self.cache

    def reset(self, /) -> Self:
        self.cache = None
        return self


@dataclass(slots=True)
class Tr[X]:
    """A tracked, mutable reference/pointer to a Python object."""
    _: X
    old: X = field(init=False)
    changed: Signal[X, X] = field(default_factory=Signal, init=False)

    @override
    def __setattr__(self, name: str, val: Any, /) -> None:
        if name == "_" and hasattr(self, "changed"):
            self.changed.emit(self._, val)
        object.__setattr__(self, name, val)

    def get(self, /) -> X:
        return self._

    def set(self, _: X, /) -> X:
        self._ = _
        return _


t = Tr(42)
t.changed.connect(print)
t._ = 69


@dataclass(slots=True)
class Computed[X]:
    """A computed Python object."""
    fn: Callable[[], X]
    cached: X | None = field(default=None, init=False)

    def compute(self, /) -> X:
        self.cached = None
        return self.get()

    def get(self, /) -> X:
        if self.cached is None:
            self.cached = self.fn()
        return self.cached

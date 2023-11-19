#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportMissingTypeStubs=false
"""MANIM utilities."""
from dataclasses import dataclass, field
from typing import Callable, Self, override
from .utils import Const, Dyn, Get
from manim import Animation


@dataclass
class AnimUpd[X](Get[X]):
    _: Get[X]
    f_intro: Callable[[X],    Animation]
    f_morph: Callable[[X, X], Animation]
    f_outro: Callable[[X],    Animation]
    last: X | None = field(init=False, default=None)

    @classmethod
    def dyn(
        cls,
        f_intro: Callable[[X], Animation],
        f_morph: Callable[[X, X], Animation],
        f_outro: Callable[[X], Animation],
    ) -> Callable[[Callable[[], X]], Self]:
        def convert(f: Callable[[], X], /) -> Self:
            return cls(Dyn(f), f_intro, f_morph, f_outro)
        return convert

    @classmethod
    def const(
        cls,
        f_intro: Callable[[X], Animation],
        f_morph: Callable[[X, X], Animation],
        f_outro: Callable[[X], Animation],
    ) -> Callable[[Callable[[], X]], Self]:
        def convert(f: Callable[[], X], /) -> Self:
            return cls(Const(f()), f_intro, f_morph, f_outro)
        return convert

    @override
    def get(self) -> X:
        return self._.get()

    def intro(self, /) -> Animation:
        self.last = self.get()
        return self.f_intro(self.last)

    def morph(self, /) -> Animation:
        if self.last is None:
            raise ValueError("Morph without intro!")
        old, new = self.last, self.get()
        anim = self.f_morph(old, new)
        self.last = new
        return anim

    def outro(self, /) -> Animation:
        if self.last is None:
            raise ValueError("Outro without intro!")
        anim = self.f_outro(self.last)
        self.last = None
        return anim


@dataclass
class AnimMut[X](Get[X]):
    _: Get[X]
    f_intro: Callable[[X], Animation]
    f_morph: Callable[[X], Animation]
    f_outro: Callable[[X], Animation]

    @classmethod
    def dyn(
        cls,
        f_intro: Callable[[X], Animation],
        f_morph: Callable[[X], Animation],
        f_outro: Callable[[X], Animation],
    ) -> Callable[[Callable[[], X]], Self]:
        def convert(f: Callable[[], X], /) -> Self:
            return cls(Dyn(f), f_intro, f_morph, f_outro)
        return convert

    @classmethod
    def const(
        cls,
        f_intro: Callable[[X], Animation],
        f_morph: Callable[[X], Animation],
        f_outro: Callable[[X], Animation],
    ) -> Callable[[Callable[[], X]], Self]:
        def convert(f: Callable[[], X], /) -> Self:
            return cls(Const(f()), f_intro, f_morph, f_outro)
        return convert

    @override
    def get(self) -> X:
        return self._.get()

    def intro(self, /) -> Animation:
        return self.f_intro(self.get())

    def morph(self, /) -> Animation:
        return self.f_morph(self.get())

    def outro(self, /) -> Animation:
        return self.f_outro(self.get())
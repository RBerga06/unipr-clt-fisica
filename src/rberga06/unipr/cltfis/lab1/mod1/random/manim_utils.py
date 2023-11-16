#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportMissingTypeStubs=false
"""MANIM utilities."""
from dataclasses import dataclass, field
from typing import Callable, override
from .utils import Get
from manim import Animation


@dataclass
class Anim[X](Get[X]):
    _: Get[X]
    f_intro: Callable[[X],    Animation]
    f_morph: Callable[[X, X], Animation]
    f_outro: Callable[[X],    Animation]
    last: X | None = field(init=False, default=None)

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

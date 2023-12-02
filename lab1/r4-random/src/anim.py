#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportWildcardImportFromLibrary=false
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportConstantRedefinition=false
# ruff: noqa: E402
"""Mathematical ANIMations via MANIM."""
from math import ceil
import sys
from pathlib import Path
from typing import Iterable, Iterator, ClassVar, cast
from typing_extensions import override
from manim import *

SRC = Path(__file__).parent
sys.path.insert(0, str(SRC.parent.parent.parent/".venv/lib/python3.12/site-packages"))

from rberga06.phylab import BinSet, DistributionFit, DataSet, Poisson
from rberga06.phylab.manim import DEFAULT_BAR_COLORS, DiscreteDistributionFitHistogram


N_MAX: int | None = None


config.max_files_cached = 10_000


type PoissonFit = DistributionFit[Poisson, BinSet[int, DataSet[int]]]


def read(file: Path, /) -> Iterator[int]:
    return (
        int(s) for s in map(str.strip, file.read_text().splitlines())
        if s and not s.startswith("#")
    )

def cumulative[T](it: Iterable[T], /) -> Iterator[tuple[T, ...]]:
    data: tuple[T, ...] = ()
    yield data
    for x in it:
        data += x,
        yield data


class PoissonScene(Scene):
    FILE: ClassVar[Path]
    final_N: int
    final_colors: list[ManimColor]
    # --- Distribution stats ---
    fit: PoissonFit

    @property
    def N(self, /) -> int:
        return self.fit.dist.n

    @property
    def xbins(self, /) -> tuple[int, ...]:
        return tuple([int(bin.center) for bin in self.fit.data.bins])

    @property
    def bins(self, /) -> tuple[int, ...]:
        return tuple([len(bin) for bin in self.fit.data.bins])

    @property
    def nbins(self, /) -> int:
        return len(self.bins)

    @property
    def dbins(self, /) -> tuple[float, ...]:
        return tuple([self.fit.dist.pdf(x)*self.N for x in self.xbins])

    @property
    def y_range(self, /) -> tuple[int, int]:
        y = max(1, max(self.bins) + 1, int(ceil(max(self.dbins))))
        d = max(1, y // 5)
        return y, d

    # --- Mobjects ---
    hist: DiscreteDistributionFitHistogram[PoissonFit]
    hist_avg: DashedLine
    hist_dots: VGroup
    texts: VGroup

    def mkhist(self, /):
        # Histogram
        hist = DiscreteDistributionFitHistogram(
            self.fit,
            y_range=[0, *self.y_range],
            bar_colors=self.final_colors[self.xbins[0]:self.xbins[-1]+1],
        ).shift(DOWN)
        hist.add_avg_line().set_stroke(width=DEFAULT_STROKE_WIDTH*.5).set_color(RED)
        hist.add_expected_dots().set_fill(RED_E, opacity=1).set_stroke(
            BLACK, width=DEFAULT_STROKE_WIDTH*.3,
        )
        hist.add_bar_labels(font_size=30).set_stroke(
            BLACK, width=DEFAULT_STROKE_WIDTH*.7, background=True,
        )
        # Return
        return hist

    def mktexts(self, /) -> VGroup:
        return VGroup(
            MathTex(f"n = {self.N}").shift(UP*.7),
            MathTex(rf"\mu = {self.fit.dist.average :.2f}").set_color(RED),
            MathTex(rf"\sigma = {self.fit.dist.sigma:.2f}").set_color(RED).shift(DOWN*.6),
        ).to_edge(UP)

    def adding[T: Mobject](self, obj: T, /) -> T:
        self.add(obj)
        return obj

    @override
    def construct(self) -> None:
        # --- Load data & decide colors ---
        raw = [*read(self.FILE)]
        final = DataSet(raw).intbins()
        final_nbins = len(final.bins)
        self.final_N = final.n
        self.final_colors = cast(list[ManimColor], color_gradient(DEFAULT_BAR_COLORS, final_nbins))
        fits = [
            Poisson.fit(DataSet(data).bins(
                final_nbins, left=final.bins[0].left, right=final.bins[-1].right
            )) for data in cumulative(raw)
        ]
        # --- Intro animations ---
        self.fit   = fits[0]
        self.hist  = self.adding(self.mkhist())
        self.texts = self.adding(self.mktexts())
        everything = VGroup(*self.mobjects)
        self.play(Write(everything))
        # --- Transform animations ---
        for fit in fits[1:]:
            self.fit = fit
            if (N_MAX is not None) and (self.N == N_MAX + 1):
                break
            # Play animations
            self.play(
                Transform(self.hist,  self.mkhist()),
                Transform(self.texts, self.mktexts()),
                run_time=self.__run_time(self.N),
            )
        # --- Outro animations ---
        self.wait(3)
        self.play(Unwrite(everything))
        self.wait(.5)

    def __run_time(self, t: int) -> float:
        if t < 10:
            return 1.
        elif t < 20:
            return .8
        elif t < 30:
            return .6
        elif t < 40:
            return .4
        elif t < 50:
            return .2
        elif t < 100:
            return .1
        elif t < self.final_N - 50:
            return .001
        elif t < self.final_N - 10:
            return .01
        elif t < self.final_N - 5:
            return .1
        else:
            return 1


class PoissonSceneMeme(PoissonScene):
    FILE = SRC.parent/"data/p-1.txt"

class PoissonScene0(PoissonScene):
    FILE = SRC.parent/"data/p0.txt"

class PoissonScene1(PoissonScene):
    FILE = SRC.parent/"data/p1.txt"

class PoissonScene2(PoissonScene):
    FILE = SRC.parent/"data/p2.txt"

class PoissonScene3(PoissonScene):
    FILE = SRC.parent/"data/p3.txt"

class PoissonScene4(PoissonScene):
    FILE = SRC.parent/"data/p4.txt"

class PoissonScene5(PoissonScene):
    FILE = SRC.parent/"data/p5.txt"


if __name__ == "__main__":
    config.quality = "low_quality"
    PoissonScene1().render(True)

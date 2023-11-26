#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportWildcardImportFromLibrary=false
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportConstantRedefinition=false
# ruff: noqa: E402
"""Mathematical ANIMations via MANIM."""
import sys
from pathlib import Path
from typing import Iterator, ClassVar, cast
from typing_extensions import override
from manim import *

SRC = Path(__file__).parent
sys.path.insert(0, str(SRC.parent.parent.parent/".venv/lib/python3.12/site-packages"))

from rberga06.phylab.poisson import Poisson
from rberga06.phylab.manim.hist import DEFAULT_BAR_COLORS, DiscreteDistributionHistogram


N_MAX: int | None = None


config.max_files_cached = 10_000


def load_data(file: Path) -> Iterator[int]:
    return (
        int(s) for s in map(str.strip, file.read_text().splitlines())
        if s and not s.startswith("#")
    )


class PoissonScene(Scene):
    FILE: ClassVar[Path]
    final_colors: list[ManimColor]
    # --- Distribution stats ---
    P: Poisson[int]

    @property
    def N(self, /) -> int:
        return len(self.P.data)

    @property
    def xbins(self, /) -> tuple[int, ...]:
        return tuple([int(b.center) for b in self.P.bins])

    @property
    def bins(self, /) -> tuple[int, ...]:
        return tuple([len(b) for b in self.P.bins])

    @property
    def nbins(self, /) -> int:
        return len(self.bins)

    @property
    def y_range(self, /) -> tuple[int, int]:
        y = max(1, max(self.bins) + 1, self.N // 2)
        d = max(1, y // 5)
        return y, d

    # --- Mobjects ---
    hist: DiscreteDistributionHistogram[Poisson[int]]
    hist_avg: DashedLine
    hist_dots: VGroup
    texts: VGroup

    def mkhist(self, /):
        # Histogram
        hist = DiscreteDistributionHistogram(
            self.P,
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
            MathTex(f"n = {self.N}")                               .shift(  UP*.7),
            MathTex(rf"\mu = {self.P.average :.2f}").set_color(RED),
            MathTex(rf"\sigma = {self.P.sigma:.2f}").set_color(RED).shift(DOWN*.6),
        ).to_edge(UP)

    def adding[T: Mobject](self, obj: T, /) -> T:
        self.add(obj)
        return obj

    @override
    def construct(self) -> None:
        # --- Load data & decide colors ---
        P_FINAL = Poisson([*load_data(self.FILE)])
        self.final_colors = cast(list[ManimColor], color_gradient(DEFAULT_BAR_COLORS, len(P_FINAL.bins)))
        Ps = [*Poisson.mk_iter_cumulative(P_FINAL.data, custom_bins_start=P_FINAL.bins_start, custom_bins_stop=P_FINAL.bins_stop)]
        # --- Intro animations ---
        self.P     = Ps[0]
        self.hist  = self.adding(self.mkhist())
        self.texts = self.adding(self.mktexts())
        everything = VGroup(*self.mobjects)
        self.play(Write(everything))
        # --- Transform animations ---
        for P in Ps[1:]:
            self.P = P
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
        elif t < 3600:
            return .001
        elif t < 3640:
            return .05
        elif t < 3645:
            return .1
        elif t < 3650:
            return .5
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

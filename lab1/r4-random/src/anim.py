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
from typing import Iterator
from typing_extensions import override
from manim import *
from manim.typing import Point3D

SRC = Path(__file__).parent
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(SRC.parent.parent.parent/".venv/lib/python3.12/site-packages"))

from rberga06.phylab.poisson import Poisson
from rberga06.phylab.manim import DEFAULT_BAR_COLORS, hist_discrete as rb06hist


# --- Poisson ---

N_MAX: int | None = 10
FILE = SRC.parent/"data/p1.txt"


def load_data(file: Path) -> Iterator[int]:
    return (
        int(s) for s in map(str.strip, file.read_text().splitlines())
        if s and not s.startswith("#")
    )

def histpt(hist: BarChart, bin: float, y: float) -> Point3D:
    return hist.coords_to_point(bin + .5, y, 0)  # type: ignore


class PoissonScene(Scene):
    # --- Distribution stats ---
    P: Poisson[int]

    @property
    def N(self, /) -> int:
        return len(self.P.data)

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
    hist: BarChart
    hist_avg: DashedLine
    hist_dots: VGroup
    texts: VGroup

    def mkhist(self, /) -> BarChart:
        # Histogram
        hist = rb06hist(
            self.P,
            bar_names=[f"{i}" for i in range(self.nbins)],
            bar_colors=DEFAULT_BAR_COLORS[:self.nbins],
            y_range=[0, *self.y_range],
        ).shift(DOWN)
        # Average line
        self.hist_avg = DashedLine(
            histpt(hist, self.P.average, 0),
            histpt(hist, self.P.average, self.y_range[0]),
        ).set_stroke(width=DEFAULT_STROKE_WIDTH*.5).set_color(RED)
        hist.add(self.hist_avg)
        # Bar labels
        hist.bar_labels = hist.get_bar_labels(font_size=28).set_stroke(
            BLACK, width=DEFAULT_STROKE_WIDTH*.6, background=True,
        )
        hist.add(hist.bar_labels)
        # Theorical dots
        self.hist_dots = VGroup(*[
            Circle(DEFAULT_DOT_RADIUS)
                .set_fill(RED_E, opacity=1)
                .set_stroke(BLACK, width=DEFAULT_STROKE_WIDTH*.3)
                .move_to(histpt(hist, i, h))
            for i, h in enumerate(self.P.expected())
        ])
        hist.add(self.hist_dots)
        # Return
        return hist

    def mktexts(self, /) -> VGroup:
        tn = MathTex(f"n = {self.N}").to_edge(UP)
        ta = MathTex(rf"\mu = {self.P.average:.2f}").next_to(tn, DOWN).set_color(RED)
        ts = MathTex(rf"\sigma = {self.P.sigma:.2f}").next_to(ta, DOWN).set_color(RED)
        return VGroup(tn, ta, ts)

    def adding[T: Mobject](self, obj: T, /) -> T:
        self.add(obj)
        return obj

    @override
    def construct(self) -> None:
        # --- Load data (as an iterator) ---
        Pit = Poisson.mk_iter_cumulative(load_data(FILE))
        # --- Intro animations ---
        self.P = next(Pit)
        self.hist  = self.adding(self.mkhist())
        self.texts = self.adding(self.mktexts())
        everything = VGroup(*self.mobjects)
        self.play(Write(everything))
        # --- Transform animations ---
        for P in Pit:
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


if __name__ == "__main__":
    config.quality = "low_quality"
    PoissonScene().render(True)

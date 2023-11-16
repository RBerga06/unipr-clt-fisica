#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportWildcardImportFromLibrary=false
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
"""Mathematical ANIMations via MANIM."""
from itertools import count
from math import exp, factorial, sqrt
from pathlib import Path
from typing import Iterator
from typing_extensions import override
from manim import *
from manim.typing import Point3D

from .utils import Dyn
from .manim_utils import AnimMut, AnimUpd


def load_file() -> Iterator[list[float]]:
    file = Path(__file__).parent/"simulazione.txt"
    for line in file.read_text().splitlines():
        if not line:
            continue
        if line.startswith("#"):
            continue
        bins = [*map(int, line.strip().split("\t")[1:])]
        t = sum(bins)
        yield [x/t for x in bins]


class Simulation(Scene):
    @override
    def construct(self) -> None:
        chart = BarChart(
            [0.]*6,
            bar_names=[*map(str, range(6))],
            y_range=[0,.4,.1],
        )
        self.add(chart)
        self.wait(1)
        for i, bins in enumerate(load_file()):
            if i == 100:
                break
            self.play(
                chart.animate.change_bar_values(bins),
                run_time=.1,
            )


# --- Poisson ---

N_MAX: int | None = 100

COLORS = [
    BLUE_E,
    TEAL_E,
    GREEN_E,
    GOLD_E,
    YELLOW_E,
    MAROON_E,
    PURPLE_E,
]

def load_poisson(n: int) -> Iterator[int]:
    file = Path(__file__).parent/f"G17{n}.txt"
    for s in file.read_text().strip().splitlines():
        if not s:
            continue
        yield int(s)


def ppoissont(a: float) -> Iterator[float]:
    for i in count():
        yield exp(-a)*pow(a,i)/factorial(i)

def bpoissont(N: int, max: int, avg: float) -> list[float]:
    return [N*p for _, p in zip(range(max+1), ppoissont(avg))]

def mybpoissont(bins: list[int]) -> tuple[float, list[float]]:
    while bins[-1] == 0:  # exclude empty bins at the end
        bins = bins[:-1]
    s = sum(bins)
    n = len(bins)
    avg = sum(i*b for i, b in enumerate(bins))/s
    return avg, bpoissont(s, n-1, avg)


def mkhist(*bins: float) -> BarChart:
    n = max(1, max(bins) + 1, sum(bins)//2)
    d = max(1, n//5)
    return BarChart(
        [*bins],
        bar_names=[f"{i}" for i in range(len(bins))],
        y_range=[0, n, d],
        bar_colors=COLORS[:len(bins)],  # type: ignore
    ).shift(DOWN)

def histpt(hist: BarChart, bin: int, y: float) -> Point3D:
    return hist.coords_to_point(bin + .5, y, 0)  # type: ignore

def histpts(hist: BarChart, ys: list[float]) -> Iterator[Point3D]:
    for i, y in enumerate(ys):
        yield histpt(hist, i, y)

def mkdot() -> Circle:
    dot = Circle(DEFAULT_DOT_RADIUS)
    dot.set_fill(RED_E, opacity=1)
    dot.set_stroke(BLACK, width=DEFAULT_STROKE_WIDTH*.3)
    return dot


class Poisson(Scene):
    @override
    def construct(self) -> None:
        bins: list[int] = [0]
        n: int   = 0
        µ: float = 0

        # --- Histogram ---
        hist = mkhist(*bins)

        # --- Column labels ---
        labels = AnimUpd(Dyn(
            lambda: hist.get_bar_labels(font_size=26).set_stroke(
                BLACK, width=DEFAULT_STROKE_WIDTH*.5, background=True,
            )
        ), Write, ReplacementTransform, Unwrite)

        # --- Counters ---
        @AnimUpd.dyn(Write, ReplacementTransform, Unwrite)
        def text() -> VGroup:
            tn = MathTex(f"n = {n}")
            ta = MathTex(rf"\mu = {µ:.2f}").next_to(tn, DOWN).set_color(RED)
            ts = MathTex(rf"\sigma = {sqrt(µ):.2f}").next_to(ta, DOWN).set_color(RED)
            return VGroup(tn, ta, ts).to_edge(UP)

        # --- Theorical dots ---
        def _dotp(bin: int, /) -> Point3D:
            return histpt(hist, bin, dist_vals[bin])

        def mk_dot(bin: int, /) -> AnimMut[Circle]:
            @AnimMut[Circle].const(
                lambda dot: DrawBorderThenFill(dot.move_to(_dotp(bin))),  # type: ignore
                lambda dot: dot.animate.move_to(_dotp(bin)),
                FadeOut,
            )
            def dot() -> Circle:
                return mkdot()
            return dot

        dist_vals: list[float]      = [0]
        dots: list[AnimMut[Circle]] = [mk_dot(0)]

        # --- Actual animations ---
        self.play(
            DrawBorderThenFill(hist),
            text.intro(), labels.intro(),
            *[d.intro() for d in dots],
        )
        for t, x in enumerate(load_poisson(1)):
            if N_MAX is not None:
                if t == N_MAX:
                    break
            # Make new empty bins if necessary
            n = t + 1
            n_old_dots = len(bins)
            while x >= (len_ := len(bins)):
                bins.append(0)
                dots.append(mk_dot(len_))
            bins[x] += 1
            # Distribution fit
            µ, dist_vals = mybpoissont(bins)
            # Update Mobjects
            ohist, hist = hist, mkhist(*bins)
            # Create dots animations
            dots_anims: list[Animation] = []
            for i, d in enumerate(dots):
                if i < n_old_dots:
                    dots_anims.append(d.morph())
                else:
                    dots_anims.append(d.intro())
            # Play animations
            self.play(
                ReplacementTransform(ohist, hist),
                text.morph(),
                labels.morph(),
                *dots_anims,
                run_time=self.__run_time(t),
            )
        self.wait(3)
        self.play(
            text.outro(),
            labels.outro(),
            *[d.outro() for d in dots],
        )
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
    Poisson().render(True)

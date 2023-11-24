#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportWildcardImportFromLibrary=false
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# ruff: noqa: E402
"""Mathematical ANIMations via MANIM."""
import sys
from math import sqrt
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
from utils import Dyn
from manim_utils import AnimMut, AnimUpd


# --- Poisson ---

N_MAX: int | None = 10
FILE = SRC.parent/"data/p1.txt"


def load_data(file: Path) -> Iterator[int]:
    return (
        int(s) for s in map(str.strip, file.read_text().splitlines())
        if s and not s.startswith("#")
    )

def y_range(*bins: int) -> tuple[float, float]:
    ymax = max(1, max(bins) + 1, sum(bins)//2)
    dy = max(1, ymax//5)
    return ymax, dy

def mkhist(P: Poisson[int], n: float, d: float) -> BarChart:
    nbins = len(P.bins)
    return rb06hist(
        P,
        bar_names=[f"{i}" for i in range(nbins)],
        bar_colors=DEFAULT_BAR_COLORS[:nbins],
        y_range=[0, n, d],
    ).shift(DOWN)

def histpt(hist: BarChart, bin: float, y: float) -> Point3D:
    return hist.coords_to_point(bin + .5, y, 0)  # type: ignore

def histpts(hist: BarChart, ys: list[float]) -> Iterator[Point3D]:
    for i, y in enumerate(ys):
        yield histpt(hist, i, y)

def mkdot() -> Circle:
    dot = Circle(DEFAULT_DOT_RADIUS)
    dot.set_fill(RED_E, opacity=1)
    dot.set_stroke(BLACK, width=DEFAULT_STROKE_WIDTH*.3)
    return dot


class PoissonScene(Scene):
    @override
    def construct(self) -> None:
        bins: list[int] = [0]
        n: int   = 0
        µ: float = 0

        # --- Column labels ---
        labels = AnimUpd(Dyn(
            lambda: hist.get_bar_labels(font_size=28).set_stroke(
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

        # --- Average line ---
        avg_line = AnimUpd(
            Dyn(lambda:
                DashedLine(histpt(hist, µ, 0), histpt(hist, µ, ymax))
                    .set_stroke(width=DEFAULT_STROKE_WIDTH*.5)
                    .set_color(RED)
            ),
            DrawBorderThenFill,
            ReplacementTransform,
            FadeOut,
        )

        # --- Theorical dots ---
        def _dotp(bin: int, /) -> Point3D:
            return histpt(
                hist, bin,
                dist_vals[bin] if bin < len(dist_vals) else 0
            )

        def mk_dot(bin: int, /) -> AnimMut[Circle]:
            @AnimMut[Circle].const(
                lambda dot: DrawBorderThenFill(dot.move_to(_dotp(bin))),  # type: ignore
                lambda dot: dot.animate.move_to(_dotp(bin)),
                FadeOut,
            )
            def dot() -> Circle:
                return mkdot()
            return dot

        # --- Actual animations ---
        ndots = 0
        dots: list[AnimMut[Circle]] = []
        for t, P in enumerate(Poisson.mk_iter_cumulative(load_data(FILE))):
            bins = [len(b.data) for b in P.bins] or [0]
            if N_MAX is not None:
                if t == N_MAX:
                    break
            n = t
            # Make new dots if necessary
            dots += [mk_dot(i) for i in range(ndots, len(bins)+1 - ndots)]
            # Distribution fit
            µ, dist_vals = P.average, [*P.expected()]
            # Update Mobjects
            ymax, dy = y_range(*bins)
            hist_anim = ReplacementTransform(
                locals().get("hist"), (hist := mkhist(P, ymax, dy))
            )
            # Create dots animations
            dots_anims: list[Animation] = []
            for i, d in enumerate(dots):
                if i < ndots:
                    dots_anims.append(d.morph())
                else:
                    dots_anims.append(d.intro())
            # Play animations
            if t == 0:
                self.play(
                    DrawBorderThenFill(hist),
                    text.intro(),
                    *dots_anims,
                    avg_line.intro(),
                    labels.intro(),
                )
            else:
                self.play(
                    hist_anim,
                    text.morph(),
                    *dots_anims,
                    avg_line.morph(),
                    labels.morph(),
                    run_time=self.__run_time(t),
                )
            ndots = len(bins)
        self.wait(3)
        self.play(
            text.outro(),
            labels.outro(),
            avg_line.outro(),
            *[d.outro() for d in dots],
            Unwrite(hist),
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
    PoissonScene().render(True)

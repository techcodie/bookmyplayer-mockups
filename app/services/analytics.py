"""Funnel analytics — the centerpiece.

The one subtlety that makes this honest: we do NOT count an application by the
stage it's *currently* in. We count it by the *furthest* stage it ever reached,
derived from its event history. So an application that was rejected after an
interview still counts toward "reached Interview". Without this, a rejection
would silently erase the progress it represents and the funnel would lie.

These are pure functions over plain data, so they're trivial to unit-test
without a database.
"""

from dataclasses import dataclass
from datetime import datetime
from collections.abc import Iterable

from app.models import Stage

# The ordered pipeline the funnel measures. `wishlist` is pre-application and
# terminal states (rejected/ghosted) aren't stages you "reach", so they're out.
FUNNEL_ORDER: list[Stage] = [Stage.APPLIED, Stage.OA, Stage.INTERVIEW, Stage.OFFER]
_INDEX = {stage: i for i, stage in enumerate(FUNNEL_ORDER)}

# Canonical ordering for velocity output (every stage, in lifecycle order).
STAGE_ORDER: list[Stage] = [
    Stage.WISHLIST,
    Stage.APPLIED,
    Stage.OA,
    Stage.INTERVIEW,
    Stage.OFFER,
    Stage.REJECTED,
    Stage.GHOSTED,
]
# Reaching any of these *after* applying means the company actually responded;
# silence (still applied) or GHOSTED means no response.
RESPONSE_STAGES: set[Stage] = {Stage.OA, Stage.INTERVIEW, Stage.OFFER, Stage.REJECTED}
# Current stages that are "done" — used to count active applications.
TERMINAL_STAGES: set[Stage] = {Stage.OFFER, Stage.REJECTED, Stage.GHOSTED}

# A single application's ordered history: (stage entered, when), including the
# seed "created" event. This is the only shape the summary/velocity cores need.
History = list[tuple[Stage, datetime]]


def furthest_index(reached_stages: Iterable[Stage]) -> int | None:
    """Given every stage an application touched, return the furthest funnel index.

    Returns None if it never entered the funnel (e.g. still on the wishlist).
    """
    indices = [_INDEX[s] for s in reached_stages if s in _INDEX]
    return max(indices) if indices else None


@dataclass
class FunnelStep:
    stage: str
    reached: int          # how many applications got at least this far
    conversion: float | None  # reached(this) / reached(previous); None for the first step


@dataclass
class FunnelResult:
    steps: list[FunnelStep]
    biggest_dropoff: dict | None  # {"from", "to", "conversion"} of the weakest step


def compute_funnel(furthest_indices: list[int | None]) -> FunnelResult:
    """Aggregate per-application furthest indices into the funnel.

    `furthest_indices` is one entry per application (None = never applied).
    """
    n = len(FUNNEL_ORDER)
    # reached[i] = number of applications whose furthest index is >= i.
    reached = [0] * n
    for idx in furthest_indices:
        if idx is None:
            continue
        for i in range(idx + 1):
            reached[i] += 1

    steps: list[FunnelStep] = []
    for i, stage in enumerate(FUNNEL_ORDER):
        if i == 0:
            conv = None
        elif reached[i - 1] == 0:
            conv = None  # can't divide by zero — no one reached the previous stage
        else:
            conv = reached[i] / reached[i - 1]
        steps.append(FunnelStep(stage=stage.value, reached=reached[i], conversion=conv))

    # Biggest drop-off = the consecutive step with the lowest conversion rate.
    candidates = [s for s in steps if s.conversion is not None]
    biggest = None
    if candidates:
        weakest = min(candidates, key=lambda s: s.conversion)
        prev = FUNNEL_ORDER[_INDEX[Stage(weakest.stage)] - 1].value
        biggest = {"from": prev, "to": weakest.stage, "conversion": weakest.conversion}

    return FunnelResult(steps=steps, biggest_dropoff=biggest)


# --------------------------------------------------------------------------
# Summary — headline rates over the whole search.
# --------------------------------------------------------------------------
@dataclass
class SummaryResult:
    total: int                          # every (non-archived) application
    active: int                         # not yet offer/rejected/ghosted
    applied: int                        # ever reached APPLIED
    responded: int                      # got any response after applying
    offers: int                         # ever reached OFFER
    response_rate: float | None         # responded / applied
    offer_rate: float | None            # offers / applied
    avg_time_to_response_days: float | None  # mean days applied -> first response


def _applied_at(history: History) -> datetime | None:
    for stage, when in history:
        if stage == Stage.APPLIED:
            return when
    return None


def compute_summary(histories: list[History]) -> SummaryResult:
    """Aggregate ordered per-application histories into headline metrics.

    Each history is ordered oldest-first; the last entry is the current stage.
    """
    total = len(histories)
    active = applied = responded = offers = 0
    response_gaps: list[float] = []

    for history in histories:
        if not history:
            continue
        stages = {stage for stage, _ in history}
        current = history[-1][0]

        if current not in TERMINAL_STAGES:
            active += 1
        if Stage.OFFER in stages:
            offers += 1

        applied_at = _applied_at(history)
        if applied_at is None:
            continue  # never entered the funnel; not part of the rate denominators
        applied += 1

        # First response strictly after applying.
        first_response = next(
            (
                when
                for stage, when in history
                if stage in RESPONSE_STAGES and when > applied_at
            ),
            None,
        )
        if first_response is not None:
            responded += 1
            response_gaps.append((first_response - applied_at).total_seconds() / 86400)

    return SummaryResult(
        total=total,
        active=active,
        applied=applied,
        responded=responded,
        offers=offers,
        response_rate=(responded / applied) if applied else None,
        offer_rate=(offers / applied) if applied else None,
        avg_time_to_response_days=(
            sum(response_gaps) / len(response_gaps) if response_gaps else None
        ),
    )


# --------------------------------------------------------------------------
# Velocity — average time spent in each stage.
# --------------------------------------------------------------------------
@dataclass
class StageVelocity:
    stage: str
    avg_days: float
    n: int  # number of completed stays measured (a stage you left)


def compute_velocity(histories: list[History]) -> list[StageVelocity]:
    """Average days spent in each stage, measured only for stages an application
    actually *left* (consecutive events). The current/last stage is still being
    occupied, so its open-ended duration is excluded to avoid skewing the mean.
    """
    totals: dict[Stage, float] = {}
    counts: dict[Stage, int] = {}

    for history in histories:
        for (stage, start), (_, end) in zip(history, history[1:]):
            days = (end - start).total_seconds() / 86400
            totals[stage] = totals.get(stage, 0.0) + days
            counts[stage] = counts.get(stage, 0) + 1

    return [
        StageVelocity(stage=stage.value, avg_days=totals[stage] / counts[stage], n=counts[stage])
        for stage in STAGE_ORDER
        if counts.get(stage)
    ]

"""Unit tests for the three logic cores.

These are deliberately database-free: each core is a pure function, so we can
prove its behaviour with plain objects. This is the "I can defend every line"
evidence for the interview.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.models import ReminderType, Stage
from app.services import analytics, pipeline, reminders, scoring


_BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _at(day: int) -> datetime:
    return _BASE + timedelta(days=day)


# --------------------------------------------------------------------------
# State machine
# --------------------------------------------------------------------------
def test_legal_transitions_allowed():
    assert pipeline.is_allowed(Stage.WISHLIST, Stage.APPLIED)
    assert pipeline.is_allowed(Stage.APPLIED, Stage.OA)
    assert pipeline.is_allowed(Stage.APPLIED, Stage.INTERVIEW)  # OA can be skipped
    assert pipeline.is_allowed(Stage.INTERVIEW, Stage.OFFER)


def test_illegal_transitions_rejected():
    assert not pipeline.is_allowed(Stage.WISHLIST, Stage.OFFER)  # can't leap to offer
    assert not pipeline.is_allowed(Stage.OFFER, Stage.APPLIED)   # terminal stage
    assert not pipeline.is_allowed(Stage.REJECTED, Stage.INTERVIEW)
    assert not pipeline.is_allowed(Stage.OA, Stage.WISHLIST)     # no going backwards


# --------------------------------------------------------------------------
# Funnel analytics
# --------------------------------------------------------------------------
def test_furthest_index_uses_max_stage_reached():
    # Rejected after an interview still counts as having reached interview.
    touched = [Stage.APPLIED, Stage.OA, Stage.INTERVIEW, Stage.REJECTED]
    assert analytics.furthest_index(touched) == 2  # index of INTERVIEW

    assert analytics.furthest_index([Stage.WISHLIST]) is None  # never applied


def test_funnel_conversions_and_dropoff():
    # 10 applied, 6 reached OA, 6 reached interview, 1 offer.
    indices = (
        [0] * 4   # stopped at applied
        + [2] * 5  # reached interview (no OA recorded but index 2 implies >= applied)
        + [3] * 1  # reached offer
    )
    result = analytics.compute_funnel(indices)

    by_stage = {s.stage: s for s in result.steps}
    assert by_stage["applied"].reached == 10
    assert by_stage["interview"].reached == 6
    assert by_stage["offer"].reached == 1

    # applied -> oa is the weakest step here (6/10 = 0.6 vs interview->offer 1/6).
    assert result.biggest_dropoff["to"] == "offer"  # 1/6 ≈ 0.167 is the lowest


def test_funnel_handles_no_applications():
    result = analytics.compute_funnel([])
    assert all(step.reached == 0 for step in result.steps)
    assert result.biggest_dropoff is None


# --------------------------------------------------------------------------
# Priority scoring
# --------------------------------------------------------------------------
@dataclass
class FakeApp:
    current_stage: Stage
    deadline: datetime | None
    interest_level: int
    last_event_at: datetime


def test_overdue_deadline_scores_higher_than_distant():
    today = datetime(2026, 6, 3, tzinfo=timezone.utc).date()
    fresh = datetime(2026, 6, 3, tzinfo=timezone.utc)

    overdue = FakeApp(Stage.OA, datetime(2026, 6, 2, tzinfo=timezone.utc), 3, fresh)
    distant = FakeApp(Stage.OA, datetime(2026, 7, 30, tzinfo=timezone.utc), 3, fresh)

    assert scoring.priority_score(overdue, today) > scoring.priority_score(distant, today)


def test_stale_application_gets_followup_bump():
    today = datetime(2026, 6, 3, tzinfo=timezone.utc).date()
    stale_event = datetime(2026, 5, 20, tzinfo=timezone.utc)  # ~14 days idle
    fresh_event = datetime(2026, 6, 3, tzinfo=timezone.utc)

    stale = FakeApp(Stage.APPLIED, None, 3, stale_event)
    fresh = FakeApp(Stage.APPLIED, None, 3, fresh_event)

    assert scoring.priority_score(stale, today) == scoring.priority_score(fresh, today) + 4


# --------------------------------------------------------------------------
# Summary analytics
# --------------------------------------------------------------------------
# Four representative histories (oldest-first, last entry = current stage):
_HISTORIES = [
    [(Stage.APPLIED, _at(0)), (Stage.OA, _at(2))],            # responded in 2d, active
    [(Stage.APPLIED, _at(0)), (Stage.GHOSTED, _at(10))],      # no response, terminal
    [(Stage.WISHLIST, _at(0))],                               # never applied
    [(Stage.WISHLIST, _at(0)), (Stage.APPLIED, _at(1)),
     (Stage.INTERVIEW, _at(4)), (Stage.OFFER, _at(6))],       # responded in 3d, offer
]


def test_summary_rates_and_time_to_response():
    s = analytics.compute_summary(_HISTORIES)
    assert s.total == 4
    assert s.active == 2           # the OA app and the wishlist app
    assert s.applied == 3          # wishlist-only app excluded from denominators
    assert s.responded == 2        # ghosted doesn't count as a response
    assert s.offers == 1
    assert s.response_rate == 2 / 3
    assert s.offer_rate == 1 / 3
    assert s.avg_time_to_response_days == 2.5  # (2 + 3) / 2


def test_summary_handles_empty():
    s = analytics.compute_summary([])
    assert s.total == 0
    assert s.response_rate is None
    assert s.offer_rate is None
    assert s.avg_time_to_response_days is None


# --------------------------------------------------------------------------
# Velocity analytics
# --------------------------------------------------------------------------
def test_velocity_averages_only_completed_stays():
    steps = {v.stage: v for v in analytics.compute_velocity(_HISTORIES)}
    # APPLIED was left by three apps: 2d (->OA), 10d (->ghosted), 3d (->interview).
    assert steps["applied"].n == 3
    assert steps["applied"].avg_days == 5.0  # (2 + 10 + 3) / 3
    # INTERVIEW left once (app 4): 2 days.
    assert steps["interview"].avg_days == 2.0
    # OFFER is terminal/current and never left, so it isn't measured.
    assert "offer" not in steps


# --------------------------------------------------------------------------
# Reminder rules
# --------------------------------------------------------------------------
@dataclass
class FakeReminderApp:
    current_stage: Stage
    company: str
    role: str
    deadline: datetime | None
    last_event_at: datetime


def test_closing_deadline_raises_a_reminder():
    today = datetime(2026, 6, 3, tzinfo=timezone.utc).date()
    app = FakeReminderApp(
        Stage.APPLIED, "Stripe", "SWE Intern",
        datetime(2026, 6, 5, tzinfo=timezone.utc),  # 2 days out
        datetime(2026, 6, 3, tzinfo=timezone.utc),  # fresh, no follow-up
    )
    types = {r.type for r in reminders.generate_for(app, today)}
    assert types == {ReminderType.DEADLINE}


def test_stale_application_raises_follow_up():
    today = datetime(2026, 6, 3, tzinfo=timezone.utc).date()
    app = FakeReminderApp(
        Stage.APPLIED, "Figma", "PM Intern", None,
        datetime(2026, 5, 20, tzinfo=timezone.utc),  # ~14 days idle
    )
    types = {r.type for r in reminders.generate_for(app, today)}
    assert types == {ReminderType.FOLLOW_UP}


def test_interview_stage_raises_prep_reminder():
    today = datetime(2026, 6, 3, tzinfo=timezone.utc).date()
    app = FakeReminderApp(
        Stage.INTERVIEW, "Datadog", "SWE Intern", None,
        datetime(2026, 6, 3, tzinfo=timezone.utc),
    )
    types = {r.type for r in reminders.generate_for(app, today)}
    assert types == {ReminderType.INTERVIEW}


def test_terminal_and_fresh_applications_are_quiet():
    today = datetime(2026, 6, 3, tzinfo=timezone.utc).date()
    fresh = FakeReminderApp(
        Stage.APPLIED, "Notion", "SWE Intern", None,
        datetime(2026, 6, 3, tzinfo=timezone.utc),  # fresh, no deadline
    )
    closed = FakeReminderApp(
        Stage.REJECTED, "Notion", "SWE Intern",
        datetime(2026, 6, 4, tzinfo=timezone.utc),
        datetime(2026, 5, 1, tzinfo=timezone.utc),
    )
    assert reminders.generate_for(fresh, today) == []
    assert reminders.generate_for(closed, today) == []

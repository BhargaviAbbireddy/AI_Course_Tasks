# Implementation Plan: Meeting Reminder Baseline

**Spec**: `specs/001-reminder-baseline/spec.md`
**Status**: Draft — documents and verifies existing behavior; no new scope
**Note**: The feature is already implemented. This plan maps requirements to code and tests, and lists verification gaps rather than reimplementation work.

## Technical Context

- **Language/Version**: Python 3.12
- **Primary Dependencies**: none — standard library only (`dataclasses`, `datetime`, `enum`, `typing`, `unittest`)
- **Storage**: in-memory; `ReminderService._sent_booking_ids` is a per-instance `set[str]`
- **Testing**: `unittest`; `python -m unittest discover -v` from the repo root
- **Target Platform**: any Python 3.12 runtime
- **Project Type**: single importable library package (`meeting_room`) with a sibling test package
- **Performance Goals**: not a concern; one pass over the supplied bookings per call
- **Constraints**: no packaging manifest, CI, linter, or formatter; tests import from the repo root
- **Scale/Scope**: small in-process batches; single timezone; naive datetimes

## Constitution Check

Source of truth: `AGENTS.md`.

- Stdlib-only, no invented tooling — **pass**
- Invalid input raises `ValueError` — **pass** (verified in `booking.py` and `reminder.py`)
- Cancelled bookings never reminded — **pass**
- At most one reminder per booking per service instance — **pass**
- Tests accompany features and run before finishing — **pass** (14 tests currently green)
- No source changes required by this plan — **pass**

No violations; complexity tracking is not needed.

## Project Structure

### Documentation

```text
specs/001-reminder-baseline/
├── spec.md   # approved baseline specification
├── plan.md   # this file
└── tasks.md  # not yet created; see Phase 2
```

### Source

```text
meeting_room/
├── __init__.py   # public exports: Booking, BookingStatus, ReminderService, REMINDER_LEAD_MINUTES
├── booking.py    # Booking, BookingStatus; validation in Booking.__post_init__
└── reminder.py   # REMINDER_LEAD_MINUTES, ReminderMessage, ReminderService
tests/
├── __init__.py
└── test_reminder.py
```

No new source modules are planned. Any future feature should extend these files and re-export from `__init__.py`.

## Phase 0 — Research & Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Runtime | Python 3.12, stdlib only | Matches repo; no manifest exists to declare dependencies |
| Time source | Caller-supplied `current_time` | Deterministic tests; no clock reads or sleeps |
| Reminder window | `[start - lead, start)` | Inclusive at lead boundary, exclusive at start (FR-007) |
| Dedupe scope | Per service instance, in memory | Current behavior; persistence explicitly out of scope |
| Delivery | Injected callback, no-op default | Keeps tests side-effect-free (FR-011) |

## Phase 1 — Design

The data model and service contract already exist; this phase records them for review.

- **Booking** (`booking.py`): validates identity fields, datetime types, ordering, and status in `__post_init__`. `cancel()` and `is_cancelled` cover FR-003/FR-004.
- **ReminderService** (`reminder.py`): `reminder_time_for`, `should_send_reminder`, `build_reminder`, `process_bookings` map to FR-005 through FR-012.
- **ReminderMessage**: frozen dataclass carrying date/time/room/body (FR-010).
- **No migrations, contracts, or schemas**: there is no persistence layer.

## Phase 2 — Verification Approach

Treat the baseline as a contract to lock down. Add tests only; do not change behavior.

1. Map each FR to at least one test in `tests/test_reminder.py` (or a new `tests/test_booking.py` if it grows).
2. Close the coverage gaps listed below.
3. Run `python -m unittest discover -v` from the repo root; expect all tests green.
4. Resolve the spec's open questions before changing any behavior.

### Requirement coverage gaps to add tests for

- `end_time == start_time` rejected (FR-002).
- Non-`datetime` `start_time`/`end_time` rejected (FR-002).
- Blank or whitespace-only `room_name` and `user_id` rejected (FR-001).
- `ReminderMessage.booking_id` and `.user_id` populated correctly (FR-010).
- Default sender is a no-op and does not raise (FR-011).
- A raising callback leaves the booking unmarked, so a later call retries (FR-009 / edge case).
- Duplicate `booking_id` values in one batch yield one message (FR-009).
- A `None` element in the input iterable raises and aborts the batch (edge case).
- Default `CONFIRMED` status when `status` is omitted (FR-003).

### Out of scope

Persistence, transports, scheduling loops, time zones, auth, logging, and any packaging or CI setup.

## Open Questions

Carried from the spec; resolve before behavior changes:

1. Should `lead_minutes` be strictly an integer? Current code rejects only `<= 0`.
2. Should a `None` booking abort the batch or be skipped?
3. Is durable dedupe across process restarts required?

## Next Step

Approve this plan, then generate `specs/001-reminder-baseline/tasks.md` with the verification tasks above.

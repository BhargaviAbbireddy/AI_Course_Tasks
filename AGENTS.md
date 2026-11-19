# Project Rules

Small, dependency-free Python 3.12 package for meeting-room bookings and reminders. There is no packaging manifest, CI, linter, formatter, or typecheck config — do not assume or invent one.

## Commands

Run from the repo root; tests import the top-level `meeting_room` package.

```powershell
python -m unittest discover -v                                   # full suite (14 tests)
python -m unittest tests.test_reminder.ReminderServiceTests.test_reminder_sent_only_once
```

- No install step and no third-party dependencies.
- `pytest` is not installed and there is no pytest config; use stdlib `unittest`.

## Layout

- `meeting_room/booking.py` — `Booking` dataclass. All validation lives in `__post_init__` and raises `ValueError`; `end_time` must be strictly after `start_time`.
- `meeting_room/reminder.py` — `ReminderService` builds and sends reminders. The send window is `[start_time - lead_minutes, start_time)`, default 10 (`REMINDER_LEAD_MINUTES`). Stateful: `_sent_booking_ids` dedupes per service instance, so reuse of one instance suppresses repeat reminders for the same booking.
- `meeting_room/__init__.py` — public API surface; re-export new public classes/constants here and update `__all__`.
- `tests/test_*.py` — `unittest.TestCase` classes; the `make_booking(...)` helper builds bookings starting 2026-11-18 15:00.

## Conventions

1. Validate inputs up front and raise `ValueError` (explicit `None` checks, not `TypeError`).
2. Cancelled bookings must never be reminded or have a reminder built; each booking is reminded at most once.
3. Sending is injected via the `send_notification` callable and defaults to a no-op, so keep notifications side-effect-free by default.
4. Add tests for new features under `tests/` and run the full suite before finishing.
5. Do not modify unrelated files; do not expose passwords or secret information.
6. Explain all changes before accepting them.
7. This directory is not a git repository — `git diff`/`git commit` will fail.

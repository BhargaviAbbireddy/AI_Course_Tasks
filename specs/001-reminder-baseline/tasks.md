# Tasks: Meeting Reminder Baseline

**Spec**: `specs/001-reminder-baseline/spec.md`
**Plan**: `specs/001-reminder-baseline/plan.md`
**Scope**: Verification-only. The feature already exists; tasks audit it and add tests. No source behavior changes are authorized by this task list.

**Legend**: `[P]` = can run in parallel with other `[P]` tasks in the same phase.

## Phase 1 — Setup

- [ ] **T001** Re-read `spec.md` and `plan.md`; confirm scope is verification-only. Covers: none (scope guard). This list changes no files; Phases 3–4 add tests only.

## Phase 2 — Implementation Audit (read-only)

- [ ] **T002** Audit `meeting_room/booking.py` `Booking.__post_init__`: non-empty identity fields, `datetime` types, strict `end_time > start_time`, status type. Covers: FR-001, FR-002, FR-003; Edge E1, E2.
- [ ] **T003** Audit `Booking.cancel()` and `Booking.is_cancelled` for in-place cancellation without deletion. Covers: FR-004; AS-4.
- [ ] **T004** Audit `ReminderService.__init__` for the 10-minute default and `lead_minutes <= 0` rejection. Covers: FR-005; AS-1.
- [ ] **T005** Audit `reminder_time_for` for `start_time - lead_minutes`. Covers: FR-006, FR-007.
- [ ] **T006** Audit `should_send_reminder`: cancellation gate, sent-booking gate, and half-open window `[reminder_time, start_time)`. Covers: FR-007, FR-008, FR-009, FR-014; AS-1, AS-2, AS-3, AS-4, AS-5; Edge E3, E7.
- [ ] **T007** Audit `build_reminder`: rejection for cancelled bookings and `YYYY-MM-DD` / `HH:MM` / room formatting. Covers: FR-008, FR-010; AS-4.
- [ ] **T008** Audit `process_bookings`: batch iteration, `None` handling, callback invocation, sent-set update, returned messages, and `ValueError` on invalid input. Covers: FR-011, FR-012, FR-013, FR-014; AS-1, AS-5, AS-6; Edge E4, E5, E6.
- [ ] **T009** Audit `meeting_room/__init__.py` exports against the public names in `plan.md` (`Booking`, `BookingStatus`, `ReminderService`, `REMINDER_LEAD_MINUTES`). Covers: none (API surface).
- [ ] **T010** Audit `meeting_room/` for system-clock reads (`datetime.now`, `datetime.today`, `datetime.utcnow`, `time.time`) to confirm all timing is caller-supplied. Covers: FR-014; SC-005.

## Phase 3 — Tests (write after this list is approved)

Run from the repo root with `python -m unittest discover -v`.

### Confirmation of existing tests

- [ ] **T011** Confirm `test_default_lead_is_ten_minutes` and `test_rejects_non_positive_lead_minutes`. Covers: FR-005.
- [ ] **T012** Confirm boundary tests: reminder time is 10 minutes before, fires at exactly 10 minutes, not at 11 minutes, not at meeting start. Covers: FR-006, FR-007; AS-1, AS-2, AS-3; Edge E7.
- [ ] **T013** Confirm cancellation tests: `should_send_reminder` is false, `process_bookings` skips, and `build_reminder` raises. Covers: FR-008; AS-4.
- [ ] **T014** Confirm the at-most-once test: a second pass sends nothing. Covers: FR-009; AS-5.
- [ ] **T015** Confirm batch isolation: one cancelled plus one confirmed yields one message for the confirmed booking. Covers: FR-012; AS-6.
- [ ] **T016** Confirm the message-content test: body and fields contain the date, time, and room name. Covers: FR-010; SC-004.
- [ ] **T017** Confirm existing booking-validation tests: missing `booking_id` and `end_time` before `start_time` both raise `ValueError`. Covers: FR-001, FR-002; Edge E1, E2.

### New tests to close coverage gaps

- [ ] **T018** Add a test that `end_time == start_time` raises `ValueError`. Covers: FR-002; Edge E1.
- [ ] **T019** Add tests that non-`datetime` `start_time` and `end_time` raise `ValueError`. Covers: FR-002.
- [ ] **T020** Add tests that blank/whitespace `room_name` and `user_id`, and whitespace-only `booking_id`, raise `ValueError`. Covers: FR-001; Edge E2.
- [ ] **T021** Add assertions that `ReminderMessage.booking_id` and `.user_id` match the booking. Covers: FR-010; AS-1.
- [ ] **T022** Add a test that a service with no `send_notification` runs `process_bookings` without raising. Covers: FR-011.
- [ ] **T023** Add a test where the callback raises, asserting the booking is not marked sent and a later call retries. Covers: FR-009; AS-5; Edge E6.
- [ ] **T024** Add a test with duplicate `booking_id` values in one batch, expecting one message. Covers: FR-009; Edge E5.
- [ ] **T025** Add a test that a `None` element in the bookings iterable raises `ValueError`. Assert the error only; do not assert rollback of earlier sends. Covers: FR-013; Edge E4.
- [ ] **T026** Add a test that omitting `status` defaults to `BookingStatus.CONFIRMED`. Covers: FR-003.
- [ ] **T027** Add a test that a non-`datetime` `current_time` raises `ValueError` (the `None` case already exists). Covers: FR-013; Edge E3.
- [ ] **T028** Add an end-to-end delivery test: with a capturing callback, `process_bookings` at 14:50 for a 15:00 booking returns exactly one message, invokes the callback once, and reports the right booking ID. Covers: FR-006, FR-007, FR-011, FR-012; AS-1; SC-001.

## Phase 4 — Polish

- [ ] **T029** Run the full suite from `D:\Bhagi taks\Cursor` with `python -m unittest discover -v`; all tests must pass. Covers: SC-001, SC-002, SC-003, SC-004, SC-005.
- [ ] **T030** Review the spec's three open questions; only update `spec.md` or `plan.md` after explicit approval, and never as part of this task list. Covers: none (scope governance).

## Dependency Order

```text
T001 -> T002..T010 (audit) -> T011..T028 (tests) -> T029 -> T030
```

`T002`–`T010` are independent `[P]` tasks. `T011`–`T028` are independent `[P]` tasks once the audit is complete; confirming existing tests does not block writing new tests. `T029` requires all of `T011`–`T028`.

## Requirement Coverage Matrix

| Requirement | Tasks |
|---|---|
| FR-001 | T002, T017, T020 |
| FR-002 | T002, T017, T018, T019 |
| FR-003 | T002, T026 |
| FR-004 | T003 |
| FR-005 | T004, T011 |
| FR-006 | T005, T012, T028 |
| FR-007 | T005, T006, T012, T028 |
| FR-008 | T006, T007, T013 |
| FR-009 | T006, T014, T023, T024 |
| FR-010 | T007, T016, T021 |
| FR-011 | T008, T022, T028 |
| FR-012 | T008, T015, T028 |
| FR-013 | T008, T025, T027 |
| FR-014 | T006, T008, T010 |

## Acceptance Criteria Coverage Matrix

| Scenario | Tasks |
|---|---|
| AS-1 Reminder at lead boundary | T004, T005, T006, T012, T021, T028 |
| AS-2 Too early | T006, T012 |
| AS-3 At meeting start | T006, T012 |
| AS-4 Cancelled meeting | T003, T006, T007, T013 |
| AS-5 At-most-once delivery | T006, T014, T023 |
| AS-6 Batch isolation | T008, T015 |
| E1 Start/end ordering | T002, T017, T018 |
| E2 Blank or invalid identity fields | T002, T017, T020 |
| E3 Invalid `current_time` | T006, T027 |
| E4 `None` booking element | T008, T025 |
| E5 Duplicate booking IDs | T008, T024 |
| E6 Raising callback | T008, T023 |
| E7 Meeting already started | T006, T012 |

## Success Criteria Mapping

| Success Criterion | Verified by |
|---|---|
| SC-001 One reminder per booking | T014, T028, T029 |
| SC-002 Cancelled bookings never reminded | T013, T029 |
| SC-003 Fire only inside the window | T012, T029 |
| SC-004 Body contains date, time, room | T016, T029 |
| SC-005 Deterministic for a fixed time | T010, T029 |

## Revision Notes

Revision 2 applies the review corrections: AS-3 and E7 mappings fixed, end-to-end delivery test added, clock-read audit added, five previously unassigned existing tests now covered, incorrect references corrected, parallel test groups enabled, and tasks renumbered sequentially.

| Previous ID | Current ID | Change |
|---|---|---|
| T001 | T001 | Coverage changed to "none" |
| T002–T008 | T002–T008 | Unchanged |
| T009 | T009 | Rescoped to API surface; FR-010 removed |
| T010 | T018 | Renumbered |
| T011 | T019 | FR-002 only; invented E2 type claim removed |
| T012 | T020 | Renumbered; whitespace `booking_id` added |
| T013 | T021 | Renumbered |
| T014 | T022 | Renumbered |
| T015 | T023 | Renumbered |
| T016 | T024 | Renumbered |
| T017 | T025 | Renumbered; no-rollback wording added |
| T018 | T026 | Renumbered |
| T019 | T027 | Renumbered |
| T020 | T012 | Renumbered; E7 added |
| T021 | T013 | Renumbered; E7 removed |
| T022 | T014 | Renumbered |
| T023 | T015 | Renumbered |
| T024 | T029 | Renumbered |
| T025 | T030 | Renumbered |
| — | T010 | New clock-read audit |
| — | T011 | New confirmation of lead-time tests |
| — | T016 | New confirmation of message-content test |
| — | T017 | New confirmation of booking-validation tests |
| — | T028 | New end-to-end delivery test |

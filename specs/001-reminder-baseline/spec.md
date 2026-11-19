# Feature Specification: Meeting Reminder Baseline

**Feature**: `meeting_room` reminder service
**Status**: Draft — reverse-engineered from existing code, not new scope
**Input**: Current behavior of `meeting_room/booking.py`, `meeting_room/reminder.py`, `tests/test_reminder.py`

## User Scenarios & Testing

### Primary user story

As a meeting-room user, I receive exactly one reminder shortly before my confirmed booking starts, containing the room, date, and start time, so I do not miss the meeting.

### Acceptance scenarios

1. **Reminder at the lead boundary**
   Given a confirmed booking starting 2026-11-18 15:00 and a lead of 10 minutes,
   When the service processes bookings at 14:50,
   Then one reminder is sent containing "2026-11-18", "15:00", and the room name.

2. **Too early**
   Given the same booking,
   When processing runs at 14:49,
   Then no reminder is sent.

3. **At meeting start**
   Given the same booking,
   When processing runs at exactly 15:00,
   Then no reminder is sent.

4. **Cancelled meeting**
   Given the booking has been cancelled,
   When processing runs at 14:50,
   Then no reminder is sent and no message is built.

5. **At-most-once delivery**
   Given a reminder was already sent for the booking,
   When processing runs again within the window,
   Then no second reminder is sent.

6. **Batch isolation**
   Given one cancelled and one confirmed booking at the same start time,
   When processing runs at 14:50,
   Then exactly one message is sent, for the confirmed booking.

### Edge cases

- `end_time` equal to `start_time` is rejected; `end_time` before `start_time` is rejected.
- Blank or whitespace-only `booking_id`, `room_name`, or `user_id` is rejected.
- `current_time` that is `None` or not a `datetime` raises `ValueError`.
- A `None` element inside the bookings iterable raises `ValueError` and aborts the batch.
- Two bookings sharing a `booking_id` are treated as the same booking for deduplication.
- If the notification callback raises, the exception propagates; that booking is **not** marked as sent.
- Reminders are skipped for meetings that already started, even if they have not ended.

## Requirements

### Functional requirements

- **FR-001**: A booking MUST require non-empty `booking_id`, `room_name`, and `user_id`.
- **FR-002**: A booking MUST require `start_time` and `end_time` to be `datetime` values, with `end_time` strictly after `start_time`.
- **FR-003**: A booking MUST carry a status of `CONFIRMED` (default) or `CANCELLED`.
- **FR-004**: Cancelling a booking MUST mark it cancelled without deleting it.
- **FR-005**: The reminder lead time MUST default to 10 minutes and MUST reject values `<= 0` at service construction.
- **FR-006**: The reminder time MUST equal `start_time - lead_minutes`.
- **FR-007**: A reminder MUST be eligible only when `reminder_time <= current_time < start_time` (inclusive at the lead boundary, exclusive at start).
- **FR-008**: Cancelled bookings MUST never be eligible and MUST never have a reminder built.
- **FR-009**: Each booking MUST receive at most one reminder per service instance.
- **FR-010**: The reminder MUST include the meeting date (`YYYY-MM-DD`), start time (`HH:MM`), room name, booking ID, and user ID.
- **FR-011**: Delivery MUST be delegated to an injected callback; when none is supplied, sending MUST be a no-op.
- **FR-012**: Batch processing MUST return the messages sent during that invocation.
- **FR-013**: Invalid or missing inputs MUST raise `ValueError`, not `TypeError`.
- **FR-014**: Eligibility and delivery MUST use a caller-supplied `current_time`, not the system clock.

### Key entities

- **Booking** — booking ID, room, user, start/end time, status.
- **BookingStatus** — `CONFIRMED`, `CANCELLED`.
- **ReminderService** — lead time, sender callback, sent-booking memory.
- **ReminderMessage** — immutable record of a sent reminder: booking ID, user, room, date, time, body.

## Success Criteria

- **SC-001**: A confirmed meeting produces exactly one reminder per service instance.
- **SC-002**: 100% of cancelled bookings produce zero reminders.
- **SC-003**: Reminders fire only within the 10-minute window before start.
- **SC-004**: Every reminder body contains the date, time, and room name.
- **SC-005**: Results are deterministic for a fixed `current_time`, with no sleeps or clock reads.

## Assumptions

- Datetimes are timezone-naive; single-timezone deployments only.
- The caller drives the service periodically; no scheduler or background loop exists.
- Sent-state is in-memory and resets when the service instance is recreated.
- Only one lead time per service instance; no per-booking overrides.

## Out of Scope

Persistence, delivery transports (email/SMS/push), calendar integration, recurrence, time zones, authentication/authorization, logging and metrics, and any web/CLI interface.

## Open Questions

1. Should `lead_minutes` be strictly an integer? Current code only rejects `<= 0`, so `2.5` is accepted despite the "positive integer" message.
2. Should a `None` booking abort the whole batch (current behavior) or be skipped?
3. Should reminders be suppressed across process restarts; i.e., is durable dedupe required?

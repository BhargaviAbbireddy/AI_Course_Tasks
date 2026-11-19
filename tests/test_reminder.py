"""Tests for the meeting-room reminder feature."""

import unittest
from datetime import datetime, timedelta

from meeting_room.booking import Booking, BookingStatus
from meeting_room.reminder import (
    REMINDER_LEAD_MINUTES,
    ReminderMessage,
    ReminderService,
)


def make_booking(
    booking_id: str = "b-1",
    start_time: datetime | None = None,
    status: BookingStatus = BookingStatus.CONFIRMED,
) -> Booking:
    start = start_time or datetime(2026, 11, 18, 15, 0, 0)
    return Booking(
        booking_id=booking_id,
        room_name="Conference A",
        user_id="user-42",
        start_time=start,
        end_time=start + timedelta(hours=1),
        status=status,
    )


class ReminderServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sent: list[ReminderMessage] = []
        self.service = ReminderService(send_notification=self.sent.append)
        self.meeting_start = datetime(2026, 11, 18, 15, 0, 0)
        self.booking = make_booking(start_time=self.meeting_start)

    def test_default_lead_is_ten_minutes(self) -> None:
        self.assertEqual(REMINDER_LEAD_MINUTES, 10)
        self.assertEqual(self.service.lead_minutes, 10)

    def test_reminder_time_is_ten_minutes_before_meeting(self) -> None:
        reminder_at = self.service.reminder_time_for(self.booking)
        self.assertEqual(reminder_at, self.meeting_start - timedelta(minutes=10))

    def test_should_send_at_exactly_ten_minutes_before(self) -> None:
        current_time = self.meeting_start - timedelta(minutes=10)
        self.assertTrue(self.service.should_send_reminder(self.booking, current_time))

    def test_should_not_send_more_than_ten_minutes_before(self) -> None:
        current_time = self.meeting_start - timedelta(minutes=11)
        self.assertFalse(self.service.should_send_reminder(self.booking, current_time))

    def test_should_not_send_after_meeting_starts(self) -> None:
        current_time = self.meeting_start
        self.assertFalse(self.service.should_send_reminder(self.booking, current_time))

    def test_should_not_send_for_cancelled_meeting(self) -> None:
        self.booking.cancel()
        current_time = self.meeting_start - timedelta(minutes=10)
        self.assertFalse(self.service.should_send_reminder(self.booking, current_time))

    def test_process_bookings_skips_cancelled_meetings(self) -> None:
        cancelled = make_booking(
            booking_id="b-cancelled",
            start_time=self.meeting_start,
            status=BookingStatus.CANCELLED,
        )
        active = make_booking(
            booking_id="b-active",
            start_time=self.meeting_start,
        )
        current_time = self.meeting_start - timedelta(minutes=10)

        sent = self.service.process_bookings([cancelled, active], current_time)

        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0].booking_id, "b-active")
        self.assertEqual(len(self.sent), 1)
        self.assertEqual(self.sent[0].booking_id, "b-active")

    def test_reminder_includes_meeting_date_and_time(self) -> None:
        message = self.service.build_reminder(self.booking)

        self.assertEqual(message.meeting_date, "2026-11-18")
        self.assertEqual(message.meeting_time, "15:00")
        self.assertIn("2026-11-18", message.body)
        self.assertIn("15:00", message.body)
        self.assertIn("Conference A", message.body)

    def test_build_reminder_rejects_cancelled_meeting(self) -> None:
        self.booking.cancel()
        with self.assertRaises(ValueError):
            self.service.build_reminder(self.booking)

    def test_reminder_sent_only_once(self) -> None:
        current_time = self.meeting_start - timedelta(minutes=10)

        first = self.service.process_bookings([self.booking], current_time)
        second = self.service.process_bookings([self.booking], current_time)

        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 0)
        self.assertEqual(len(self.sent), 1)

    def test_rejects_invalid_current_time(self) -> None:
        with self.assertRaises(ValueError):
            self.service.should_send_reminder(self.booking, None)  # type: ignore[arg-type]

    def test_rejects_non_positive_lead_minutes(self) -> None:
        with self.assertRaises(ValueError):
            ReminderService(lead_minutes=0)


class BookingValidationTests(unittest.TestCase):
    def test_rejects_missing_booking_id(self) -> None:
        with self.assertRaises(ValueError):
            Booking(
                booking_id="",
                room_name="Room 1",
                user_id="u1",
                start_time=datetime(2026, 11, 18, 10, 0),
                end_time=datetime(2026, 11, 18, 11, 0),
            )

    def test_rejects_end_before_start(self) -> None:
        with self.assertRaises(ValueError):
            Booking(
                booking_id="b1",
                room_name="Room 1",
                user_id="u1",
                start_time=datetime(2026, 11, 18, 11, 0),
                end_time=datetime(2026, 11, 18, 10, 0),
            )


if __name__ == "__main__":
    unittest.main()

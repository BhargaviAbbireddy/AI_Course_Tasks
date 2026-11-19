"""Reminder service for upcoming meeting-room bookings."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Iterable, List, Optional

from .booking import Booking, BookingStatus

REMINDER_LEAD_MINUTES = 10


@dataclass(frozen=True)
class ReminderMessage:
    """A reminder notification prepared for a user."""

    booking_id: str
    user_id: str
    room_name: str
    meeting_date: str
    meeting_time: str
    body: str


class ReminderService:
    """Builds and sends reminders 10 minutes before a meeting starts."""

    def __init__(
        self,
        send_notification: Optional[Callable[[ReminderMessage], None]] = None,
        lead_minutes: int = REMINDER_LEAD_MINUTES,
    ) -> None:
        if lead_minutes <= 0:
            raise ValueError("lead_minutes must be a positive integer")
        self._lead_minutes = lead_minutes
        self._send_notification = send_notification or (lambda _message: None)
        self._sent_booking_ids: set[str] = set()

    @property
    def lead_minutes(self) -> int:
        return self._lead_minutes

    def reminder_time_for(self, booking: Booking) -> datetime:
        """Return when the reminder should be sent for a booking."""
        if booking is None:
            raise ValueError("booking is required")
        return booking.start_time - timedelta(minutes=self._lead_minutes)

    def should_send_reminder(
        self,
        booking: Booking,
        current_time: datetime,
    ) -> bool:
        """
        Return True when a reminder should be sent now.

        Rules:
        - Booking must not be cancelled.
        - Current time must be at or after the reminder window start
          (meeting start minus lead minutes) and before the meeting starts.
        - A reminder is sent only once per booking.
        """
        if booking is None:
            raise ValueError("booking is required")
        if current_time is None or not isinstance(current_time, datetime):
            raise ValueError("current_time must be a datetime")

        if booking.status == BookingStatus.CANCELLED or booking.is_cancelled:
            return False
        if booking.booking_id in self._sent_booking_ids:
            return False

        reminder_at = self.reminder_time_for(booking)
        return reminder_at <= current_time < booking.start_time

    def build_reminder(self, booking: Booking) -> ReminderMessage:
        """Create a reminder that includes the meeting date and time."""
        if booking is None:
            raise ValueError("booking is required")
        if booking.is_cancelled:
            raise ValueError("Cannot build a reminder for a cancelled meeting")

        meeting_date = booking.start_time.strftime("%Y-%m-%d")
        meeting_time = booking.start_time.strftime("%H:%M")
        body = (
            f"Reminder: your meeting in '{booking.room_name}' "
            f"starts on {meeting_date} at {meeting_time}."
        )
        return ReminderMessage(
            booking_id=booking.booking_id,
            user_id=booking.user_id,
            room_name=booking.room_name,
            meeting_date=meeting_date,
            meeting_time=meeting_time,
            body=body,
        )

    def process_bookings(
        self,
        bookings: Iterable[Booking],
        current_time: datetime,
    ) -> List[ReminderMessage]:
        """
        Send reminders for eligible bookings and return the messages sent.

        Cancelled meetings are skipped. Each booking is reminded at most once.
        """
        if bookings is None:
            raise ValueError("bookings is required")
        if current_time is None or not isinstance(current_time, datetime):
            raise ValueError("current_time must be a datetime")

        sent: List[ReminderMessage] = []
        for booking in bookings:
            if booking is None:
                raise ValueError("bookings must not contain None")
            if not self.should_send_reminder(booking, current_time):
                continue
            message = self.build_reminder(booking)
            self._send_notification(message)
            self._sent_booking_ids.add(booking.booking_id)
            sent.append(message)
        return sent

"""Meeting-room booking model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class BookingStatus(Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class Booking:
    """A meeting-room reservation."""

    booking_id: str
    room_name: str
    user_id: str
    start_time: datetime
    end_time: datetime
    status: BookingStatus = BookingStatus.CONFIRMED

    def __post_init__(self) -> None:
        if not self.booking_id or not str(self.booking_id).strip():
            raise ValueError("booking_id is required")
        if not self.room_name or not str(self.room_name).strip():
            raise ValueError("room_name is required")
        if not self.user_id or not str(self.user_id).strip():
            raise ValueError("user_id is required")
        if not isinstance(self.start_time, datetime):
            raise ValueError("start_time must be a datetime")
        if not isinstance(self.end_time, datetime):
            raise ValueError("end_time must be a datetime")
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if not isinstance(self.status, BookingStatus):
            raise ValueError("status must be a BookingStatus")

    def cancel(self) -> None:
        """Mark this booking as cancelled."""
        self.status = BookingStatus.CANCELLED

    @property
    def is_cancelled(self) -> bool:
        return self.status == BookingStatus.CANCELLED

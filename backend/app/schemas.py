from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[date] = None
    application_deadline: Optional[date] = None
    organizer: Optional[str] = None
    category: Optional[str] = None
    application_status: str = Field(default="researching", max_length=50)
    source_url: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = None
    expected_revenue: Optional[int] = None
    expected_attendance: Optional[int] = None
    is_active: bool = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[date] = None
    application_deadline: Optional[date] = None
    organizer: Optional[str] = None
    category: Optional[str] = None
    application_status: Optional[str] = Field(default=None, max_length=50)
    source_url: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = None
    expected_revenue: Optional[int] = None
    expected_attendance: Optional[int] = None
    is_active: Optional[bool] = None


class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class OrganizerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class VenueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    capacity: Optional[int] = None
    notes: Optional[str] = None

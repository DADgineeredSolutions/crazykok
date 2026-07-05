from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer


class UTCModel(BaseModel):
    """Serialize database timestamps as RFC 3339 UTC values.

    SQLite drops timezone metadata even for timezone-aware columns. Public API
    responses restore the UTC designator instead of emitting ambiguous local
    timestamps that violate their OpenAPI `date-time` format.
    """

    @field_serializer("created_at", "updated_at", check_fields=False, when_used="json")
    def serialize_timestamp(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

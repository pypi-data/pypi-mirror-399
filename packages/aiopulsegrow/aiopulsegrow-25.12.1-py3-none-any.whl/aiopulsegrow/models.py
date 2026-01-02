"""Data models for Pulsegrow API responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Device:
    """Represents a Pulsegrow device."""

    id: int
    name: str | None = None
    device_type: str | None = None
    hub_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Device:
        """Create a Device from API response data."""
        device_type = data.get("deviceType")
        return cls(
            id=data.get("id", 0),
            name=data.get("name"),
            device_type=str(device_type) if device_type is not None else None,
            hub_id=data.get("hubId"),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
        )


@dataclass
class Sensor:
    """Represents a sensor within a device."""

    id: int
    name: str | None = None
    sensor_type: str | None = None
    device_id: int | None = None
    unit: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Sensor:
        """Create a Sensor from universalSensorViews API response."""
        # Extract sensor ID from nested mostRecentDataPoint
        sensor_id = data["mostRecentDataPoint"].get("sensorId", 0)

        # Get sensor type
        sensor_type = data.get("sensorType")

        # Extract unit from dataPointValues
        unit = None
        dp_values = data.get("mostRecentDataPoint", {}).get("dataPointValues", [])
        if dp_values:
            unit = dp_values[0].get("MeasuringUnit") or None

        return cls(
            id=sensor_id,
            name=data.get("name"),
            sensor_type=str(sensor_type) if sensor_type is not None else None,
            device_id=data.get("hubId"),
            unit=unit,
        )


@dataclass
class DataPoint:
    """Represents a single data point measurement."""

    timestamp: datetime | None = None
    value: float | None = None
    device_id: int | None = None
    sensor_id: int | None = None
    unit: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataPoint:
        """Create a DataPoint from API response data."""
        return cls(
            timestamp=_parse_datetime(data.get("timestamp") or data.get("time")),
            value=data.get("value"),
            device_id=data.get("deviceId"),
            sensor_id=data.get("sensorId"),
            unit=data.get("unit"),
        )


@dataclass
class DeviceData:
    """Container for all devices and sensors."""

    devices: list[Device]
    sensors: list[Sensor]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeviceData:
        """Create DeviceData from API response."""
        return cls(
            devices=[Device.from_dict(d) for d in data.get("deviceViewDtos", [])],
            sensors=[Sensor.from_dict(s) for s in data.get("universalSensorViews", [])],
        )


@dataclass
class SensorDetails:
    """Detailed sensor information including thresholds."""

    id: int
    name: str | None = None
    sensor_type: str | None = None
    device_id: int | None = None
    unit: str | None = None
    min_threshold: float | None = None
    max_threshold: float | None = None
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorDetails:
        """Create SensorDetails from API response data."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name"),
            sensor_type=data.get("sensorType") or data.get("type"),
            device_id=data.get("deviceId"),
            unit=data.get("unit"),
            min_threshold=data.get("minThreshold"),
            max_threshold=data.get("maxThreshold"),
            enabled=data.get("enabled", True),
        )


@dataclass
class Hub:
    """Represents a Pulsegrow hub."""

    id: int
    name: str | None = None
    online: bool = False
    firmware_version: str | None = None
    ip_address: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Hub:
        """Create a Hub from API response data."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name"),
            online=data.get("online", False),
            firmware_version=data.get("firmwareVersion"),
            ip_address=data.get("ipAddress"),
        )


@dataclass
class LightReading:
    """Light spectrum reading from Pro device."""

    timestamp: datetime | None = None
    par: float | None = None
    ppfd: float | None = None
    dli: float | None = None
    spectrum: dict[str, float] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LightReading:
        """Create a LightReading from API response data."""
        return cls(
            timestamp=_parse_datetime(data.get("timestamp")),
            par=data.get("par"),
            ppfd=data.get("ppfd"),
            dli=data.get("dli"),
            spectrum=data.get("spectrum"),
        )


@dataclass
class LightReadingsResponse:
    """Response containing multiple light readings."""

    readings: list[LightReading]
    page: int = 0
    total_pages: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LightReadingsResponse:
        """Create LightReadingsResponse from API response data."""
        readings_data = data.get("readings", [])
        return cls(
            readings=[LightReading.from_dict(r) for r in readings_data],
            page=data.get("page", 0),
            total_pages=data.get("totalPages", 0),
        )


@dataclass
class TimelineEvent:
    """Represents a timeline event in the grow cycle."""

    id: int
    event_type: str | None = None
    timestamp: datetime | None = None
    description: str | None = None
    device_id: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimelineEvent:
        """Create a TimelineEvent from API response data."""
        return cls(
            id=data.get("id", 0),
            event_type=data.get("eventType") or data.get("type"),
            timestamp=_parse_datetime(data.get("timestamp")),
            description=data.get("description"),
            device_id=data.get("deviceId"),
        )


@dataclass
class TriggeredThreshold:
    """Represents a triggered threshold alert."""

    id: int
    sensor_id: int | None = None
    threshold_type: str | None = None
    threshold_value: float | None = None
    current_value: float | None = None
    triggered_at: datetime | None = None
    resolved_at: datetime | None = None
    is_active: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TriggeredThreshold:
        """Create a TriggeredThreshold from API response data."""
        return cls(
            id=data.get("id", 0),
            sensor_id=data.get("sensorId"),
            threshold_type=data.get("thresholdType") or data.get("type"),
            threshold_value=data.get("thresholdValue"),
            current_value=data.get("currentValue") or data.get("value"),
            triggered_at=_parse_datetime(data.get("triggeredAt")),
            resolved_at=_parse_datetime(data.get("resolvedAt")),
            is_active=data.get("isActive", data.get("resolvedAt") is None),
        )


@dataclass
class UserUsage:
    """User usage and quota information."""

    user_id: int
    email: str | None = None
    plan_type: str | None = None
    datapoints_used: int = 0
    datapoints_limit: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserUsage:
        """Create UserUsage from API response data."""
        return cls(
            user_id=data.get("userId", 0),
            email=data.get("email"),
            plan_type=data.get("planType") or data.get("plan"),
            datapoints_used=data.get("datapointsUsed", 0),
            datapoints_limit=data.get("datapointsLimit", 0),
        )


@dataclass
class Invitation:
    """Pending invitation information."""

    id: int
    email: str | None = None
    invited_at: datetime | None = None
    invited_by: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Invitation:
        """Create Invitation from API response data."""
        return cls(
            id=data.get("id", 0),
            email=data.get("email"),
            invited_at=_parse_datetime(data.get("invitedAt")),
            invited_by=data.get("invitedBy"),
        )


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO 8601 datetime string."""
    if not value:
        return None
    try:
        # Handle various ISO 8601 formats
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None

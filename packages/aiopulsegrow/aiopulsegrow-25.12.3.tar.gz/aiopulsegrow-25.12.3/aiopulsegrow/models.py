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
class DeviceDataPoint:
    """Represents a full device data point with all sensor readings."""

    device_id: int
    device_type: str | None = None
    created_at: datetime | None = None

    # Power and connectivity
    plugged_in: bool | None = None
    battery_v: float | None = None
    signal_strength: int | None = None

    # Environmental readings
    temperature_f: float | None = None
    temperature_c: float | None = None
    humidity_rh: float | None = None
    light_lux: float | None = None
    air_pressure: float | None = None
    vpd: float | None = None
    dp_c: float | None = None
    dp_f: float | None = None

    # Gas sensors
    co2: int | None = None
    co2_temperature: float | None = None
    co2_rh: float | None = None
    voc: int | None = None

    # Light spectrum channels
    channel1: float | None = None
    channel2: float | None = None
    channel3: float | None = None
    channel4: float | None = None
    channel5: float | None = None
    channel6: float | None = None
    channel7: float | None = None
    channel8: float | None = None

    # Additional light measurements
    near: float | None = None
    clear: float | None = None
    flicker: int | None = None
    par: float | None = None
    gain: int | None = None
    tint: float | None = None
    light_calculation_reading: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeviceDataPoint:
        """Create a DeviceDataPoint from API response data."""
        device_type = data.get("deviceType")
        return cls(
            device_id=data.get("deviceId", 0),
            device_type=str(device_type) if device_type is not None else None,
            created_at=_parse_datetime(data.get("createdAt")),
            plugged_in=data.get("pluggedIn"),
            battery_v=data.get("batteryV"),
            signal_strength=data.get("signalStrength"),
            temperature_f=data.get("temperatureF"),
            temperature_c=data.get("temperatureC"),
            humidity_rh=data.get("humidityRh"),
            light_lux=data.get("lightLux"),
            air_pressure=data.get("airPressure"),
            vpd=data.get("vpd"),
            dp_c=data.get("dpC"),
            dp_f=data.get("dpF"),
            co2=data.get("co2"),
            co2_temperature=data.get("co2Temperature"),
            co2_rh=data.get("co2Rh"),
            voc=data.get("voc"),
            channel1=data.get("channel1"),
            channel2=data.get("channel2"),
            channel3=data.get("channel3"),
            channel4=data.get("channel4"),
            channel5=data.get("channel5"),
            channel6=data.get("channel6"),
            channel7=data.get("channel7"),
            channel8=data.get("channel8"),
            near=data.get("near"),
            clear=data.get("clear"),
            flicker=data.get("flicker"),
            par=data.get("par"),
            gain=data.get("gain"),
            tint=data.get("tint"),
            light_calculation_reading=data.get("lightCalculationReading"),
        )


@dataclass
class SensorDataPointValue:
    """Represents a single parameter value from a sensor reading."""

    param_name: str | None = None
    param_value: str | None = None
    measuring_unit: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorDataPointValue:
        """Create a SensorDataPointValue from API response data."""
        return cls(
            param_name=data.get("ParamName"),
            param_value=data.get("ParamValue"),
            measuring_unit=data.get("MeasuringUnit"),
        )


@dataclass
class SensorDataPoint:
    """Represents a sensor data point (UniversalDataPointDto)."""

    sensor_id: int
    created_at: datetime | None = None
    data_point_values: list[SensorDataPointValue] | None = None

    def __post_init__(self) -> None:
        """Initialize default list if None."""
        if self.data_point_values is None:
            self.data_point_values = []

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorDataPoint:
        """Create a SensorDataPoint from API response data."""
        values = [SensorDataPointValue.from_dict(v) for v in data.get("dataPointValues", [])]
        return cls(
            sensor_id=data.get("sensorId", 0),
            created_at=_parse_datetime(data.get("createdAt")),
            data_point_values=values,
        )


@dataclass
class DataPoint:
    """Represents a single data point measurement (legacy/simple format)."""

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

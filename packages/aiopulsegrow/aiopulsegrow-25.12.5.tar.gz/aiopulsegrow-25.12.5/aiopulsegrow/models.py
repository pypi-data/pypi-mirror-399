"""Data models for Pulsegrow API responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ProLightReadingPreview:
    """Preview of professional light reading data."""

    id: int
    ppfd: float | None = None
    dli: float | None = None
    created_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProLightReadingPreview:
        """Create a ProLightReadingPreview from API response data."""
        return cls(
            id=data.get("id", 0),
            ppfd=data.get("ppfd"),
            dli=data.get("dli"),
            created_at=_parse_datetime(data.get("createdAt")),
        )


@dataclass
class Device:
    """Represents a Pulsegrow device from DeviceViewDto."""

    id: int
    name: str | None = None
    device_type: str | None = None
    grow_id: int | None = None
    guid: str | None = None
    pulse_guid: str | None = None
    display_order: int = 0
    hidden: bool = False

    # Schedule settings
    day_start: str | None = None
    night_start: str | None = None
    is_day: bool | None = None

    # VPD settings
    vpd_leaf_temp_offset_in_f: int | None = None
    vpd_target: float | None = None

    # Battery settings
    battery_count: int | None = None
    low_battery_voltage: float | None = None

    # Timezone
    grow_timezone_offset: int | None = None

    # Template
    template_id: int | None = None

    # Nested data
    most_recent_data_point: DeviceDataPoint | None = None
    pro_light_reading_preview: ProLightReadingPreview | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Device:
        """Create a Device from API response data (DeviceViewDto or DeviceDetailsDto)."""
        device_type = data.get("deviceType")

        # Parse nested mostRecentDataPoint if present
        most_recent = None
        if "mostRecentDataPoint" in data and data["mostRecentDataPoint"]:
            most_recent = DeviceDataPoint.from_dict(data["mostRecentDataPoint"])

        # Parse nested proLightReadingPreviewDto if present
        light_preview = None
        if "proLightReadingPreviewDto" in data and data["proLightReadingPreviewDto"]:
            light_preview = ProLightReadingPreview.from_dict(data["proLightReadingPreviewDto"])

        return cls(
            id=data.get("id", 0),
            name=data.get("name"),
            device_type=str(device_type) if device_type is not None else None,
            grow_id=data.get("growId"),
            guid=data.get("guid"),
            pulse_guid=data.get("pulseGuid"),
            display_order=data.get("displayOrder", 0),
            hidden=data.get("hidden", False),
            day_start=data.get("dayStart"),
            night_start=data.get("nightStart"),
            is_day=data.get("isDay"),
            vpd_leaf_temp_offset_in_f=data.get("vpdLeafTempOffsetInF"),
            vpd_target=data.get("vpdTarget"),
            battery_count=data.get("batteryCount"),
            low_battery_voltage=data.get("lowBatteryVoltage"),
            grow_timezone_offset=data.get("growTimezoneOffset"),
            template_id=data.get("templateId"),
            most_recent_data_point=most_recent,
            pro_light_reading_preview=light_preview,
        )


@dataclass
class Sensor:
    """Represents a sensor from universalSensorViews."""

    id: int
    name: str | None = None
    sensor_type: str | None = None
    device_type: str | None = None
    hub_id: int | None = None
    grow_id: int | None = None
    display_order: int = 0
    hidden: bool = False

    # Schedule settings
    day_start: str | None = None
    night_start: str | None = None

    # Sensor specific
    par_sensor_subtype: int | None = None
    template_id: int | None = None

    # Nested data
    most_recent_data_point: SensorDataPoint | None = None
    last_hour_data_point_dtos: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Sensor:
        """Create a Sensor from universalSensorViews API response."""
        # Extract sensor ID from nested mostRecentDataPoint
        sensor_id = data.get("id", 0)
        if "mostRecentDataPoint" in data and data["mostRecentDataPoint"]:
            sensor_id = data["mostRecentDataPoint"].get("sensorId", sensor_id)

        # Get sensor and device types
        sensor_type = data.get("sensorType")
        device_type = data.get("deviceType")

        # Parse nested mostRecentDataPoint if present
        most_recent = None
        if "mostRecentDataPoint" in data and data["mostRecentDataPoint"]:
            most_recent = SensorDataPoint.from_dict(data["mostRecentDataPoint"])

        return cls(
            id=sensor_id,
            name=data.get("name"),
            sensor_type=str(sensor_type) if sensor_type is not None else None,
            device_type=str(device_type) if device_type is not None else None,
            hub_id=data.get("hubId"),
            grow_id=data.get("growId"),
            display_order=data.get("displayOrder", 0),
            hidden=data.get("hidden", False),
            day_start=data.get("dayStart"),
            night_start=data.get("nightStart"),
            par_sensor_subtype=data.get("parSensorSubtype"),
            template_id=data.get("templateId"),
            most_recent_data_point=most_recent,
            last_hour_data_point_dtos=data.get("lastHourDataPointDtos"),
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
            sensor_type=data.get("sensorType"),
            device_id=data.get("deviceId"),
            unit=data.get("unit"),
            min_threshold=data.get("minThreshold"),
            max_threshold=data.get("maxThreshold"),
            enabled=data.get("enabled", True),
        )


@dataclass
class Hub:
    """Represents a Pulsegrow hub from HubDetailsDto."""

    id: int
    name: str | None = None
    grow_id: int | None = None
    mac_address: str | None = None
    hidden: bool = False
    hub_thresholds: list[dict[str, Any]] | None = None
    sensor_devices: list[dict[str, Any]] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Hub:
        """Create a Hub from API response data."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name"),
            grow_id=data.get("growId"),
            mac_address=data.get("macAddress"),
            hidden=data.get("hidden", False),
            hub_thresholds=data.get("hubThresholds"),
            sensor_devices=data.get("sensorDevices"),
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
    """Represents a timeline event from TimelineEventDto."""

    id: int
    timeline_event_type: int | None = None
    title: str | None = None
    detail: str | None = None
    display: bool = True
    grow_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimelineEvent:
        """Create a TimelineEvent from API response data."""
        return cls(
            id=data.get("id", 0),
            timeline_event_type=data.get("timelineEventType"),
            title=data.get("title"),
            detail=data.get("detail"),
            display=data.get("display", True),
            grow_id=data.get("growId"),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
        )


@dataclass
class TriggeredThreshold:
    """Represents a triggered threshold from SortedTriggeredThresholdsDto."""

    id: int
    device_id: int | None = None
    device_name: str | None = None
    low_or_high: bool | None = None
    low_threshold_value: float | None = None
    high_threshold_value: float | None = None
    triggering_value: str | None = None
    sensor_threshold_type: int | None = None
    hub_threshold_type: int | None = None
    threshold_id: int | None = None
    threshold_type: int | None = None
    resolved: bool = False
    created_at: datetime | None = None
    resolved_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TriggeredThreshold:
        """Create a TriggeredThreshold from API response data."""
        return cls(
            id=data.get("id", 0),
            device_id=data.get("deviceId"),
            device_name=data.get("deviceName"),
            low_or_high=data.get("lowOrHigh"),
            low_threshold_value=data.get("lowThresholdValue"),
            high_threshold_value=data.get("highThresholdValue"),
            triggering_value=data.get("triggeringValue"),
            sensor_threshold_type=data.get("sensorThresholdType"),
            hub_threshold_type=data.get("hubThresholdType"),
            threshold_id=data.get("thresholdId"),
            threshold_type=data.get("thresholdType"),
            resolved=data.get("resolved", False),
            created_at=_parse_datetime(data.get("createdAt")),
            resolved_at=_parse_datetime(data.get("resolvedAt")),
        )


@dataclass
class UserUsage:
    """User information from UserUsageInformation."""

    user_id: int
    user_email: str | None = None
    user_name: str | None = None
    role: str | None = None
    last_active: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserUsage:
        """Create UserUsage from API response data."""
        return cls(
            user_id=data.get("userId", 0),
            user_email=data.get("userEmail"),
            user_name=data.get("userName"),
            role=data.get("role"),
            last_active=_parse_datetime(data.get("lastActive")),
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

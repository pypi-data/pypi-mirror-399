"""Tests using real API mock data from fixtures.

NOTE: If you get import errors about 'null' not being defined, you need to
regenerate the mock_data.py file with the updated script:
    python scripts/fetch_mock_data.py YOUR_API_KEY
"""

import pytest

from aiopulsegrow.models import Device, DeviceData, Hub, Sensor

try:
    from tests.fixtures.mock_data import ALL_DEVICES, HUB_DETAILS, HUB_IDS
except (ImportError, NameError):
    pytest.skip(
        "Mock data fixtures not available or need regeneration. "
        "Run: python scripts/fetch_mock_data.py YOUR_API_KEY",
        allow_module_level=True,
    )


class TestRealFixtures:
    """Test models with real API response data."""

    def test_all_devices_parsing(self):
        """Test parsing real /all-devices response."""
        device_data = DeviceData.from_dict(ALL_DEVICES)

        # Should have parsed devices
        assert isinstance(device_data, DeviceData)
        assert len(device_data.devices) > 0
        assert len(device_data.sensors) > 0

        # Check first device
        first_device = device_data.devices[0]
        assert isinstance(first_device, Device)
        assert first_device.id == 20447
        assert first_device.name == "PulsePro"
        assert first_device.device_type == "1"  # Converted to string from API int

        # Check first sensor
        first_sensor = device_data.sensors[0]
        assert isinstance(first_sensor, Sensor)
        assert first_sensor.id == 1638  # From mostRecentDataPoint.sensorId
        assert first_sensor.sensor_type == "3"
        assert first_sensor.device_id == 402  # From hubId

    def test_hub_ids_parsing(self):
        """Test parsing real /hubs/ids response."""
        assert isinstance(HUB_IDS, list)
        assert len(HUB_IDS) > 0
        assert all(isinstance(hub_id, int) for hub_id in HUB_IDS)

    def test_hub_details_parsing(self):
        """Test parsing real /hubs/{id} response."""
        hub = Hub.from_dict(HUB_DETAILS)

        assert isinstance(hub, Hub)
        assert hub.id == 402
        assert hub.name is not None
        assert isinstance(hub.online, bool)

    def test_device_with_real_data(self):
        """Test that Device model handles real API deviceViewDto structure."""
        device_dto = ALL_DEVICES["deviceViewDtos"][0]
        device = Device.from_dict(device_dto)

        assert device.id == 20447
        assert device.name == "PulsePro"
        assert device.device_type == "1"  # Converted to string from API int

    def test_sensor_with_real_data(self):
        """Test that Sensor model handles real API universalSensorViews structure."""
        sensor_view = ALL_DEVICES["universalSensorViews"][0]
        sensor = Sensor.from_dict(sensor_view)

        assert sensor.id == 1638  # From nested mostRecentDataPoint
        assert sensor.sensor_type == "3"
        assert sensor.device_id == 402  # hubId
        # Unit is None when empty string is converted
        assert sensor.unit is None or sensor.unit == ""

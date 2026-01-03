"""Tests for data models."""

from aiopulsegrow.models import (
    Device,
    DeviceData,
)


class TestDevice:
    """Test Device model."""

    def test_from_dict(self):
        """Test creating Device from dict."""
        data = {"id": 1, "name": "Test Device", "deviceType": "pro"}
        device = Device.from_dict(data)
        assert device.id == 1
        assert device.name == "Test Device"
        assert device.device_type == "pro"


class TestDeviceData:
    """Test DeviceData model."""

    def test_from_dict(self):
        """Test creating DeviceData from dict with real API format."""
        data = {
            "deviceViewDtos": [{"id": 1, "deviceType": 1}, {"id": 2, "deviceType": 2}],
            "universalSensorViews": [
                {
                    "sensorType": 1,
                    "hubId": 100,
                    "mostRecentDataPoint": {
                        "sensorId": 10,
                        "dataPointValues": [{"MeasuringUnit": "°C"}],
                    },
                },
                {
                    "sensorType": 2,
                    "hubId": 101,
                    "mostRecentDataPoint": {
                        "sensorId": 20,
                        "dataPointValues": [{"MeasuringUnit": "%"}],
                    },
                },
            ],
        }
        device_data = DeviceData.from_dict(data)
        assert len(device_data.devices) == 2
        assert len(device_data.sensors) == 2
        assert device_data.devices[0].id == 1
        assert device_data.sensors[0].id == 10

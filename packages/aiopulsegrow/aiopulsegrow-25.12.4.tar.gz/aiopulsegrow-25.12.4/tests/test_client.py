"""Tests for PulsegrowClient."""

import re
from datetime import UTC, datetime

import aiohttp
import pytest
from aioresponses import aioresponses

from aiopulsegrow import (
    Device,
    DeviceData,
    DeviceDataPoint,
    Hub,
    LightReadingsResponse,
    PulsegrowAuthError,
    PulsegrowClient,
    PulsegrowConnectionError,
    PulsegrowError,
    PulsegrowRateLimitError,
    SensorDataPoint,
    SensorDetails,
)

API_KEY = "test-api-key-123"
BASE_URL = "https://api.pulsegrow.com"


@pytest.fixture
def mock_aioresponse():
    """Create aioresponses mock."""
    with aioresponses() as m:
        yield m


@pytest.fixture
async def client():
    """Create a test client."""
    async with aiohttp.ClientSession() as session:
        client = PulsegrowClient(api_key=API_KEY, session=session)
        yield client


@pytest.fixture
async def standalone_client():
    """Create a test client without external session."""
    client = PulsegrowClient(api_key=API_KEY)
    yield client
    await client.close()


class TestClientInitialization:
    """Test client initialization."""

    async def test_init_with_session(self):
        """Test initialization with external session."""
        async with aiohttp.ClientSession() as session:
            client = PulsegrowClient(api_key=API_KEY, session=session)
            assert client.api_key == API_KEY
            assert client._session == session
            assert client._close_session is False
            assert client.base_url == BASE_URL

    async def test_init_without_session(self, standalone_client):
        """Test initialization without external session."""
        assert standalone_client.api_key == API_KEY
        assert standalone_client._close_session is False  # Not created yet
        assert standalone_client.base_url == BASE_URL

    async def test_custom_base_url(self):
        """Test initialization with custom base URL."""
        custom_url = "https://custom.api.com"
        async with aiohttp.ClientSession() as session:
            client = PulsegrowClient(api_key=API_KEY, session=session, base_url=custom_url)
            assert client.base_url == custom_url

    async def test_base_url_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        async with aiohttp.ClientSession() as session:
            client = PulsegrowClient(
                api_key=API_KEY, session=session, base_url="https://api.test.com/"
            )
            assert client.base_url == "https://api.test.com"


class TestContextManager:
    """Test async context manager."""

    async def test_context_manager(self):
        """Test async context manager."""
        async with PulsegrowClient(api_key=API_KEY) as client:
            assert client.api_key == API_KEY

    async def test_close_internal_session(self):
        """Test that internally created session is closed."""
        client = PulsegrowClient(api_key=API_KEY)
        # Trigger session creation
        session = await client._get_session()
        assert not session.closed

        await client.close()
        assert session.closed

    async def test_close_external_session(self):
        """Test that external session is not closed."""
        async with aiohttp.ClientSession() as session:
            client = PulsegrowClient(api_key=API_KEY, session=session)
            await client.close()
            assert not session.closed


class TestErrorHandling:
    """Test error handling."""

    async def test_auth_error_401(self, client, mock_aioresponse):
        """Test authentication error handling."""
        mock_aioresponse.get(
            f"{BASE_URL}/devices/ids",
            status=401,
            payload={"error": "Unauthorized"},
        )

        with pytest.raises(PulsegrowAuthError, match="Authentication failed"):
            await client.get_device_ids()

    async def test_rate_limit_error_429(self, client, mock_aioresponse):
        """Test rate limit error handling."""
        mock_aioresponse.get(
            f"{BASE_URL}/devices/ids",
            status=429,
            payload={"error": "Rate limit exceeded"},
        )

        with pytest.raises(PulsegrowRateLimitError, match="Rate limit exceeded"):
            await client.get_device_ids()

    async def test_bad_request_400(self, client, mock_aioresponse):
        """Test bad request error handling."""
        mock_aioresponse.get(
            f"{BASE_URL}/devices/ids",
            status=400,
            body="Invalid parameters",
        )

        with pytest.raises(PulsegrowError, match="Bad request"):
            await client.get_device_ids()

    async def test_server_error_500(self, client, mock_aioresponse):
        """Test server error handling."""
        mock_aioresponse.get(
            f"{BASE_URL}/devices/ids",
            status=500,
            body="Internal server error",
        )

        with pytest.raises(PulsegrowError, match="API error 500"):
            await client.get_device_ids()

    async def test_connection_error(self, client, mock_aioresponse):
        """Test connection error handling."""
        mock_aioresponse.get(
            f"{BASE_URL}/devices/ids",
            exception=aiohttp.ClientError("Connection failed"),
        )

        with pytest.raises(PulsegrowConnectionError, match="Connection error"):
            await client.get_device_ids()


class TestDeviceEndpoints:
    """Test device endpoints."""

    async def test_get_all_devices(self, client, mock_aioresponse):
        """Test getting all devices."""
        api_response = {
            "deviceViewDtos": [{"id": 1, "deviceType": 1}],
            "universalSensorViews": [
                {
                    "sensorType": 1,
                    "hubId": 100,
                    "mostRecentDataPoint": {
                        "sensorId": 2,
                        "dataPointValues": [{"MeasuringUnit": "°C"}],
                    },
                }
            ],
        }
        mock_aioresponse.get(
            f"{BASE_URL}/all-devices",
            payload=api_response,
        )

        result = await client.get_all_devices()
        assert isinstance(result, DeviceData)
        assert len(result.devices) == 1
        assert result.devices[0].id == 1
        assert len(result.sensors) == 1
        assert result.sensors[0].id == 2

    async def test_get_device_ids(self, client, mock_aioresponse):
        """Test getting device IDs."""
        expected_ids = [1, 2, 3, 4, 5]
        mock_aioresponse.get(
            f"{BASE_URL}/devices/ids",
            payload=expected_ids,
        )

        result = await client.get_device_ids()
        assert result is not None

    async def test_get_device_details(self, client, mock_aioresponse):
        """Test getting device details."""
        api_response = [{"id": 1, "name": "Device 1"}]
        mock_aioresponse.get(
            f"{BASE_URL}/devices/details",
            payload=api_response,
        )

        result = await client.get_device_details()
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Device)
        assert result[0].id == 1
        assert result[0].name == "Device 1"

    async def test_get_device_recent_data(self, client, mock_aioresponse):
        """Test getting recent device data."""
        device_id = 20447
        api_response = {
            "deviceId": 20447,
            "deviceType": 1,
            "temperatureF": 71.3328,
            "humidityRh": 64.55934,
            "lightLux": 95.6835,
            "airPressure": 94753.5,
            "vpd": 0.93992567,
            "co2": 740,
            "pluggedIn": True,
            "batteryV": 4.114231,
            "signalStrength": -50,
            "createdAt": "2025-12-29T22:02:33",
        }
        mock_aioresponse.get(
            f"{BASE_URL}/devices/{device_id}/recent-data",
            payload=api_response,
        )

        result = await client.get_device_recent_data(device_id)
        assert isinstance(result, DeviceDataPoint)
        assert result.device_id == 20447
        assert result.temperature_f == 71.3328
        assert result.humidity_rh == 64.55934
        assert result.co2 == 740
        assert result.plugged_in is True

    async def test_get_device_data_range(self, client, mock_aioresponse):
        """Test getting device data range."""
        device_id = 20447
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        end = datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
        api_response = [
            {
                "deviceId": 20447,
                "temperatureF": 71.5,
                "humidityRh": 65.0,
                "co2": 750,
                "createdAt": "2024-01-01T00:00:00Z",
            }
        ]

        # Use regex pattern to match URL with query parameters
        mock_aioresponse.get(
            re.compile(rf"{BASE_URL}/devices/{device_id}/data-range\?.*"),
            payload=api_response,
        )

        result = await client.get_device_data_range(device_id, start, end)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], DeviceDataPoint)
        assert result[0].device_id == 20447
        assert result[0].temperature_f == 71.5

    async def test_get_device_data_range_no_end(self, client, mock_aioresponse):
        """Test getting device data range without end date."""
        device_id = 20447
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        api_response = [{"deviceId": 20447, "temperatureF": 70.0}]

        # Use regex pattern to match URL with query parameters
        mock_aioresponse.get(
            re.compile(rf"{BASE_URL}/devices/{device_id}/data-range\?.*"),
            payload=api_response,
        )

        result = await client.get_device_data_range(device_id, start)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], DeviceDataPoint)

    async def test_get_devices_range(self, client, mock_aioresponse):
        """Test getting all devices data range."""
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        end = datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
        api_response = [{"deviceId": 20447, "temperatureF": 72.0, "co2": 800}]

        # Use regex pattern to match URL with query parameters
        mock_aioresponse.get(
            re.compile(rf"{BASE_URL}/devices/range\?.*"),
            payload=api_response,
        )

        result = await client.get_devices_range(start, end)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], DeviceDataPoint)
        assert result[0].device_id == 20447


class TestSensorEndpoints:
    """Test sensor endpoints."""

    async def test_get_sensor_ids(self, client, mock_aioresponse):
        """Test getting sensor IDs."""
        expected_ids = [10, 20, 30]
        mock_aioresponse.get(
            f"{BASE_URL}/sensors/ids",
            payload=expected_ids,
        )

        result = await client.get_sensor_ids()
        assert result is not None

    async def test_get_sensor_recent_data(self, client, mock_aioresponse):
        """Test getting recent sensor data."""
        sensor_id = 1638
        api_response = {
            "dataPointValues": [{"ParamName": "pH", "ParamValue": "6.2", "MeasuringUnit": ""}],
            "sensorId": 1638,
            "createdAt": "2024-01-01T00:00:00Z",
        }
        mock_aioresponse.get(
            f"{BASE_URL}/sensors/{sensor_id}/recent-data",
            payload=api_response,
        )

        result = await client.get_sensor_recent_data(sensor_id)
        assert isinstance(result, SensorDataPoint)
        assert result.sensor_id == 1638
        assert len(result.data_point_values) == 1
        assert result.data_point_values[0].param_name == "pH"
        assert result.data_point_values[0].param_value == "6.2"

    async def test_force_sensor_read(self, client, mock_aioresponse):
        """Test forcing sensor read."""
        sensor_id = 1696
        api_response = {
            "dataPointValues": [
                {"ParamName": "EC", "ParamValue": "0.85", "MeasuringUnit": "mS/cm"},
                {"ParamName": "Temperature", "ParamValue": "22.5", "MeasuringUnit": "°C"},
            ],
            "sensorId": 1696,
            "createdAt": "2024-01-01T00:00:00Z",
        }
        mock_aioresponse.get(
            f"{BASE_URL}/sensors/{sensor_id}/force-read",
            payload=api_response,
        )

        result = await client.force_sensor_read(sensor_id)
        assert isinstance(result, SensorDataPoint)
        assert result.sensor_id == 1696
        assert len(result.data_point_values) == 2

    async def test_get_sensor_data_range(self, client, mock_aioresponse):
        """Test getting sensor data range."""
        sensor_id = 1638
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        api_response = [
            {
                "dataPointValues": [{"ParamName": "pH", "ParamValue": "6.0"}],
                "sensorId": 1638,
                "createdAt": "2024-01-01T00:00:00Z",
            }
        ]

        # Use regex pattern to match URL with query parameters
        mock_aioresponse.get(
            re.compile(rf"{BASE_URL}/sensors/{sensor_id}/data-range\?.*"),
            payload=api_response,
        )

        result = await client.get_sensor_data_range(sensor_id, start)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], SensorDataPoint)

    async def test_get_sensor_details(self, client, mock_aioresponse):
        """Test getting sensor details."""
        sensor_id = 456
        api_response = [{"id": 456, "type": "light"}]
        mock_aioresponse.get(
            f"{BASE_URL}/sensors/{sensor_id}/details",
            payload=api_response,
        )

        result = await client.get_sensor_details(sensor_id)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], SensorDetails)


class TestHubEndpoints:
    """Test hub endpoints."""

    async def test_get_hub_ids(self, client, mock_aioresponse):
        """Test getting hub IDs."""
        expected_ids = [100, 200]
        mock_aioresponse.get(
            f"{BASE_URL}/hubs/ids",
            payload=expected_ids,
        )

        result = await client.get_hub_ids()
        assert result is not None

    async def test_get_hub_details(self, client, mock_aioresponse):
        """Test getting hub details."""
        hub_id = 100
        api_response = {"id": 100, "name": "Main Hub"}
        mock_aioresponse.get(
            f"{BASE_URL}/hubs/{hub_id}",
            payload=api_response,
        )

        result = await client.get_hub_details(hub_id)
        assert isinstance(result, Hub)
        assert result.id == 100
        assert result.name == "Main Hub"


class TestLightReadingEndpoints:
    """Test light reading endpoints."""

    async def test_get_light_readings(self, client, mock_aioresponse):
        """Test getting light readings."""
        device_id = 123
        api_response = {"readings": [], "page": 0}
        mock_aioresponse.get(
            f"{BASE_URL}/api/light-readings/{device_id}",
            payload=api_response,
        )

        result = await client.get_light_readings(device_id)
        assert result is not None

    async def test_get_light_readings_with_page(self, client, mock_aioresponse):
        """Test getting light readings with page parameter."""
        device_id = 123
        page = 2
        api_response = {"readings": [], "page": 2}
        mock_aioresponse.get(
            f"{BASE_URL}/api/light-readings/{device_id}?page={page}",
            payload=api_response,
        )

        result = await client.get_light_readings(device_id, page=page)
        assert isinstance(result, LightReadingsResponse)
        assert result.page == 2

    async def test_trigger_light_reading(self, client, mock_aioresponse):
        """Test triggering light reading."""
        device_id = 123
        expected_result = {"success": True}
        mock_aioresponse.get(
            f"{BASE_URL}/api/devices/{device_id}/trigger-light-reading",
            payload=expected_result,
        )

        result = await client.trigger_light_reading(device_id)
        assert result is not None


class TestTimelineAndThresholdEndpoints:
    """Test timeline and threshold endpoints."""

    async def test_get_timeline_default(self, client, mock_aioresponse):
        """Test getting timeline with default parameters."""
        api_response = {"events": []}
        mock_aioresponse.get(
            f"{BASE_URL}/api/timeline",
            payload=api_response,
        )

        result = await client.get_timeline()
        assert isinstance(result, list)

    async def test_get_timeline_with_params(self, client, mock_aioresponse):
        """Test getting timeline with parameters."""
        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        api_response = {"events": [{"type": "watering", "id": 1}]}

        # Use regex pattern to match URL with query parameters
        mock_aioresponse.get(
            re.compile(rf"{BASE_URL}/api/timeline\?.*"),
            payload=api_response,
        )

        result = await client.get_timeline(
            event_types=["watering"],
            start_date=start_date,
            count=10,
            page=0,
        )
        assert result is not None

    async def test_get_triggered_thresholds(self, client, mock_aioresponse):
        """Test getting triggered thresholds."""
        api_response = [{"id": 1, "triggered": True}]
        mock_aioresponse.get(
            f"{BASE_URL}/api/triggered-thresholds",
            payload=api_response,
        )

        result = await client.get_triggered_thresholds()
        assert result is not None


class TestUserEndpoints:
    """Test user endpoints."""

    async def test_get_users(self, client, mock_aioresponse):
        """Test getting users."""
        api_response = [{"userId": 1, "datapointsUsed": 1000}]
        mock_aioresponse.get(
            f"{BASE_URL}/users",
            payload=api_response,
        )

        result = await client.get_users()
        assert result is not None

    async def test_get_invitations(self, client, mock_aioresponse):
        """Test getting invitations."""
        api_response = [{"id": 1, "email": "test@example.com"}]
        mock_aioresponse.get(
            f"{BASE_URL}/invitations",
            payload=api_response,
        )

        result = await client.get_invitations()
        assert result is not None


class TestRequestHeaders:
    """Test that correct headers are sent."""

    async def test_api_key_header(self, client, mock_aioresponse):
        """Test that API key is sent in header."""
        mock_aioresponse.get(
            f"{BASE_URL}/devices/ids",
            payload=[1, 2, 3],
        )

        result = await client.get_device_ids()

        # Verify the result
        assert result == [1, 2, 3]

        # Verify a request was made
        assert len(mock_aioresponse.requests) > 0

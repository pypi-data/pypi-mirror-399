# aiopulsegrow

Async Python client for the Pulsegrow API - designed for Home Assistant integrations.

## Features

- Fully async using `aiohttp`
- Type-safe with full type hints
- Comprehensive API coverage for all Pulsegrow endpoints
- Session management following Home Assistant best practices
- Extensive test coverage
- Automatic rate limit handling
- ISO 8601 datetime support

## Installation

```bash
pip install aiopulsegrow
```

## Quick Start

```python
import asyncio
from aiopulsegrow import PulsegrowClient
from aiohttp import ClientSession

async def main():
    async with ClientSession() as session:
        client = PulsegrowClient(api_key="your-api-key", session=session)

        # Get all devices
        devices = await client.get_all_devices()
        print(f"Found {len(devices.get('devices', []))} devices")

        # Get recent data for a device
        data = await client.get_device_recent_data(device_id=123)
        print(f"Temperature: {data.get('temperature')}°C")

asyncio.run(main())
```

## Usage with Home Assistant Pattern

```python
from aiopulsegrow import PulsegrowClient
from aiohttp import ClientSession

# In Home Assistant, create the session once and reuse it
session = ClientSession()
client = PulsegrowClient(api_key="your-api-key", session=session)

# Use the client throughout your integration
devices = await client.get_all_devices()

# Close when done (usually in async_unload_entry)
await client.close()
await session.close()
```

## API Methods

### Devices

- `get_all_devices()` - Get all devices with latest data
- `get_device_ids()` - List all device IDs
- `get_device_details()` - Get detailed device information
- `get_device_recent_data(device_id)` - Get last data point for a device
- `get_device_data_range(device_id, start, end=None)` - Get data within timeframe
- `get_devices_range(start, end=None)` - Get all device data (max 7 days)

### Sensors

- `get_sensor_ids()` - List all sensor IDs
- `get_sensor_recent_data(sensor_id)` - Get last data point for a sensor
- `force_sensor_read(sensor_id)` - Trigger immediate sensor reading
- `get_sensor_data_range(sensor_id, start, end=None)` - Get sensor data in range
- `get_sensor_details(sensor_id)` - Get sensor configuration

### Hubs

- `get_hub_ids()` - List all hub IDs
- `get_hub_details(hub_id)` - Get hub details

### Light Readings (Pro)

- `get_light_readings(device_id, page=None)` - Get light spectrum readings
- `trigger_light_reading(device_id)` - Trigger Pro light measurement

### Timeline & Thresholds

- `get_timeline(event_types=None, start_date=None, end_date=None, count=None, page=None)` - Get grow events
- `get_triggered_thresholds()` - Get active/resolved threshold violations

### Users

- `get_users()` - Get user usage information
- `get_invitations()` - Get pending invitations

## Authentication

All requests require an API key. Get yours from your Pulsegrow account settings.

```python
client = PulsegrowClient(api_key="your-api-key-here", session=session)
```

## Rate Limits

- Hobbyist: 4,800 datapoints/day
- Enthusiast: 24,000 datapoints/day
- Professional: 120,000 datapoints/day

## Error Handling

```python
from aiopulsegrow import PulsegrowError

try:
    data = await client.get_device_recent_data(device_id=123)
except PulsegrowError as err:
    print(f"API error: {err}")
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/aiopulsegrow.git
cd aiopulsegrow

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=aiopulsegrow --cov-report=html

# Format code
ruff format aiopulsegrow tests

# Lint and fix issues
ruff check --fix aiopulsegrow tests

# Type checking
mypy aiopulsegrow
```

### Generating Mock Data from Real API

You can fetch real data from your Pulsegrow account to generate realistic test fixtures:

```bash
python scripts/fetch_mock_data.py YOUR_API_KEY
```

This will create `tests/fixtures/mock_data.py` with real API responses that you can use in tests. See [scripts/README.md](scripts/README.md) for more details.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

# winix-api

This library provides a Python client for interacting with Winix devices. It includes classes for authenticating with the Winix API (`WinixAuth`), managing a user account (`WinixAccount`), as well as interacting with Winix devices (`WinixAPI`).

## Requirements

-   Python 3.8+
-   [warrant-lite](https://pypi.org/project/warrant-lite/), [requests](https://pypi.org/project/requests/), [PyJWT](https://pypi.org/project/PyJWT/)

## Installation

Install via pip (recommended to use a virtual environment):

```bash
pip install winix-api
```

Or clone and install locally:

```bash
git clone https://github.com/yourusername/winix-api.git
cd winix-api
pip install .
```

## Usage

### Authentication

The `WinixAuth` class is used for authenticating with the Winix API. You can use it to log in with a username and password, or to refresh an existing session.

```python
from winix_api.winix_auth import WinixAuth

# Log in with a username and password
auth = WinixAuth.login('<username>', '<password>')

# Refresh an existing session
refreshed_auth = WinixAuth.refresh('<refresh_token>', '<user_id>')
```

### Managing a User Account

The `WinixAccount` class is used for managing a user account. You can use it to get a list of devices associated with the account.

```python
from winix_api.winix_account import WinixAccount

# Create a WinixAccount from credentials
account = WinixAccount.from_credentials('<username>', '<password>')

# Create a WinixAccount from existing auth credentials
account2 = WinixAccount.from_refresh_token('<username>', '<refresh_token>', '<user_id>')

# Get a list of devices associated with the account
devices = account.devices
for device in devices:
        print(device.__dict__)
```

### Interacting with a Device

```python
from winix_api.winix_api import WinixAPI
from winix_api.winix_types import Power, Mode, Airflow, AirQuality, Plasmawave

# Assume this is defined throughout the examples
device_id = '<your_device_id>'
```

#### Get and set the Power state

```python
power = WinixAPI.get_power(account, device_id)
print('off?:', power == Power.Off)

# Set power on
WinixAPI.set_power(account, device_id, Power.On)
```

#### Get and set the Mode

```python
mode = WinixAPI.get_mode(account, device_id)
print('manual?:', mode == Mode.Manual)

# Set to auto
WinixAPI.set_mode(account, device_id, Mode.Auto)
```

#### Get and set the Airflow speed

```python
airflow = WinixAPI.get_airflow(account, device_id)
print('turbo?:', airflow == Airflow.Turbo)

# Set to low
WinixAPI.set_airflow(account, device_id, Airflow.Low)
```

#### Get the Air Quality

```python
air_quality = WinixAPI.get_air_quality(account, device_id)
print('quality:', air_quality)
```

#### Get and set the Plasmawave state

```python
plasma = WinixAPI.get_plasmawave(account, device_id)
print('plasmawave on?:', plasma == Plasmawave.On)

# Set to off
WinixAPI.set_plasmawave(account, device_id, Plasmawave.Off)
```

#### Get the Ambient Light

```python
ambient_light = WinixAPI.get_ambient_light(account, device_id)
print('ambientLight:', ambient_light)
```

#### Get the Filter Hours

```python
filter_hours = WinixAPI.get_filter_hours(account, device_id)
print('filterHours:', filter_hours)
```

### Error Handling

API errors are raised as exceptions with descriptive messages. You can also use helper functions:

```python
from winix_api.errors import is_response_error, get_error_message

if is_response_error('no data'):
        print(get_error_message('no data'))
```

## Development & Testing

-   Run tests:
    ```bash
    make test
    ```
-   View coverage:
    ```bash
    make coverage
    ```
-   Clean build/test artifacts:
    ```bash
    make clean
    ```

## License

MIT

## Disclaimer

This project is not affiliated with or endorsed by Winix. Use at your own risk.

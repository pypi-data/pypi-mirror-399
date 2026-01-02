# python-mystrom aka. pystrom

This is an unofficial Python integration for finding and controlling local MyStrom devices.

Due to the lack of owned devices, some features may not be fully implemented or tested. The project is primarily
developed and tested with the MyStrom Wi-Fi Switch CH.

> [!IMPORTANT]  
> This project is not developed by [MyStrom](https://mystrom.ch) nor affiliated with them in any way.

Official MyStrom API Documentation: [https://api.mystrom.ch/](https://api.mystrom.ch/)

Want to contribute? Check out the [Contributing](#contributing) section below.

## Installation

Installation requires [Python](https://www.python.org/downloads/)
and [Pip](https://pip.pypa.io/en/stable/installation/) (which usually comes with Python).

`python -m pip install -U pystrom`

## Features

This library provides a simple [CLI](#console-commands) and a [Python API](#python-api).

### Console Commands

| Command                         | Function                                                     |
|---------------------------------|--------------------------------------------------------------|
| `python -m pystrom find`        | Listen for MyStrom devices in the local network              |
| `python -m pystrom find --live` | Continuously listen for MyStrom devices in the local network |

### Python API

#### Get device objects

You can use the `MyStromDeviceFinder` class to find devices in your local network. It will return a list of
`MyStromDevice` objects or subclasses thereof.

```python
from pystrom.finder import MyStromDeviceFinder

with MyStromDeviceFinder() as finder:
    devices = finder.find_all()  # will take 5 seconds
    for device in devices:
        print(device)
```

You can also create a `MyStromDevice` object by using the `MyStromDeviceFactory.from_ip` method, which only requires the
IP address of the device:

```python
from pystrom.device import MyStromDeviceFactory

device = MyStromDeviceFactory.from_ip("192.168.1.220")
print(device)
```

#### Control devices

The following API methods are available for controlling devices:

##### General (`MyStromDevice`)

| Method                | Function                              |
|-----------------------|---------------------------------------|
| `.get_general_info()` | Get general device information        |
| `.get_wifi_list()`    | Get reachable Wi-Fi networks          |
| `.get_help()`         | Get a list of available API endpoints |
| `.get_settings()`     | Get current device settings           |
| `.set_settings()`     | Set or update device settings         |

##### Switch (`MyStromSwitch`)

| Method               | Function                                              |
|----------------------|-------------------------------------------------------|
| `.turn_on()`         | Turn on the switch                                    |
| `.turn_off()`        | Turn off the switch                                   |
| `.toggle()`          | Toggle the switch state and return the new state      |
| `.power_cycle()`     | Power cycle the switch (off, wait, then on)           |
| `.timer()`           | Set the state and reverse it after a specified time   |
| `.get_report()`      | Get a report of the switch's current state            |
| `.get_temperature()` | Get the current temperature reading and configuration |

##### Bulb (`MyStromBulb`)

| Method                      | Function                                                 |
|-----------------------------|----------------------------------------------------------|
| `.turn_on()`                | Turn on the bulb                                         |
| `.turn_off()`               | Turn off the bulb                                        |
| `.toggle()`                 | Toggle the bulb state                                    |
| `.set_options()`            | Set options like color, ramp, mode, and notifyurl        |
| `.get_device_information()` | Get the device information, including current bulb state |

##### Other devices and missing endpoints

Other device types are not yet implemented with specific classes, but you can still interact with them:

To control them, you can use the manual API methods of the `MyStromDevice` class, which allows you to send HTTP requests
to the device's API endpoints.

| Method        | Function                                         |
|---------------|--------------------------------------------------|
| `.api_get()`  | Send a GET request to the device's API endpoint  |
| `.api_post()` | Send a POST request to the device's API endpoint |

## Contributing

If you want to contribute to this project, feel free to open an issue or pull request. Contributions are welcome!

1. Fork the repository
2. Clone your forked repository
3. `python -m pip install -e .[dev]` to install the package in editable mode with development dependencies
4. Install mypy types: `python -m mypy --install-types --non-interactive .`
5. Make your changes
6. Format & check your code:
    - Format your code with `python -m black .`
    - Check typing with `python -m mypy --strict .`
7. Push your changes to your forked repository
8. Open a pull request

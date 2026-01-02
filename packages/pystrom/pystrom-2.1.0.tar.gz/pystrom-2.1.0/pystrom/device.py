import logging
from json import JSONDecodeError
from typing import Literal, TypedDict, NotRequired, Any, TypeVar, Type, cast

import requests

from pystrom.exceptions import MyStromException

logger = logging.getLogger(__name__)

DEVICE_TYPE_NAME_MAP = {
    101: "Switch CH v1",
    102: "Bulb",
    103: "Button+ 1st gen",
    104: "Button small/simple",
    105: "LED Strip",
    106: "Switch CH v2",
    107: "Switch EU",
    110: "Motion Sensor",
    112: "Gateway",
    113: "modulo® STECCO / CUBO",
    118: "Button+ 2nd gen",
    120: "Switch Zero",
}

R = TypeVar("R")


class MyStromDevice:
    """Base class for MyStrom devices. All MyStrom devices inherit from this class."""

    def __init__(self, ip: str, mac: str, device_type: int):
        """Do not instantiate this class directly; use MyStromDeviceFactory to create device instances."""
        self.ip: str = ip
        self.mac: str = mac
        self.device_type: int = device_type
        self.settings: dict[str, Any] = {}

    # Properties

    @property
    def type_name(self) -> str:
        """Returns the name of the device type based on the device_type integer."""
        if self.device_type in DEVICE_TYPE_NAME_MAP:
            return DEVICE_TYPE_NAME_MAP[self.device_type]
        else:
            return f"Unknown type: {str(self.device_type)}"

    @property
    def name(self) -> str:
        """Returns the name of the device. Must have fetched settings first."""
        return cast(str, self.settings.get("name", "Name unknown"))

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__} ({self.type_name}) '{self.name}' {self.mac} @ {self.ip}>"
        )

    # Base API

    def api_request(
        self, method: str, path: str, return_type: Type[R] | None = None, **kwargs: Any
    ) -> R:
        """Sends a request to the device API and returns the response in an appropriate format."""
        protocol = "http"
        url = f"{protocol}://{self.ip}/{path.lstrip('/')}"
        logger.info("Requesting %s %s", method.upper(), url)
        r = requests.request(method, url, **kwargs)
        if r.status_code < 200 or r.status_code >= 300:
            logger.error("Error %d while requesting %s", r.status_code, url)
            raise MyStromException(f"Error {r.status_code} while requesting {url}: {r.text}")

        if return_type is None:
            return None  # type: ignore[return-value]
        if return_type is str:
            return r.text  # type: ignore[return-value]
        try:
            return cast(R, r.json())
        except JSONDecodeError:
            logger.error("Error decoding JSON response from %s: %s", url, r.text)
            raise MyStromException(f"Error decoding JSON response from {url}: {r.text}")

    def api_get(self, path: str, return_type: Type[R] | None = None, **kwargs: Any) -> R:
        """Sends a GET request to the device API and returns the response in an appropriate format."""
        return self.api_request("GET", path, return_type=return_type, **kwargs)

    def api_post(self, path: str, return_type: Type[R] | None = None, **kwargs: Any) -> R:
        """Sends a POST request to the device API and returns the response in an appropriate format."""
        return self.api_request("POST", path, return_type=return_type, **kwargs)

    # General API Endpoints

    def get_general_info(self) -> dict[str, Any]:
        """Returns general device information such as network settings, type, firmware version, etc."""
        return self.api_get("api/v1/info", return_type=dict[str, Any])

    def get_wifi_list(self) -> dict[str, int]:
        """Returns a dictionary of available Wi-Fi networks with their signal strength."""
        data = self.api_get("api/v1/scan", return_type=list[int | str])
        networks: dict[str, int] = {}
        for i in range(len(data) // 2):
            networks[str(data[i * 2])] = int(data[i * 2 + 1])
        return networks

    def get_help(self) -> str:
        """Returns a string containing a list of available API endpoints."""
        return self.api_get("help", return_type=str)

    # Common Settings API Endpoints

    def get_settings(self) -> dict[str, Any]:
        """Returns the current settings of the device."""
        self.settings = self.api_get("api/v1/settings", return_type=dict)
        return self.settings

    def set_settings(self, settings: dict[str, Any]) -> None:
        """Sets/Updates the device settings."""
        self.api_post("api/v1/settings", data=settings)


class MyStromSwitch(MyStromDevice):
    """MyStrom Switch device class."""

    def __init__(self, ip: str, mac: str, device_type: int):
        super().__init__(ip=ip, mac=mac, device_type=device_type)

    def turn_on(self) -> None:
        """Turn on the switch."""
        self.api_get("relay?state=1")

    def turn_off(self) -> None:
        """Turn off the switch."""
        self.api_get("relay?state=0")

    def toggle(self) -> bool:
        """Toggle the switch state. If it is on, it will be turned off, and vice versa.
        Returns the new state of the relay."""
        return self.api_get("toggle", return_type=dict[str, bool]).get("relay", False)

    def power_cycle(self, seconds: int = 10) -> None:
        """Power cycle the switch by turning it off, waiting for a specified number of seconds, and then turning it back on.
        Will throw an error if the switch is not currently on.

        Args:
            seconds (int): The number of seconds to wait while the switch is off. Maximum is 3600 seconds (1 hour).
        """
        self.api_get(f"power_cycle?time={seconds}")

    def timer(self, mode: Literal["on", "off", "toggle", "none"], seconds: int = 5) -> None:
        """Set the state of the switch and reverse it after a specified number of seconds."""
        self.api_post("timer", data={"mode": mode, "time": seconds})

    def get_report(self) -> str:
        """Returns a report of the switch's current state, including power consumption, relay state and temperature."""
        return self.api_get("report", return_type=str)

    def get_temperature(self) -> dict[str, float]:
        """Returns the current temperature reading and temperature configuration."""
        return self.api_get("api/v1/temperature", return_type=dict[str, float])


class MyStromBulb(MyStromDevice):
    """MyStrom Bulb device class."""

    class BulbStateResponse(TypedDict):
        on: bool
        color: str
        mode: str  # color mode, "rgb" or "hsv"
        ramp: int  # ramp time in ms
        notifyurl: str

    class BulbStateRequest(TypedDict):
        action: NotRequired[Literal["on", "off", "toggle"]]
        color: NotRequired[str]  # e.g. "255,0,0" for red in RGB
        mode: NotRequired[Literal["hsv", "rgb"]]
        ramp: NotRequired[int]  # ramp time in ms
        notifyurl: NotRequired[str]  # URL to notify via POST when the state changes

    def __init__(self, ip: str, mac: str, device_type: int) -> None:
        super().__init__(ip=ip, mac=mac, device_type=device_type)

    def _post_action(self, data: BulbStateRequest) -> BulbStateResponse:
        return cast(
            MyStromBulb.BulbStateResponse,
            self.api_post(
                f"api/v1/device/{self.mac}",
                return_type=dict[str, MyStromBulb.BulbStateResponse],
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ).get(self.mac),
        )

    def turn_on(self) -> BulbStateResponse:
        """Turn on the bulb."""
        return self._post_action({"action": "on"})

    def turn_off(self) -> BulbStateResponse:
        """Turn off the bulb."""
        return self._post_action({"action": "off"})

    def toggle(self) -> BulbStateResponse:
        """Toggle the bulb."""
        return self._post_action({"action": "toggle"})

    def set_options(self, data: BulbStateRequest) -> BulbStateResponse:
        """Sets options like color, ramp, mode and notifyurl for the bulb."""
        return self._post_action(data)

    def get_device_information(self) -> dict[str, Any]:
        """Returns the device information, including the current state of the bulb."""
        data = self.api_get("api/v1/device", dict[str, Any])
        mac = self.mac.upper()
        return cast(dict[str, Any], data.get(mac, data.get(mac.lower(), {})))


DEVICE_TYPE_CLASS_MAP = {
    101: MyStromSwitch,  # Switch CH v1
    106: MyStromSwitch,  # Switch CH v2
    107: MyStromSwitch,  # Switch EU
    120: MyStromSwitch,  # Switch Zero
    102: MyStromBulb,  # Bulb
}


class MyStromDeviceFactory:
    all_devices: dict[str, MyStromDevice] = {}

    @classmethod
    def _get_or_create_device(cls, mac: str, ip: str, device_type: int) -> MyStromDevice:
        if mac not in cls.all_devices:
            clazz = DEVICE_TYPE_CLASS_MAP.get(device_type, MyStromDevice)
            device = clazz(ip=ip, mac=mac, device_type=device_type)
            cls.all_devices[mac] = device

        device = cls.all_devices[mac]
        device.ip = ip
        return device

    @classmethod
    def from_announcement(cls, data: bytes, ip: str) -> "MyStromDevice":
        mac = data[:6].hex()
        device_type = data[6]
        # flags = data[7]

        return cls._get_or_create_device(mac=mac, ip=ip, device_type=device_type)

    @classmethod
    def from_ip(cls, ip: str) -> "MyStromDevice":
        r = requests.get(f"http://{ip}/api/v1/info")
        if r.status_code != 200:
            raise ConnectionError(f"Could not connect to device at {ip}")
        data = r.json()
        mac = data.get("mac")
        device_type = data.get("type")
        if not mac or not device_type:
            raise ValueError("Invalid device data received from the API")

        return cls._get_or_create_device(mac=mac, ip=ip, device_type=device_type)

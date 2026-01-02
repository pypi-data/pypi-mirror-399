import logging
import socket
from datetime import datetime
from typing import Any

from pystrom.device import MyStromDevice, MyStromDeviceFactory

logger = logging.getLogger(__name__)


class MyStromDeviceFinder:
    """
    Finds MyStrom devices on the local network by listening for UDP broadcasts.

    Usage:

        with MyStromDeviceFinder() as finder:
            devices = finder.find_all()
            for device in devices:
                print(device)
    """

    def __init__(self, ip: str = "0.0.0.0", port: int = 7979):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet (IPv4) / UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ip = ip
        self.port = port

    def __enter__(self) -> "MyStromDeviceFinder":
        self.sock.bind((self.ip, self.port))
        logger.debug("Socket bound to %s:%s", self.ip, self.port)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.sock.close()
        logger.debug("Socket closed")

    def find_all(self) -> list[MyStromDevice]:
        """Find all MyStrom devices on the local network.

        MyStrom devices announce themselves via UDP broadcasts on port 7979 every 5 seconds.
        This methods listens for these broadcasts and returns a list of found devices as soon as
        no new devices are encountered in 10 seconds.

        This method will at least take 10 seconds before it returns.
        """

        logger.info("Looking for devices...")

        ips_found = []
        devices_found = []

        last_new_device_found = datetime.now()

        try:
            while (datetime.now() - last_new_device_found).total_seconds() < 10:
                self.sock.settimeout(5.0)
                data, (ip, _) = self.sock.recvfrom(1024)  # buffer size is 1024 bytes

                if ip not in ips_found:
                    device = MyStromDeviceFactory.from_announcement(data, ip)
                    logger.info("Found device: %s", device)

                    ips_found.append(ip)
                    devices_found.append(device)
                    last_new_device_found = datetime.now()
        except socket.timeout:
            pass

        logger.info("%s devices found!", len(devices_found))
        return devices_found

    def find_continuous(self) -> None:
        """Continuously listen for MyStrom devices on the local network."""

        logger.info("Looking for devices... (Press Ctrl+C to exit!)")

        try:
            while True:
                try:
                    self.sock.settimeout(5.0)
                    data, (ip, _) = self.sock.recvfrom(1024)  # buffer size is 1024 bytes

                    x = MyStromDeviceFactory.from_announcement(data, ip)
                    logger.info("Found device: %s", x)
                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            pass

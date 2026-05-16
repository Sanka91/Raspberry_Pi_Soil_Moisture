import network
from logger import write_log
import time
import socket

class WifiClient:
    def __init__(self, ssid: str, password: str):
        self.ssid = ssid
        self.password = password
        self.wifi = network.WLAN(network.STA_IF)
        self.socket = socket.socket()

    def connect(self, retries: int):
        self.wifi.active(False)
        self.wifi.active(True)
        self.wifi.disconnect()

        for i in range(retries):
            print("Attempting to connect to WiFi...")
            self.wifi.connect(self.ssid, self.password)
            time.sleep(5)
            if self.wifi.isconnected():
                print("Connected to {}!".format(self.ssid))
                print("Config:", self.wifi.ifconfig())
            else:
                write_log("{}: Error: Could not connect to WiFi on attempt {}\n".format(time.time(), i + 1))
                write_log("{}: Status: {}\n".format(time.time(), self.wifi.status()))
                write_log("{}: Config: {}\n".format(time.time(), self.wifi.ifconfig()))
                time.sleep(3)

    def _is_wifi_connected(self):
        """Prüft, ob die WLAN-Verbindung aktiv ist."""
        if self.wifi.isconnected():
            return True
        else:
            write_log("{}: Error: Not connected to Wifi \n".format(time.time()))
            return False

    @staticmethod
    def has_internet_connection():
        """Prüft, ob eine Internet - und Wifiverbindung besteht, indem ein TCP-Connect zu google.com:80 versucht
        wird."""
        if _tcp_reachable() and _is_wifi_connected():
            return True
        else:
            return False

    def _tcp_reachable(self, host="google.com", port=80, timeout_ms=2000):
        """Prüft, ob ein TCP-Connect zu host:port innerhalb timeout_ms gelingt."""
        try:
            addr = self.socket.getaddrinfo(host, port)[0][-1]
            self.socket.settimeout(timeout_ms / 1000)
            self.socket.connect(addr)
            self.socket.close()
            return True
        except Exception:
            return False
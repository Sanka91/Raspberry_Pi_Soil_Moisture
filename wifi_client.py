import network
import time
import socket

class WifiClient:
    def __init__(self, ssid: str, password: str):
        self.ssid = ssid
        self.password = password
        self.wifi = network.WLAN(network.STA_IF)

    def connect(self, retries: int):
        self.wifi.active(False)
        time.sleep(0.5)
        self.wifi.active(True)
        self.wifi.disconnect()

        for i in range(retries):
            try:
                print(f"--- Attempting to connect to {self.ssid} ---")
                self.wifi.connect(self.ssid, self.password)
                # Check every 0.5s for up to 10 seconds total. This connects instantly when ready!
                timeout = 20
                while timeout > 0 and not self.wifi.isconnected():
                    time.sleep(0.5)
                    timeout -= 1

                if self.wifi.isconnected():
                    print(f"Successfully connected to {self.ssid}!")
                    print("Config:", self.wifi.ifconfig())
                    print("-------------------------------------- \n")
                    return True
            except OSError as e:
                print(f"Hardware/Network error during attempt {i + 1}: {e}")

            time.sleep(2)
        print(f"Failed to connect to {self.ssid} after {retries} attempts.")
        return False

    def has_internet_connection(self) -> bool:
        """Prüft, ob eine Internet - und Wifiverbindung besteht, indem ein TCP-Connect zu google.com:80 versucht
        wird."""
        print("--- Checking wifi and internet connection ---")
        if self.wifi.isconnected() and self.tcp_reachable():
            print("Checked connection to {}!".format(self.ssid))
            print("Config:", self.wifi.ifconfig())
            print("Internet connection verified!")
            return True
        else:
            msg = "Not connected to Wifi or internet. Status: {}, Config: {}".format(self.wifi.status(),
                                                                                     self.wifi.ifconfig())
            print(msg)
            time.sleep(3)
            return False

    @staticmethod
    def tcp_reachable(host="google.com", port=80, timeout_ms=2000):
        """Prüft, ob ein TCP-Connect zu host:port innerhalb timeout_ms gelingt."""
        temp_socket = None
        try:
            addr = socket.getaddrinfo(host, port)[0][-1]
            temp_socket = socket.socket()
            temp_socket.settimeout(timeout_ms / 1000)
            temp_socket.connect(addr)
            temp_socket.close()
            return True
        except Exception as e:
            print("TCP connection to {}:{} failed: {}".format(host, port, e))
            return False
        finally:
            if temp_socket is not None:
                try:
                    temp_socket.close()
                except Exception:
                    pass  # Ignore errors if close fails because it was never truly opened
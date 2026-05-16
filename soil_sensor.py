from logger import write_log
import time

class SoilSensor:
    # https://wiki.dfrobot.com/sen0602/#tech_specs
    # https://wiki.dfrobot.com/sen0602/docs/19656
    # Inquiry Frame: 01 (Addr), 03 (Func), 0000 (Start), 0004 (Length), 4409 (CRC)
    _inquiry_frame = b'\x01\x03\x00\x00\x00\x04\x44\x09'

    def __init__(self, baudrate, tx_pin, rx_pin, timeout=500):
        self._uart = UART(0, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=timeout)
        print("Initializing 3-in-1 Sensor... \n")
        print("UART Config: Baudrate={}, TX Pin={}, RX Pin={}, Timeout={}ms".format(baudrate, tx_pin, rx_pin, timeout))
        pass

    # Returns a tuple of (humidity, temperature, pH) or None if reading fails
    @staticmethod
    def request_reading() -> tuple:
        uart.write(_inquiry_frame)
        time.sleep(0.3)
        if uart.any():
            response = uart.read()
            if is_valid_response(response):
                # Standard response: [Addr][Func][ByteCount][Hum_H][Hum_L][Temp_H][Temp_L][Empty_H][Empty_L][PH_H][PH_L][CRC_L][CRC_H]
                if len(data) < 13:
                    return None

                # 1. Humidity (Bytes 3 & 4) -> Value / 10
                hum_raw = (data[3] << 8) | data[4]
                humidity = hum_raw / 10.0

                # 2. Temperature (Bytes 5 & 6) -> Signed Value / 10
                temp_raw = (data[5] << 8) | data[6]
                # Handle negative temperatures using two's complement
                if temp_raw > 0x7FFF:
                    temp_raw -= 0x10000
                temperature = temp_raw / 10.0

                # 3. pH (Bytes 9 & 10) -> Value / 10
                # Per your manual: 0x38 (56) = 5.6 pH
                ph_raw = (data[9] << 8) | data[10]
                ph = ph_raw / 10.0

                return humidity, temperature, ph
        else:
            write_log("{}: No response from sensor...".format(time.time()))
        return None

    # Verify basic Modbus structure before decoding
    @staticmethod
    def _is_valid_response(response):
        if len(response) >= 3 and response[1] == 0x03:
            return True
        return False
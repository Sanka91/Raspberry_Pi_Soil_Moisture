from machine import UART, Pin
import ssl
import utime
import machine
import _thread
# from logger import write_log
from soil_sensor import SoilSensor
from utilities import sync_time
from wifi_client import WifiClient
from hive_thread_worker import add_to_publish_queue, hivemq_core1_worker

pump_1 = Pin(15, Pin.OUT)
# Start with relay off (active LOW)
pump_1.value(1)
led = Pin("LED", Pin.OUT)
led.off()

wifi_client = WifiClient(ssid="FRITZ!Box 7490", password="53910924776233792153")
wifi_client.connect(retries=5)

# --- START THE SECOND THREAD ---
_thread.start_new_thread(hivemq_core1_worker)

while True:
    if not wifi_client.has_internet_connection():
        wifi_client.connect(retries=5)
        sync_time(retries=5)

    soil_sensor = SoilSensor(baudrate=9600, tx_pin=16, rx_pin=17)
    humidity, temp, ph = soil_sensor.request_reading()

    # Do not use the character ° for degrees. It's 1 byte in python but a different size in mqtt. This causes errors.
    publish_string = f"Humidity: {humidity}" + " %" + f"Temperature: {temp}" + " C" + f"pH: {ph}"

    add_to_publish_queue("Raised_Bed/Blue", publish_string)


    pump_1.value(0)
    print("Relay is on")
    time.sleep(5)

    pump_1.value(1)
    print("Relay is off")
    led.off()
    time.sleep(5)

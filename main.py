from machine import UART, Pin, ADC
import json
import time
import _thread
import config
from soil_sensor import SoilSensor
from pump_client import PumpController
from core1_thread import add_to_publish_queue, core1_thread, publish_lock

# Internal temperature sensor on ADC pin 4
internal_temp_sensor = ADC(4)

pump = PumpController(pin=26)
soil_sensor = SoilSensor(baudrate=9600, tx_pin=16, rx_pin=17)

# --- START THE SECOND THREAD ---
_thread.start_new_thread(core1_thread, ())
time.sleep(2)

while True:
    try:
        humidity, temp, ph = soil_sensor.request_reading()
        int_temp_value = internal_temp_sensor.read_u16() * (3.3 / 65535)
        # # Calculate temperature using the voltage
        int_temp = round(27 - (int_temp_value - 0.706) / 0.001721, 1)

        # Do not use the character ° for degrees. It's 1 byte in python but a different size in mqtt. This causes errors.
        publish_json = json.dumps({
            "last_reading": time.time(),
            "temperature_celsius": temp,
            "humidity_percent": humidity,
            "ph": ph,
            "watering_on_demand": config.WATERING_ON_DEMAND,
            "watering_duration_seconds": config.WATERING_DURATION_SECONDS,
            "humidity_threshold_percent": config.HUMIDITY_THRESHOLD_PERCENT,
            "measurement_interval_seconds": config.MEASUREMENT_INTERVAL_SECONDS,
            "temp_internal_celsius": int_temp
        })

        print(publish_json)
        print("--------------------------------------\n")

        add_to_publish_queue("Raised_Bed/Blue", publish_json.encode('utf-8'))

        if humidity <= config.HUMIDITY_THRESHOLD_PERCENT or config.WATERING_ON_DEMAND:
            pump.run_for_duration(seconds=config.WATERING_DURATION_SECONDS)
            # After watering, we reset the on-demand flag to prevent continuous watering.
            config.WATERING_ON_DEMAND = False

        time.sleep(config.MEASUREMENT_INTERVAL_SECONDS)
    except Exception as e:
        print("[Core 0]: Problem in main loop: {}".format(e))
        time.sleep(config.MEASUREMENT_INTERVAL_SECONDS)


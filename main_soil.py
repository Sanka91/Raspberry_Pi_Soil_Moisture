import machine
import utime

# Setup ADC on GP26
moisture_sensor = machine.ADC(26)

# Your calibrated values
DRY_VALUE = 55000
WET_VALUE = 25000

while True:
    # Read raw value (0 to 65535)
    # Most soil sensors: ~65000 is bone dry, ~20000 is submerged in water
    raw_value = moisture_sensor.read_u16()

    # Optional: Convert to percentage (Calibration needed!)
    percentage = (DRY_VALUE - raw_value) / (DRY_VALUE - WET_VALUE) * 100

    percentage = max(0, min(100, percentage))
    print(f"Moisture Raw Value: {raw_value}")
    print(f"Moisture Percentage: {percentage}")
    utime.sleep(5)
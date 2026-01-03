import machine
import utime

# Setup PIR on GP22
pir = machine.Pin(28, machine.Pin.IN)

print("Sensor stabilizing... stay still for 60 seconds")
utime.sleep(60)  # PIR sensors need a 'warm up' period to map the room's heat

while True:
    if pir.value() == 1:
        print("ALARM! Motion Detected!")
        # You could trigger your Home Assistant notification here!
        utime.sleep(5)  # Wait a bit so we don't spam the console
    else:
        print("Monitoring...")

    utime.sleep(1)
import network
import time
import ntptime
import ssl
from umqtt.simple import MQTTClient
import utime
import machine

# 1. Connect to WiFi
SSID = "Virenschleuder"
PASSWORD = "Ja_rate_mal_91!"

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
wlan.active(True)
wlan.disconnect()
wlan.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(5)

time.sleep(5)

# 2. Sync Time (Crucial for TLS!)
print("Syncing time via NTP...")
ntptime.settime()

# 1. Create the SSL Context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

# 2. Load the CA certificate
# Note: Ensure ca.der is on your Pico
with open("ca.der", "rb") as f:
    ca_data = f.read()
context.load_verify_locations(cadata=ca_data)

# 3. Configure the context
context.verify_mode = ssl.CERT_REQUIRED

# This MUST match the CN of your server certificate
context.check_hostname = True
MQTT_SERVER = "34.23.79.183"

# 4. Initialize the Client
client = MQTTClient(
    client_id="Pico_W_Moisture_Sensor",
    server=MQTT_SERVER,
    port=8883,
    user="Philipp",
    password="@3Zai5$0!kP+Xt=a",
    ssl=context
)
# 4. MQTT Setup
# Note: server_hostname MUST match the CN you used for your cert

print("Connecting to Mosquitto via TLS...")
client.connect()
print("Connected!")

# Setup Moisture sensor on GP22
moisture_sensor = machine.ADC(26)

# Calibrated values
# Read raw value (0 to 65535)
# Most soil sensors: ~65000 is bone dry, ~20000 is submerged in water
DRY_VALUE = 55000
WET_VALUE = 25000

led = machine.Pin("LED", machine.Pin.OUT)

while True:

    raw_value = moisture_sensor.read_u16()

    # Optional: Convert to percentage (Calibration needed!)
    percentage = (DRY_VALUE - raw_value) / (DRY_VALUE - WET_VALUE) * 100

    percentage = max(0, min(100, percentage))
    print(f"Moisture Raw Value: {raw_value}")
    print(f"Moisture Percentage: {percentage}")

    client.publish("topic/moisture", "{:.2f}".format(percentage))
    print("Message sent.")
    utime.sleep(10)
    print("Going into lightsleep mode")
    led.on()
    machine.lightsleep(60000)
    led.off()



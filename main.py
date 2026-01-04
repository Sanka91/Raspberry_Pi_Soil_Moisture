import network
import time
import ntptime
import ssl
from umqtt.simple import MQTTClient

# 1. Connect to WiFi
SSID = "Virenschleuder"
PASSWORD = "Ja_rate_mal_91!"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(1)

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
    client_id="PicoW_Sensor",
    server=MQTT_SERVER,
    port=8883,
    user="Philipp",
    password="*jQsWAw%IumrNB'L",
    ssl=context  # Pass the context object here, not a dict
)
# 4. MQTT Setup
# Note: server_hostname MUST match the CN you used for your cert

print("Connecting to Mosquitto via TLS...")
client.connect()
print("Connected!")

# 5. Send Data
client.publish("test", "Hello from Secure Pico!")
print("Message sent.")
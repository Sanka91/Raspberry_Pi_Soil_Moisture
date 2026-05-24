# Key is topic, value is a list of JSON objects to publish for that topic
mqtt_publish_queue = {}
# How long to wait between measurements
MEASUREMENT_INTERVAL_SECONDS = 60 * 60
# 30 seconds == 250ml
WATERING_DURATION_SECONDS = 5
# If the soil humidity is at or below this percentage, the pump will be triggered
HUMIDITY_THRESHOLD_PERCENT = 50
# Flag to control watering on demand
WATERING_ON_DEMAND = False

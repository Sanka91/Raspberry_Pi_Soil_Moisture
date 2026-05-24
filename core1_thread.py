import ssl
from umqtt.simple import MQTTClient
import time
import _thread
from utilities import sync_time
from wifi_client import WifiClient
import config
import gc
from machine import Pin

# Lock for thread-safe access to the publish queue
publish_lock = _thread.allocate_lock()

onboard_led = Pin("LED", Pin.OUT)

# Appends messages to the list for the topic, or creates a new list if the topic does not yet exist in the queue.
def add_to_publish_queue(topic, message):
    try:
        publish_lock.acquire()
        if topic in config.mqtt_publish_queue:
            if len(config.mqtt_publish_queue[topic]) >= 10:
                print(f"[Core 1 WARNING]: Publish queue for topic '{topic}' has reached 10 messages. Oldest message will"
                      f" be dropped to prevent memory issues.")
                # Remove the oldest message to make room for the new one
                config.mqtt_publish_queue[topic].pop(0)
            config.mqtt_publish_queue[topic].append(message)
        else:
            config.mqtt_publish_queue[topic] = [message]
    finally:
        publish_lock.release()


def on_mqtt_message_received(topic, msg):
    # MicroPython delivers data as bytes, so we decode it to regular text strings
    topic_str = topic.decode('utf-8')
    payload_str = msg.decode('utf-8')

    print(f"\n[Core 1] MQTT Inbound Triggered! Topic: {topic_str} | Payload: {payload_str}")

    try:
        publish_lock.acquire()
        if topic_str == "Raised_Bed/Blue/set_measurement_interval":
            config.MEASUREMENT_INTERVAL_SECONDS = int(payload_str)
            print(f"[Core 1]: Soil measurement interval successfully changed to every {config.MEASUREMENT_INTERVAL_SECONDS} seconds.")
        elif topic_str == "Raised_Bed/Blue/set_watering_duration":
            config.WATERING_DURATION_SECONDS = int(payload_str)
            print(f"[Core 1]: Pump runtime interval successfully changed to {config.WATERING_DURATION_SECONDS} seconds.")
        elif topic_str == "Raised_Bed/Blue/set_humidity_threshold":
            config.HUMIDITY_THRESHOLD_PERCENT = int(payload_str)
            print(f"[Core 1]: Humidity threshold successfully changed to {config.HUMIDITY_THRESHOLD_PERCENT} %.")
        elif topic_str == "Raised_Bed/Blue/watering_on_demand":
            if payload_str.lower() in ["true", "1", "on"]:
                config.WATERING_ON_DEMAND = True
                print("[Core 1]: One-time watering request received!")
            else:
                config.WATERING_ON_DEMAND = False
    except ValueError:
        print("[Core 1 ERROR]: Received a payload that couldn't be parsed into an integer.")
    finally:
        publish_lock.release()

# --- Thread: DEDICATED HIVEMQ WATCHDOG ---
# This thread will run the HiveMQ watchdog, which maintains the MQTT connection and publishes/subscribes to messages.
def core1_thread():
    print("[Core 1]: Starting thread...")

    wifi_client = None
    mqtt_client = None

    mqtt_server = "ef53cd69c81c4fa3bbdffa29e4ea152f.s1.eu.hivemq.cloud"
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    # Connect loop with auto-reconnect for wifi and mqtt
    while True:
        try:
            # Establish Wi-Fi Connection
            if wifi_client is None:
                wifi_client = WifiClient(ssid="FRITZ!Box 7490", password="53910924776233792153")
                wifi_client.connect(retries=5)
                sync_time(retries=5)
            elif not wifi_client.has_internet_connection():
                wifi_client.connect(retries=5)
                sync_time(retries=5)
                onboard_led.off()

            if wifi_client.has_internet_connection():
                if onboard_led.value() == 0:
                    onboard_led.on()

            if mqtt_client is None:
                mqtt_client = MQTTClient(
                    client_id="Pico_W_Raised_Bed_BLUE",
                    server=mqtt_server,
                    port=8883,
                    user="Philipp",
                    password="Test7[]/-x6890as",
                    ssl=ssl_context,
                    keepalive=120
                )
                print("[Core 1]: Created new instance of MQTTClient...")
                mqtt_client.connect()
                # Register callback and subscriptions immediately after connect
                mqtt_client.set_callback(on_mqtt_message_received)
                mqtt_client.subscribe("Raised_Bed/Blue/set_measurement_interval")
                mqtt_client.subscribe("Raised_Bed/Blue/set_watering_duration")
                mqtt_client.subscribe("Raised_Bed/Blue/set_humidity_threshold")
                mqtt_client.subscribe("Raised_Bed/Blue/watering_on_demand")

                print("[Core 1]: HiveMQ connected, callbacks registered, and subscribed!")
                print("-------------------------------------- \n")

            elif not mqtt_client.sock:  # If not connected
                print("[Core 1]: MQTTClient exists, connecting to HiveMQ...")
                mqtt_client.connect()
                print("[Core 1]: HiveMQ connected and stable!")

                # Register the callback for incoming MQTT messages
                mqtt_client.set_callback(on_mqtt_message_received)

                # Subscribe to control channels (use qos=1 for reliability if supported)
                mqtt_client.subscribe("Raised_Bed/Blue/set_measurement_interval")
                mqtt_client.subscribe("Raised_Bed/Blue/set_watering_duration")
                mqtt_client.subscribe("Raised_Bed/Blue/set_humidity_threshold")
                mqtt_client.subscribe("Raised_Bed/Blue/watering_on_demand")

                print("[Core 1]: HiveMQ connected, callbacks registered, and subscribed!")
                print("-------------------------------------- \n")

            publish_messages(mqtt_client)

            # Use a small nested loop to listen for messages continuously for 90 seconds.
            print("[Core 1]: Entering alert/listening phase...")
            for _ in range(45):
                # .check_msg() looks at the chip's internal network buffer.
                # If an MQTT packet is sitting there, it instantly fires your callback.
                # If nothing is there, it immediately passes through without freezing.
                mqtt_client.check_msg()
                time.sleep(1)

        except OSError as e:
            print(f"[Core 1]: Error ({e}). Retrying in 10s...")
            try:
                if mqtt_client is not None:
                    mqtt_client.disconnect()
            except Exception as ex:
                print(f"[Core 1]: Error disconnecting MQTT client during cleanup ({ex}).")

            try:
                if wifi_client is not None:
                    wifi_client.disconnect()
            except Exception as ex:
                print(f"[Core 1]: Error disconnecting Wi-Fi client during cleanup ({ex})")

            mqtt_client = None
            wifi_client = None

            time.sleep(10)
            continue
        finally:
            pass
            gc.collect()

"""Publishes all messages in the config.mqtt_publish_queue to HiveMQ. 
If there are no messages, it sends a PING to keep the connection alive."""
def publish_messages(mqtt_client: MQTTClient):

    # Grab a snapshot list of the keys so we aren't modifying the dict while reading it
    publish_lock.acquire()

    try:
        topics = list(config.mqtt_publish_queue.keys())
    finally:
        publish_lock.release()

    # Send the background PING heartbeat to reset HiveMQ's timer if there are no messages to publish
    if not topics:
        try:
            mqtt_client.ping()
        except OSError as e:
            print(f"[Core 1]: Error during MQTT ping ({e}). Will attempt to reconnect in the main loop.")
            raise

    for mqtt_topic in topics:
        publish_lock.acquire()
        try:
            # Pop the message list out of the dictionary safely or get an empty list if the key is not found
            message_list = config.mqtt_publish_queue.pop(mqtt_topic, [])
        finally:
            publish_lock.release()

        if not message_list:
            continue

        for index, msg in enumerate(message_list):
            try:
                mqtt_client.publish(mqtt_topic, msg)
            except OSError as e:
                print(f"[Core 1]: publish failed for topic {mqtt_topic} ({e}), re-queueing remaining messages")
                # Get the remaining messages that were not published, including the current one
                remaining_messages = message_list[index:]
                publish_lock.acquire()
                try:
                    if mqtt_topic in config.mqtt_publish_queue:
                        # Prepend remaining messages to the front of the existing list
                        config.mqtt_publish_queue[mqtt_topic] = remaining_messages + config.mqtt_publish_queue[mqtt_topic]
                    else:
                        config.mqtt_publish_queue[mqtt_topic] = remaining_messages
                finally:
                    publish_lock.release()
                raise

            print("[Core 1]: Publishing {} queued messages for topic: {}".format(len(message_list), mqtt_topic))

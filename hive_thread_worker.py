# Key is topic, value is a list of messages to publish for that topic
mqtt_publish_queue = {}

# Appends messages to the list for the topic, or creates a new list if the topic does not yet exist in the queue.
def add_to_publish_queue(topic, message):
    if topic in mqtt_publish_queue:
        mqtt_publish_queue[topic].append(message)
    else:
        mqtt_publish_queue[topic] = [message]

# --- Thread: DEDICATED HIVEMQ WATCHDOG ---
# This thread will run the HiveMQ watchdog, which maintains the MQTT connection and publishes messages from the queue.
def hivemq_core1_worker():
    global mqtt_publish_queue

    print("[Core 1] Starting HiveMQ thread...")

    mqtt_server = "ef53cd69c81c4fa3bbdffa29e4ea152f.s1.eu.hivemq.cloud"
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    mqtt_client = MQTTClient(
        client_id="Pico_W_Raised_Bed_BLUE",
        server=mqtt_server,
        port=8883,
        user="Philipp",
        password="Test7[]/-x6890as",
        ssl=ssl_context,
        timeout=120
    )

    # Connect loop with auto-reconnect
    while True:
        try:
            if not mqtt_client.sock:  # If not connected
                print("Thread: Connecting to HiveMQ...")
                mqtt_client.connect()
                print("Thread: Connected and Stable!")

            # Send the background PING heartbeat to reset HiveMQ's timer
            mqtt_client.ping()

            for k,v in mqtt_publish_queue.items():
                print("Thread: Publishing queued messages for topic: {}".format(k))
                for msg in v:
                    mqtt_client.publish(k, msg)
                del mqtt_publish_queue[k]  # Remove after publishing

        except OSError as e:
            print("Thread Connection hiccup ({e}). Retrying in 10s...")
            try:
                mqtt_client.disconnect()
            except:
                pass
            time.sleep(10)
            continue

        # Sleep for 5 seconds before checking heartbeats and queues again
        time.sleep(5)

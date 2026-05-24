import ntptime
import time
import socket

NTP_TIMEOUT = 5

def sync_time(retries: int):
    print("--- Syncing Pico system clock via NTP ---")
    for i in range(retries):
        try:
            print(f"NTP Sync Attempt {i + 1}...")
            ntptime.host = "pool.ntp.org"
            ntptime.timeout = NTP_TIMEOUT
            ntptime.settime()
            print("Time synced successfully!")
            return True

        except Exception as e:
            print(f"[WARN] NTP attempt {i + 1} failed: {e}")

        time.sleep(2)

    return False

import ntptime

def sync_time(retries: int):
    print("Syncing time with internet...")
    for i in range(retries):
        try:
            # This fetches the current UTC time from pool.ntp.org and sets the Pico's internal clock
            ntptime.settime()
            print("Time synced successfully!")
        except Exception as e:
            write_log("{}: Failed to sync time:".format(time.time()) + str(e))

from machine import Pin
import time

class PumpController:
    def __init__(self, pin: int):
        print(f"--- Initializing Pump on GPIO {pin} ---")
        self.pump = Pin(pin, Pin.OUT)
        self.pump.value(1)  # Initialize with relay off (active LOW)

    def run_for_duration(self, seconds: float):
        try:
            print(f"--- Starting pump for {seconds} seconds ---")
            self.pump.value(0)
            print("Pump turned ON")
            time.sleep(seconds)
        except Exception as e:
            print(f"Pump sequence interrupted by error: {e}.")
        finally:
            self.pump.value(1)
            print("Pump turned OFF")
            print("-------------------------------------- \n")

    def run_for_amount(self, amount_ml: float):
        """Calculates required seconds and hands execution to the safe duration method."""
        print(f"--- Request to run pump for {amount_ml} ml ---")

        # Calculate precise seconds needed based on a 500 ml/min flow rate
        calculated_seconds = (amount_ml / 500.0) * 60.0

        self.run_for_duration(calculated_seconds)


import machine
import utime

# Setup the Analog pin
mic_pin = machine.ADC(26)


def get_volume(samples=100):
    min_val = 65535
    max_val = 0

    # Sample the mic quickly to find the "peak-to-peak" amplitude
    for _ in range(samples):
        val = mic_pin.read_u16()
        if val > max_val: max_val = val
        if val < min_val: min_val = val

    # The difference between the highest and lowest point is the "volume"
    return max_val - min_val


while True:
    volume = get_volume()

    # You might need to adjust this threshold based on your room's noise
    if volume > 5000:
        print(f"Loud Sound Detected! Level: {volume}")
    else:
        print(f"Quiet... Level: {volume}")

    utime.sleep(1)
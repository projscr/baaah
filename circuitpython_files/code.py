import usb_cdc
import board
import digitalio
import time


# Initialize all 26 GPIO pins as inputs with pull-up resistors
pins = [getattr(board, f"GP{i}") for i in range(26)]
inputs = [digitalio.DigitalInOut(pin) for pin in pins]

for input_pin in inputs:
    input_pin.direction = digitalio.Direction.INPUT
    input_pin.pull = digitalio.Pull.UP

def send_data(data):
    if usb_cdc.data:
        usb_cdc.data.write(data.encode('utf-8'))

def receive_data():
    if usb_cdc.data and usb_cdc.data.in_waiting > 0:
        return usb_cdc.data.read(usb_cdc.data.in_waiting).decode('utf-8').strip()
    return None

# Track the state of each pin to detect button presses
previous_states = [True] * 26

while True:
    # Check for button presses
    for i, input_pin in enumerate(inputs):
        current_state = input_pin.value
        # Detect a button press (transition from HIGH to LOW)
        if previous_states[i] and not current_state:
            send_data(f"{i}\n")
        previous_states[i] = current_state

    # Check for incoming data
    incoming_message = receive_data()
    if incoming_message == "baaah":
        send_data("humbug\n")

    time.sleep(0.01)  # Debounce delay
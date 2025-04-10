import serial
import serial.tools.list_ports

def list_com_ports():
    """List all available COM ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def main():
    # List available COM ports
    com_ports = list_com_ports()
    if not com_ports:
        print("No COM ports found.")
        return

    print("Available COM ports:")
    for i, port in enumerate(com_ports):
        print(f"{i}: {port}")

    # Select a COM port
    try:
        selection = int(input(f"Select a COM port (0-{len(com_ports) - 1}): "))
        if selection < 0 or selection >= len(com_ports):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    selected_port = com_ports[selection]
    print(f"Connecting to {selected_port}...")

    # Open the selected COM port
    try:
        with serial.Serial(selected_port, baudrate=9600, timeout=1) as ser:
            # Send "baaah"
            ser.write(b"baaah\n")
            print("Sent: baaah")

            # Wait for "humbug"
            while True:
                response = ser.readline().decode('utf-8').strip()
                if response:
                    print(f"Received: {response}")
                    if response == "humbug":
                        print("Device responded with 'humbug'. Listening for further messages...")
                    # Continue printing any other messages
    except serial.SerialException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
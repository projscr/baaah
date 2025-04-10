import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import os
import pyautogui

# List of action names
action_names = [
    "Play / Pause", "Vol +", "Vol -", "Skip Back", "Skip Forward",
    "Windows Key", "Action 7", "Action 8", "Action 9", "Action 10",
    "Action 11", "Action 12", "Action 13", "Action 14", "Action 15",
    "Action 16", "Action 17", "Action 18", "Action 19", "Action 20",
    "Action 21", "Action 22", "Action 23", "Action 24", "Action 25",
    "Action 26", "Action 27", "Action 28", "Action 29", "Action 30"
]

# Placeholder functions for actions
def temp_action_placeholder(action_number):
    if (int(action_number) == 1):
        pyautogui.press("playpause")
    elif (int(action_number) == 2):
        pyautogui.press("volumeup")
    elif (int(action_number) == 3):
        pyautogui.press("volumedown")
    elif (int(action_number) == 4):
        pyautogui.press("prevtrack")
    elif (int(action_number) == 5):
        pyautogui.press("nexttrack")
    elif (int(action_number) == 6):
        pyautogui.hotkey("win")
    else:
        print(f"Action {action_number} executed")

# Create a dictionary of actions based on action names
actions = {name: lambda name=name: temp_action_placeholder(action_names.index(name) + 1) for name in action_names}

# Global variables
serial_connection = None
slot_action_mapping = {slot: None for slot in range(27)}  # Map slots to selected actions

def list_com_ports():
    """List all available COM ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def validate_com_port(port):
    """Validate the COM port by sending 'baaah' and waiting for 'humbug'."""
    try:
        with serial.Serial(port, baudrate=9600, timeout=1) as ser:
            ser.write(b"baaah\n")
            response = ser.readline().decode('utf-8').strip()
            return response == "humbug"
    except serial.SerialException:
        return False

def connect_to_com_port(selected_port, status_label):
    """Connect to the selected COM port and start the main loop."""
    global serial_connection
    try:
        serial_connection = serial.Serial(selected_port, baudrate=9600, timeout=1)
        status_label.config(text=f"Connected to {selected_port}")
        threading.Thread(target=main_loop, daemon=True).start()
    except serial.SerialException as e:
        status_label.config(text=f"Error: {e}")

def main_loop():
    """Main loop to read numbers from the serial port and execute actions."""
    global serial_connection
    while serial_connection and serial_connection.is_open:
        try:
            data = serial_connection.readline().decode('utf-8').strip()
            if data.isdigit():
                slot_number = int(data)
                if slot_number in slot_action_mapping and slot_action_mapping[slot_number]:
                    # Execute the action assigned to the slot
                    slot_action_mapping[slot_number]()
        except serial.SerialException:
            break

def create_ui():
    """Create the main UI with a bouncing baaah.png background."""
    root = tk.Tk()
    root.title("Baah Action Selector")
    root.iconbitmap("baaah.ico")

    # Load the image for the bouncing effect
    try:
        baaah_image = tk.PhotoImage(file="baaah.png")
    except tk.TclError:
        print("Error: baaah.png not found. Ensure the file is in the same directory.")
        return

    # Make the canvas fill the entire window
    root.geometry("550x750")  # Set initial window size
    root.configure(bg="white")  # Set the background color to white

    # Create a canvas for the background animation
    canvas = tk.Canvas(root, bg="white", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Add the image to the canvas
    image_id = canvas.create_image(400, 300, image=baaah_image)

    # Variables for bouncing logic
    dx, dy = 2, 2  # Speed of movement

    def move_image():
        """Move the image and bounce it off the edges."""
        nonlocal dx, dy
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        x, y = canvas.coords(image_id)

        # Check for collisions with canvas edges
        if x + baaah_image.width() // 2 >= canvas_width or x - baaah_image.width() // 2 <= 0:
            dx = -dx  # Reverse horizontal direction
        if y + baaah_image.height() // 2 >= canvas_height or y - baaah_image.height() // 2 <= 0:
            dy = -dy  # Reverse vertical direction

        # Move the image
        canvas.move(image_id, dx, dy)

        # Schedule the next frame
        root.after(10, move_image)

    # Start the animation
    move_image()

    # Create a frame for the widgets (overlaid on the canvas)
    widget_frame = ttk.Frame(canvas, padding="10")
    widget_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the frame

    # Create a dropdown for each slot
    for slot in range(27):  # 0-26 slots
        ttk.Label(widget_frame, text=f"Slot {slot}").grid(row=slot, column=0, sticky=tk.W)
        action_var = tk.StringVar(value="Select Action")
        
        def assign_action(action_name, slot=slot):
            """Assign the selected action to the slot."""
            if action_name != "Select Action":
                slot_action_mapping[slot] = actions[action_name]
                print(f"Assigned Action {action_name} to Slot {slot}")

        action_menu = ttk.OptionMenu(
            widget_frame, action_var, "Select Action", *action_names,
            command=lambda action_name, slot=slot: assign_action(action_name, slot)
        )
        action_menu.grid(row=slot, column=1, sticky=tk.W)

    # COM port selection
    com_frame = ttk.Frame(widget_frame, padding="10")
    com_frame.grid(row=28, column=0, columnspan=2, sticky=(tk.W, tk.E))

    ttk.Label(com_frame, text="Select a Baaah COM Device").grid(row=0, column=0, sticky=tk.W)
    com_var = tk.StringVar(value="Select a Baaah COM Device")
    com_ports = list_com_ports()
    com_menu = ttk.OptionMenu(com_frame, com_var, "Baaah COM", *com_ports)
    com_menu.grid(row=0, column=1, sticky=tk.W)

    status_label = ttk.Label(com_frame, text="Not connected")
    status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)

    def on_connect():
        selected_port = com_var.get()
        if selected_port in com_ports:
            if validate_com_port(selected_port):
                connect_to_com_port(selected_port, status_label)
            else:
                status_label.config(text="Not a Baaah Device.")
        else:
            status_label.config(text="Select a valid Baaah port.")

    ttk.Button(com_frame, text="Baaah!", command=on_connect).grid(row=0, column=2, sticky=tk.W)

    # Add a Quit button
    ttk.Button(widget_frame, text="No Baaah :(", command=root.destroy).grid(row=29, column=0, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_ui()
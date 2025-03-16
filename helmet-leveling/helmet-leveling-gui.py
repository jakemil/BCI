import serial
import tkinter as tk

# Update with your Arduino's port
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

def select_servo(servo):
    arduino.write(str(servo).encode())
    status_label.config(text=f"Controlling Servo {servo}")

def change_angle(direction):
    if direction == "increase":
        arduino.write(b'+')
    elif direction == "decrease":
        arduino.write(b'-')

def reset_servos():
    arduino.write(b'R')
    status_label.config(text="All servos reset to 0°")

# GUI Setup
root = tk.Tk()
root.title("8-Servo Controller")

status_label = tk.Label(root, text="Select Servo to Control", font=("Arial", 14))
status_label.pack(pady=10)

# Create buttons for selecting each servo
for i in range(1, 9):
    btn = tk.Button(root, text=f"Control Servo {i}", command=lambda i=i: select_servo(i), width=20, height=1)
    btn.pack(pady=3)

increase_btn = tk.Button(root, text="Increase Angle (+5°)", command=lambda: change_angle("increase"), width=20, height=2)
increase_btn.pack(pady=5)

decrease_btn = tk.Button(root, text="Decrease Angle (-5°)", command=lambda: change_angle("decrease"), width=20, height=2)
decrease_btn.pack(pady=5)

reset_btn = tk.Button(root, text="Reset All Servos to 0°", command=reset_servos, width=20, height=2, bg="red", fg="white")
reset_btn.pack(pady=10)

root.mainloop()


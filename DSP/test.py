import pyfirmata2
import time

# Initialize Arduino
board = pyfirmata2.Arduino("/dev/cu.usbmodem14201")

print("connected to board")

# while this statement is true execute script hereunder
HIGH = True  # Create a high state for turn on led
LOW = False  # Create a low state for turn off led
LED_pin = board.get_pin(
    "d:5:o"
)  # Initialize the pin (d => digital, 13 => Number of the pin, o => output)

for i in range(10):  # Loop to blink the micro-led dix times
    LED_pin.write(HIGH)  # Turn on the led
    time.sleep(0.5)  # Delay of 0.5 seconds
    LED_pin.write(LOW)  # Turn off the led
    time.sleep(0.5)  # Delay of 0.5 seconds

import pyaudio
import numpy as np
import numpy.fft as fft
from scipy.signal import butter, lfilter
import keyboard
import pyfirmata
import time

# Initialize Arduino
board = pyfirmata.Arduino("C/dev/cu.usbmodem14201")

# Initialize PyAudio
p = pyaudio.PyAudio()

# Audio stream parameters
FORMAT = pyaudio.paInt8
CHANNELS = 1
RATE = 22000
sample_time = 0.1
CHUNK = int(RATE * sample_time)

# Start the audio stream
stream = p.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
)

# Define the frequency ranges for different drums
BASS_DRUM_FREQ_RANGE = (75, 125)  # Bass drum typically in 50-100 Hz
SNARE_DRUM_FREQ_RANGE = (400, 550)  # Snare drum typically in 200-220 Hz
HI_HAT_FREQ_RANGE = (8800, 9350)
# Hi-hat typically in 300-500 Hz but choose this range to avoid overlap with snare

# Define the Peak threshold for each drum
peak_threshold_bass = 300
peak_threshold_snare = 900
peak_threshold_hihat = 100

# Update threshold based on calibration
TH_BASS = 0
TH_SNARE = 0
TH_HIHAT = 0

# Max magnitude for each drum recorded
max_bass = []
max_snare = []
max_hihat = []

END = False


# Key press event handler
def on_space_bar_press(e):
    global END
    END = True
    # print("Space bar pressed, preparing to exit loop...")


# Register the space bar press event
keyboard.on_press_key("space", on_space_bar_press)


def calibrate_drum(drum_name, freq_range, threshold_peak, max_list):
    global END, TH_BASS, TH_SNARE, TH_HIHAT, peak_threshold_bass, peak_threshold_snare, peak_threshold_hihat

    END = False

    input(f"Press Enter to start calibrating {drum_name} Drum...")
    print(f"Calibrating {drum_name} Drum... Play the samples now.")
    print("Press space bar to stop calibration.")

    # Register the space bar press event
    keyboard.on_press_key("space", on_space_bar_press)

    while not END:
        raw_data = stream.read(CHUNK, exception_on_overflow=False)
        data = np.frombuffer(raw_data, dtype=np.int8)
        data_fft = np.abs(fft.fft(data))[: CHUNK // 2]

        freq_index = (
            freq_range[0] * CHUNK // RATE,
            freq_range[1] * CHUNK // RATE,
        )

        drum_fft = data_fft[freq_index[0] : freq_index[1]]
        current_max = np.max(drum_fft)

        if current_max > threshold_peak:
            max_list.append(current_max)
            threshold_peak = (current_max / 3 + threshold_peak) / 2
            print(threshold_peak)

    max_list = np.array(max_list)

    if len(max_list) == 0:
        print(
            f"No {drum_name} drum detected. Please try again by restarting the program."
        )
        return

    if drum_name == "Bass":
        TH_BASS = np.mean(max_list) * 0.7
    elif drum_name == "Snare":
        TH_SNARE = np.mean(max_list) * 0.7
    elif drum_name == "Hi-hat":
        TH_HIHAT = np.mean(max_list) * 0.7

    print(f"Finished calibrating {drum_name} Drum.")


"""
Calibration Steps: 
    1. audio input until keyboard inturrupt
    2. 3 chunks of loop for bass, snare, hihat
    3. during each loop, I need to record the max magnitude of each drum
        - range of frequencies around peak magnitue frequency
    4. number of peaks and distance between two peaks could be taken into the acount
        - keep track of number of peaks and their positions
        - number of peaks could be enough?
"""

# Calibration for Bass Drum
calibrate_drum("Bass", BASS_DRUM_FREQ_RANGE, peak_threshold_bass, max_bass)
print(f"Bass Drum adjusted threshold: {TH_BASS}")


# Calibration for Snare Drum
calibrate_drum("Snare", SNARE_DRUM_FREQ_RANGE, peak_threshold_snare, max_snare)
print(f"Snare Drum adjusted threshold: {TH_SNARE}")


# Calibration for Hi-hat Drum
calibrate_drum("Hi-hat", HI_HAT_FREQ_RANGE, peak_threshold_hihat, max_hihat)
print(f"Hi-hat Drum adjusted threshold: {TH_HIHAT}")


# After calibration, ask use to press space bar to start the detection
input = input("Press Enter to start drum detection...")

# Main loop
print("Drum pattern detection started. Press Ctrl+C to stop.")
try:
    while True:
        # Read raw audio data
        raw_data = stream.read(CHUNK, exception_on_overflow=False)
        # Convert raw data to NumPy array
        data = np.frombuffer(raw_data, dtype=np.int8)

        data_fft = np.abs(fft.fft(data))
        data_fft = data_fft[: CHUNK // 2]
        # Find the maximum frequency component
        max_index = np.argmax(data_fft)
        frequency = max_index * RATE / CHUNK

        bass_index = (
            BASS_DRUM_FREQ_RANGE[0] * CHUNK // RATE,
            BASS_DRUM_FREQ_RANGE[1] * CHUNK // RATE,
        )
        snare_index = (
            SNARE_DRUM_FREQ_RANGE[0] * CHUNK // RATE,
            SNARE_DRUM_FREQ_RANGE[1] * CHUNK // RATE,
        )
        hihat_index = (
            HI_HAT_FREQ_RANGE[0] * CHUNK // RATE,
            HI_HAT_FREQ_RANGE[1] * CHUNK // RATE,
        )

        bass_fft = data_fft[bass_index[0] : bass_index[1]]
        snare_fft = data_fft[snare_index[0] : snare_index[1]]
        hihat_fft = data_fft[hihat_index[0] : hihat_index[1]]

        # Find the peak frequency in each drum's frequency range
        bass_peak = np.argmax(bass_fft)
        snare_peak = np.argmax(snare_fft)
        hi_hat_peak = np.argmax(hihat_fft)

        """
        if max(bass_fft) > max_bass:
            max_bass = max(bass_fft)
        if max(snare_fft) > max_snare:
            max_snare = max(snare_fft)
        if max(hihat_fft) > max_hihat:
            max_hihat = max(hihat_fft)
        """

        triggered = False
        # Check if the peak magnitude exceeds a threshold
        if bass_fft[bass_peak] > TH_BASS:
            print("*****Bass drum hit detected*****")
            triggered = True

        if snare_fft[snare_peak] > TH_SNARE:
            print("*****Snare drum hit detected*****")
            triggered = True

        if hihat_fft[hi_hat_peak] > TH_HIHAT:
            print("*****Hi-hat hit detected*****")
            triggered = True

        if triggered:
            print("")

except KeyboardInterrupt:
    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # print("\nrecorded max bass magnitude: ", max_bass)
    # print("recorded max snare magnitude: ", max_snare)
    # print("recorded max hihat magnitude: ", max_hihat)
    keyboard.unhook_all()
    print("\nExiting the program.")

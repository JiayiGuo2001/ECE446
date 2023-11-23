import pyaudio
import numpy as np
import numpy.fft as fft
from scipy.signal import butter, lfilter

# Define the frequency ranges for different drums
BASS_DRUM_FREQ_RANGE = (50, 100)  # Bass drum typically in 50-100 Hz
SNARE_DRUM_FREQ_RANGE = (160, 220)  # Snare drum typically in 200-220 Hz
HI_HAT_FREQ_RANGE = (300, 500)  # Hi-hat typically in 300-500 Hz

"""
1. audio input until keyboard inturrupt
2. 3 chunks of loop for bass, snare, hihat
3. during each loop, I need to record the max magnitude of each drum
    - range of frequencies around peak magnitue frequency
4. number of peaks and distance between two peaks could be taken into the acount
    - keep track of number of peaks and their positions
    - number of peaks could be enough?
"""


# Define Thresholds for different drums based on prior investigation.
TH_BASS = 3.2e5
TH_SNARE = 2.5e6
TH_HIHAT = 0.4e7


"""
# Butterworth bandpass filter setup
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return b, a


def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y
"""


# Initialize PyAudio
p = pyaudio.PyAudio()

# Audio stream parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
sample_time = 0.1
CHUNK = int(RATE * sample_time)

# Start the audio stream
stream = p.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
)

print("Drum pattern detection started. Press Ctrl+C to stop.")

max_bass = 0
max_snare = 0
max_hihat = 0

try:
    while True:
        # Read raw audio data
        raw_data = stream.read(CHUNK, exception_on_overflow=False)
        # Convert raw data to NumPy array
        data = np.frombuffer(raw_data, dtype=np.int16)

        data_fft = np.abs(fft.fft(data))
        data_fft = data_fft[: CHUNK // 2]
        # Find the maximum frequency component
        max_index = np.argmax(data_fft)
        frequency = max_index * RATE / CHUNK

        # print("\nFrequency: {:.2f} Hz".format(frequency))
        # print("\nMagnitude: ", data_fft[max_index])

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

        """
        # Bandpass filter data for each drum
        bass_data = bandpass_filter(data, *BASS_DRUM_FREQ_RANGE, RATE)
        snare_data = bandpass_filter(data, *SNARE_DRUM_FREQ_RANGE, RATE)
        hi_hat_data = bandpass_filter(data, *HI_HAT_FREQ_RANGE, RATE)

        # Perform FFT and get the magnitudes
        bass_fft = np.abs(fft.fft(bass_data))
        snare_fft = np.abs(fft.fft(snare_data))
        hi_hat_fft = np.abs(fft.fft(hi_hat_data))
        
        """

        # Find the peak frequency in each drum's frequency range
        bass_peak = np.argmax(bass_fft)
        snare_peak = np.argmax(snare_fft)
        hi_hat_peak = np.argmax(hihat_fft)

        if max(bass_fft) > max_bass:
            max_bass = max(bass_fft)
        if max(snare_fft) > max_snare:
            max_snare = max(snare_fft)
        if max(hihat_fft) > max_hihat:
            max_hihat = max(hihat_fft)

        # print("\nBass drum peak magnitude: ", bass_fft[bass_peak])
        # print("Snare drum peak magnitude: ", snare_fft[snare_peak])
        # print("Hi-hat peak magnitude: ", hihat_fft[hi_hat_peak])

        # Check if the peak magnitude exceeds a threshold
        if bass_fft[bass_peak] > TH_BASS:  # This threshold value can be adjusted
            print("Bass drum hit detected")
            print("\n****Bass drum magnitude: ", bass_fft[bass_peak])
        if snare_fft[snare_peak] > TH_SNARE:  # This threshold value can be adjusted
            print("Snare drum hit detected")
            print("\n****Snare drum magnitude: ", snare_fft[snare_peak])
        if hihat_fft[hi_hat_peak] > TH_HIHAT:  # This threshold value can be adjusted
            print("Hi-hat hit detected")
            print("\n****Hi-hat magnitude: ", hihat_fft[hi_hat_peak])


except KeyboardInterrupt:
    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("\nrecorded max bass magnitude: ", max_bass)
    print("recorded max snare magnitude: ", max_snare)
    print("recorded max hihat magnitude: ", max_hihat)
    print("\nExiting the program.")

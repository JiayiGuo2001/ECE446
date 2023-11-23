import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import os

# This will print the current working directory
print("Current Working Directory:", os.getcwd())

sample_rate, data = wavfile.read("bass.wav")

# If stereo, convert to mono by averaging the channels
if data.ndim > 1:
    data = np.mean(data, axis=1)

# Compute the FFT of the signal
fft_result = np.fft.fft(data)
fft_magnitude = np.abs(fft_result)

# Generate frequency bins
freqs = np.fft.fftfreq(len(fft_magnitude), d=1 / sample_rate)

# Plot only the frequencies in range 0 - 600 Hz
# Since the FFT output and frequency bins are symmetrical, take the first half
half_n = len(freqs) // 2
plt.figure(figsize=(12, 6))
plt.plot(freqs[:half_n], fft_magnitude[:half_n])
plt.xlim(0, 600)
plt.title("Frequency Spectrum of Drum Beat")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid()
plt.show()

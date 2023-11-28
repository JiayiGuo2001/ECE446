import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from numpy.fft import rfft, rfftfreq

# Audio parameters
END = False
audio_fmt = pyaudio.paInt8
channel_num = 1
sample_rate = 2200
sample_interval = 1 / sample_rate
sample_time = 0.1
chunk = int(sample_time / sample_interval)

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(
    format=audio_fmt,
    channels=channel_num,
    rate=sample_rate,
    input=True,
    frames_per_buffer=chunk,
)


# Key press event handler
def on_press(event):
    global END
    if event.key == "q":
        plt.close()
        stream.stop_stream()
        stream.close()
        p.terminate()
        END = True


x_lim = sample_rate // 2
# Plotting setup
mpl.rcParams["toolbar"] = "None"
fig, ax = plt.subplots(figsize=(12, 3))
fig.canvas.mpl_connect("key_press_event", on_press)
plt.subplots_adjust(left=0.05, top=0.95, right=0.95, bottom=0.05)
plt.get_current_fig_manager().set_window_title("Spectrum")
freq = rfftfreq(chunk, d=sample_interval)
y_data = np.zeros_like(freq)
(line,) = ax.step(freq, y_data, where="mid", color="#C04851")
ax.set_xlim(0, x_lim)
ax.set_ylim(0, 5)
ax.set_xticks(np.arange(0, x_lim, 50))
ax.set_yticks(np.arange(0, 5, 1))
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Amplitude")
plt.grid(True, linestyle="-.", color="#C04851", alpha=0.3)  # 设置网格

plt.ion()
plt.show()

# Main loop
try:  # Use try-except to catch KeyboardInterrupt
    while not END:
        data = stream.read(chunk, exception_on_overflow=False)
        data = np.frombuffer(data, dtype=np.int8)
        X = rfft(data)
        y_data = np.abs(X) * 0.01
        line.set_ydata(y_data)
        fig.canvas.draw_idle()  # Redraw the figure
        plt.pause(0.01)

    # Cleanup
    plt.close()
    stream.stop_stream()
    stream.close()
    p.terminate()

except KeyboardInterrupt:
    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()
    p.terminate()

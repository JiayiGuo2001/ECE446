[bass, Fs] = audioread('bass.wav');
duration = length(bass) / Fs;
n = length(bass);

t = 0 : 1/Fs : duration - 1/Fs;

bass_fft = abs(fft(bass));

f = (0:n-1)*(Fs/n);

plot(f, bass_fft);
xlim([0 200])
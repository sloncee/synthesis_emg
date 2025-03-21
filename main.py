import numpy as np
import matplotlib.pyplot as plt

def gaussian_derivative(t, sigma, amplitude):
    return - (t / sigma ** 2) * np.exp(-t ** 2 / (2 * sigma ** 2)) * amplitude

def noise(signal):
    noise = np.zeros_like(signal)
    num_intervals = np.random.randint(200, 500)
    for _ in range(num_intervals):
        std = np.random.uniform(0.03, 0.05)
        window_size = np.random.randint(10, 20)
        start = np.random.randint(0, len(signal) - window_size)
        noise[start:start + window_size] = np.random.normal(0, std, size=window_size)
    return noise

def synthesis_emg(duration, start_time, num_peaks):
    ticks = np.arange(0, duration, 1)
    signal = np.zeros_like(ticks, dtype=float)

    for _ in range(num_peaks):
        peak_position = np.random.randint(start_time, duration)
        amplitude = np.random.uniform(0.5, 1.5)
        sigma = np.random.uniform(5, 50)

        time_range = np.arange(- 3 * sigma, 3 * sigma, 1)
        if peak_position + len(time_range) < len(signal):
            signal[peak_position:peak_position + len(time_range)] += gaussian_derivative(time_range, sigma, amplitude)


    signal += noise(signal)
    return signal


def save_emg(signal):
    np.savetxt("synthetic_emg.txt", signal, fmt="%.6f")

def draw_emg(signal):
    plt.figure(figsize=(12, 4))
    plt.plot(signal, label="Synthetic EMG", linewidth=1)
    plt.xlabel("Time (ms)")
    plt.ylabel("Amplitude")
    plt.title("Synthetic EMG Signal")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    signal = synthesis_emg(10000,2000, 5000)
    save_emg(signal)
    draw_emg(signal)
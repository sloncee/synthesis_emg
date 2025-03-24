import customtkinter as ctk
import tkinter.messagebox as messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from FloatSpinbox import FloatSpinbox


class CustomToolbar(NavigationToolbar2Tk):
    def set_message(self, message):
        # Переопределяем метод, чтобы панель не изменяла размер
        pass


def noise(signal):
    noise_std = 0.005
    noise = np.zeros_like(signal)
    num_noise_intervals = np.random.randint(100, 500)
    for _ in range(num_noise_intervals):
        noise_window_size = np.random.randint(10, 20)
        start = np.random.randint(0, len(signal) - noise_window_size)
        noise[start:start + noise_window_size] = np.random.normal(0, noise_std, size=noise_window_size)
    return noise


def gaussian_derivative(t, sigma, amplitude):
    return - (t / sigma ** 2) * np.exp(-t ** 2 / (2 * sigma ** 2)) * amplitude


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Synthetic EMG")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.configure(fg_color="#FFFFFF")

        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=2, column=0, sticky="ns")

        self.create_empty_plot()

        self.duration_label = ctk.CTkLabel(self.control_frame, text="Протяженность:")
        self.duration_label.grid(row=0, column=0)
        self.duration_spinbox = FloatSpinbox(self.control_frame, step_size=100, width=150)
        self.duration_spinbox.set(10000)
        self.duration_spinbox.grid(row=1, column=0)

        self.start_time_label = ctk.CTkLabel(self.control_frame, text="Время старта:")
        self.start_time_label.grid(row=0, column=1)
        self.start_time_spinbox = FloatSpinbox(self.control_frame, step_size=100, width=150)
        self.start_time_spinbox.set(2000)
        self.start_time_spinbox.grid(row=1, column=1)

        self.num_peaks_label = ctk.CTkLabel(self.control_frame, text="Кол-во пиков:")
        self.num_peaks_label.grid(row=0, column=2)
        self.num_peaks_spinbox = FloatSpinbox(self.control_frame, step_size=100, width=150)
        self.num_peaks_spinbox.set(5000)
        self.num_peaks_spinbox.grid(row=1, column=2)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=3, column=0, sticky="ns")

        self.show_button = ctk.CTkButton(self.button_frame, text="Показать график", command=self.synthesis_emg_plot)
        self.show_button.grid(row=0, column=0)

        self.save_button = ctk.CTkButton(self.button_frame, text="Сохранить", command=self.save_emg)
        self.save_button.grid(row=0, column=1)

        # Относительный размер
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def create_empty_plot(self):
        self.fig, self.graph = plt.subplots(figsize=(12, 4))
        self.graph.set_title("Пустой график")
        self.graph.set_xlabel("X")
        self.graph.set_ylabel("Y")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.toolbar = CustomToolbar(self.canvas, self, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=1, column=0)


    def synthesis_emg_plot(self):
        duration = self.duration_spinbox.get()
        num_peaks = self.num_peaks_spinbox.get()
        start_time = self.start_time_spinbox.get()

        try:
            duration = int(duration)
            num_peaks = int(num_peaks)
            start_time = int(start_time)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числа")
            return

        ticks = np.arange(0, duration, 1)
        self.signal = np.zeros_like(ticks, dtype=float)

        for _ in range(num_peaks):
            peak_position = np.random.randint(start_time, duration)
            amplitude = np.random.uniform(0.5, 1.5)
            sigma = np.random.uniform(5, 50)

            time_range = np.arange(- 3 * sigma, 3 * sigma, 1)
            if peak_position + len(time_range) < len(self.signal):
                self.signal[peak_position:peak_position + len(time_range)] += gaussian_derivative(time_range, sigma,
                                                                                             amplitude)

        self.signal += noise(self.signal)

        self.graph.clear()
        self.graph.plot(self.signal, label="Synthetic EMG", linewidth=1)
        self.graph.set_title("Синтез ЭМГ")
        self.graph.set_xlabel("Time (ms)")
        self.graph.set_ylabel("Amplitude")
        self.graph.legend()
        self.graph.grid()
        self.canvas.draw()

    def save_emg(self):
        if self.signal is not None:
            np.savetxt("synthetic_emg.txt", self.signal, fmt="%.6f")
            messagebox.showinfo("Успех", "Данные сохранены в synthetic_emg.txt")
        else:
            messagebox.showerror("Ошибка", "Нет данных для сохранения")

    def on_close(self):
        plt.close(self.fig)
        self.quit()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()

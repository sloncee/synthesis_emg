import os
import threading
import time

import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from FloatSpinbox import FloatSpinbox
from Synthetic_EMG import gaussian_derivative, noise

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class CustomToolbar(NavigationToolbar2Tk):
    def set_message(self, message):
        # Переопределяем метод, чтобы панель не изменяла размер
        pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.signal = None
        self.title("Synthetic EMG")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.configure(fg_color="#FFFFFF")

        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=2, column=0, sticky="ns")

        self.create_empty_plot()

        menubar = tk.Menu(self, tearoff=0)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть файл", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=lambda: self.save_emg(self.duration_spinbox.get(),
                                                                               self.start_time_spinbox.get(),
                                                                               self.num_peaks_spinbox.get(), True))

        menubar.add_cascade(label="Файл", menu=file_menu)
        self.config(menu=menubar)

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

        self.save_count_label = ctk.CTkLabel(self.control_frame, text="Файлов для генерации:")
        self.save_count_label.grid(row=0, column=3)
        self.save_count_spinbox = FloatSpinbox(self.control_frame, step_size=100, width=150)
        self.save_count_spinbox.set(500)
        self.save_count_spinbox.grid(row=1, column=3)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=3, column=0, sticky="ns")

        self.show_button = ctk.CTkButton(self.button_frame, text="Показать график", command=self.synthesis_emg_plot)
        self.show_button.grid(row=0, column=0)

        self.save_button = ctk.CTkButton(self.button_frame, text="Сохранить несколько",
                                         command=self.save_several_emg)
        self.save_button.grid(row=0, column=2)

        self.save_button_param = ctk.CTkButton(self.button_frame, text="Сохранить несколько с параметрами",
                                               command=self.save_several_emg_param)
        self.save_button_param.grid(row=0, column=3)

        self.progressbar = ctk.CTkProgressBar(self)
        self.progressbar.set(0)
        self.progressbar.grid(row=4, column=0, sticky="ew")

        # Относительный размер
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def open_file(self):
        file_path = ctk.filedialog.askopenfile()
        data = np.loadtxt(file_path)

        x = np.arange(len(data))

        self.graph.plot(x, data, label="Synthetic EMG", linewidth=1)
        self.graph.set_title("Синтез ЭМГ")
        self.graph.set_xlabel("Time (ms)")
        self.graph.set_ylabel("Amplitude")
        self.graph.legend()
        self.graph.grid()
        self.canvas.draw()

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

    def construct_emg(self, duration, start_time, num_peaks):

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

        self.construct_emg(duration, start_time, num_peaks)

        self.graph.clear()
        self.graph.plot(self.signal, label="Synthetic EMG", linewidth=1)
        self.graph.set_title("Синтез ЭМГ")
        self.graph.set_xlabel("Time (ms)")
        self.graph.set_ylabel("Amplitude")
        self.graph.legend()
        self.graph.grid()
        self.canvas.draw()

    def save_emg(self, duration, start_time, num_peaks, mbox, directory=None, counter=0):
        if self.signal is None:
            messagebox.showinfo("Успех", "Нет данных для сохранения")
            return
        if not directory:
            directory = ctk.filedialog.askdirectory()  # Запрашиваем директорию, если не указана
            if not directory:
                return

        fname = os.path.join(directory, f"{duration}_{start_time}_{num_peaks}_emg.txt")
        while os.path.exists(fname):
            fname = os.path.join(directory, f"{duration}_{start_time}_{num_peaks}_emg({counter}).txt")
            counter += 1
        if self.signal is not None:
            np.savetxt(fname, self.signal, fmt="%.6f")
            if mbox:
                messagebox.showinfo("Успех", "Данные сохранены \n" + fname)
        elif mbox:
            messagebox.showerror("Ошибка", "Ошибка сохранения")

    def save_several_emg(self):
        directory = ctk.filedialog.askdirectory()

        if not directory:
            return

        def save_thread():
            save_count = int(self.save_count_spinbox.get())
            try:

                for i in range(0, save_count + 1):
                    duration = int(self.duration_spinbox.get())
                    start_time = int(self.start_time_spinbox.get())
                    num_peaks = int(self.num_peaks_spinbox.get())

                    self.progressbar.set(i / save_count)

                    self.construct_emg(duration, start_time, num_peaks)
                    self.save_emg(duration, start_time, num_peaks, False, directory)
                self.progressbar.stop()
                messagebox.showinfo("Успех", "Все файлы сохранены!")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректные значения параметров")

        threading.Thread(target=save_thread, daemon=True).start()

    def save_several_emg_param(self):

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        settings_window = ctk.CTkToplevel(self)
        settings_window.title("save several EMG")
        settings_window.geometry("500x400")

        settings_window.grab_set()

        settings_window.grid_columnconfigure(0, weight=1)
        settings_window.grid_rowconfigure(0, weight=1)  # Для фрейма "От"
        settings_window.grid_rowconfigure(1, weight=1)  # Для фрейма "До"
        settings_window.grid_rowconfigure(2, weight=1)  # Для фрейма "Шаг"
        settings_window.grid_rowconfigure(3, weight=0)  # Для кнопки (фиксированная высота)
        settings_window.grid_rowconfigure(4, weight=0)  # Для полосы прогресса

        # Фрейм "От"
        frame_from = ctk.CTkFrame(settings_window)
        frame_from.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame_from.grid_columnconfigure((0, 1, 2), weight=1)
        frame_from.grid_rowconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(frame_from, text="Параметры ОТ", font=("Arial", 14, "bold")).grid(row=0, columnspan=3, pady=5)

        # Протяженность ОТ
        ctk.CTkLabel(frame_from, text="Протяженность:").grid(row=1, column=0, padx=5, sticky="w")
        spinbox_from_duration = FloatSpinbox(frame_from, step_size=100, width=150)
        spinbox_from_duration.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        spinbox_from_duration.set(1000)

        # Время старта ОТ
        ctk.CTkLabel(frame_from, text="Время старта:").grid(row=1, column=1, padx=5, sticky="w")
        spinbox_from_start = FloatSpinbox(frame_from, step_size=100, width=150)
        spinbox_from_start.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        spinbox_from_start.set(10)

        # Кол-во пиков ОТ
        ctk.CTkLabel(frame_from, text="Кол-во пиков:").grid(row=1, column=2, padx=5, sticky="w")
        spinbox_from_peaks = FloatSpinbox(frame_from, step_size=100, width=150)
        spinbox_from_peaks.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        spinbox_from_peaks.set(5000)

        # Фрейм "До"
        frame_to = ctk.CTkFrame(settings_window)
        frame_to.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame_to.grid_columnconfigure((0, 1, 2), weight=1)
        frame_to.grid_rowconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(frame_to, text="Параметры ДО", font=("Arial", 14, "bold")).grid(row=0, columnspan=3, pady=5)

        # Протяженность ДО
        ctk.CTkLabel(frame_to, text="Протяженность:").grid(row=1, column=0, padx=5, sticky="w")
        spinbox_to_duration = FloatSpinbox(frame_to, step_size=100, width=150)
        spinbox_to_duration.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        spinbox_to_duration.set(5000)

        # Время старта ДО
        ctk.CTkLabel(frame_to, text="Время старта:").grid(row=1, column=1, padx=5, sticky="w")
        spinbox_to_start = FloatSpinbox(frame_to, step_size=100, width=150)
        spinbox_to_start.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        spinbox_to_start.set(30)

        # Кол-во пиков ДО
        ctk.CTkLabel(frame_to, text="Кол-во пиков:").grid(row=1, column=2, padx=5, sticky="w")
        spinbox_to_peaks = FloatSpinbox(frame_to, step_size=100, width=150)
        spinbox_to_peaks.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        spinbox_to_peaks.set(10000)

        # Фрейм "Шаг"
        frame_step = ctk.CTkFrame(settings_window)
        frame_step.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        frame_step.grid_columnconfigure((0, 1, 2), weight=1)
        frame_step.grid_rowconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(frame_step, text="Шаг", font=("Arial", 14, "bold")).grid(row=0, columnspan=3, pady=5)

        # Протяженность ШАГ
        ctk.CTkLabel(frame_step, text="Шаг протяженности:").grid(row=1, column=0, padx=5, sticky="w")
        spinbox_step_duration = FloatSpinbox(frame_step, step_size=100, width=150)
        spinbox_step_duration.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        spinbox_step_duration.set(500)

        # Время старта ШАГ
        ctk.CTkLabel(frame_step, text="Шаг времени старта:").grid(row=1, column=1, padx=5, sticky="w")
        spinbox_step_start = FloatSpinbox(frame_step, step_size=100, width=150)
        spinbox_step_start.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        spinbox_step_start.set(5)

        # Кол-во пиков ШАГ
        ctk.CTkLabel(frame_step, text="Шаг кол-ва пиков:").grid(row=1, column=2, padx=5, sticky="w")
        spinbox_step_peaks = FloatSpinbox(frame_step, step_size=100, width=150)
        spinbox_step_peaks.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        spinbox_step_peaks.set(500)

        save_path_var = ctk.StringVar(value="")

        def browse_directory():
            directory = ctk.filedialog.askdirectory()
            if directory:
                save_path_var.set(directory)
                write_emg_param()

        def write_emg_param():
            if not save_path_var.get():
                messagebox.showerror("Ошибка", "Сначала выберите директорию")
                return

            progressbar.start()
            current_file = 0

            try:
                # Получаем значения из спинбоксов
                from_dur = int(spinbox_from_duration.get())
                to_dur = int(spinbox_to_duration.get())
                step_dur = int(spinbox_step_duration.get())

                from_start = int(spinbox_from_start.get())
                to_start = int(spinbox_to_start.get())
                step_start = int(spinbox_step_start.get())

                from_peaks = int(spinbox_from_peaks.get())
                to_peaks = int(spinbox_to_peaks.get())
                step_peaks = int(spinbox_step_peaks.get())

                total_files = self.calculate_total_files(
                    from_dur, to_dur, step_dur,
                    from_start, to_start, step_start,
                    from_peaks, to_peaks, step_peaks
                )

                # Сохраняем файлы
                for i in range(from_dur, to_dur + 1, step_dur):
                    for j in range(from_start, to_start + 1, step_start):
                        for k in range(from_peaks, to_peaks + 1, step_peaks):
                            self.construct_emg(i, j, k)
                            current_file += 1
                            progressbar.set(current_file / total_files)
                            self.save_emg(i, j, k, False, save_path_var.get())
                            settings_window.update()
                progressbar.stop()
                messagebox.showinfo("Успех", "Все файлы сохранены!")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректные значения параметров")
            settings_window.destroy()

        progressbar = ctk.CTkProgressBar(settings_window)
        progressbar.set(0)
        progressbar.grid(row=4, column=0, sticky="ew")

        # Кнопка сохранения (ниже всех фреймов)
        save_button = ctk.CTkButton(settings_window, text="Сохранить", command=browse_directory)
        save_button.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

    def calculate_total_files(self,
                              from_dur, to_dur, step_dur,
                              from_start, to_start, step_start,
                              from_peaks, to_peaks, step_peaks
                              ):
        def count_steps(from_val, to_val, step):
            if step == 0 or from_val > to_val:
                return 0
            return (to_val - from_val) // step + 1

        dur_steps = count_steps(from_dur, to_dur, step_dur)
        start_steps = count_steps(from_start, to_start, step_start)
        peaks_steps = count_steps(from_peaks, to_peaks, step_peaks)

        return dur_steps * start_steps * peaks_steps

    def on_close(self):
        plt.close(self.fig)
        self.quit()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()

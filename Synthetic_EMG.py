import os
import threading
import time

import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk



def noise(signal):
    noise = np.zeros_like(signal)
    num_intervals = np.random.randint(200, 500)
    for _ in range(num_intervals):
        std = np.random.uniform(0.03, 0.05)
        window_size = np.random.randint(10, 20)
        start = np.random.randint(0, len(signal) - window_size)
        noise[start:start + window_size] = np.random.normal(0, std, size=window_size)
    return noise


def gaussian_derivative(t, sigma, amplitude):
    return - (t / sigma ** 2) * np.exp(-t ** 2 / (2 * sigma ** 2)) * amplitude



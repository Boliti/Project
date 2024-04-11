# Подключение библиотек
import numpy as np
import os
import random
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve
from scipy.signal import savgol_filter
from scipy import sparse
from tkinter import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from time import perf_counter

from scipy.signal import find_peaks


# Функции удаления базовой линии
# Функция нахождения БЛ
def baseline_als(amplitudes, lam, p, niter=10):
    L = len(amplitudes)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    w = np.ones(L)
    for i in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + float(lam) * D.dot(D.transpose())
        z = spsolve(Z, w * amplitudes)
        w = p * (amplitudes > z) + (1 - p) * (amplitudes < z)
    return z
# Функция удаления БЛ
def delet_BaseLime(amplitudes_list):
    lam = float(entry3.get())
    p = float(entry4.get())
    amplitudesBL_list = []
    for amplitudes in amplitudes_list:
        baseline = baseline_als(amplitudes, lam, p)
        cleaned_spectrum = amplitudes - baseline
        amplitudesBL_list.append(cleaned_spectrum)
    return amplitudesBL_list

# Строительтво графика на экране.
def bilding(frequencies_list, amplitudes_list):
    global new_flag, frame, root
    if new_flag:
        frame.destroy()
    frame = tk.Frame(root)
    frame.pack()

    # frame.pack_propagate(False)
    fig = Figure(figsize=(11.5, 7.9))
    ax = fig.add_subplot()
    for i in range(len(amplitudes_list)):
        ax.plot(frequencies_list[i], amplitudes_list[i], alpha=0.5)
        if find_flag:
            peaks, _ = find_peaks(amplitudes_list[i], width=10, prominence=10)
            ax.plot(frequencies_list[i][peaks], amplitudes_list[i][peaks], 'ro')
            for j in range(len(peaks)):
                ax.text(frequencies_list[i][peaks[j]], amplitudes_list[i][peaks[j]], f'({frequencies_list[i][peaks[j]]:.2f},\n {amplitudes_list[i][peaks[j]]:.2f})', fontsize=8)    


    ax.set_xlabel('Рамановский сдвиг, см^-1')
    ax.set_ylabel('Интенсивность')
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, frame)
    toolbar.update()
    new_flag = True

# Функция средней спектрограммы
def averages_spectrum(averaged):
    averaged2 = []
    averaged = np.mean(np.array(averaged), axis=0)
    averaged2.append(averaged)
    return averaged2

# Функция выбора полосы частот
def selection(freq_list, ampl_list):
    min_freq = entry1.get()
    max_freq = entry2.get()
    if min_freq == "min_freq":
        min_freq = 0
    else:
        min_freq = float(entry1.get())
    if max_freq == "max_freq":
        max_freq = 10000
    else:
        max_freq = float(entry2.get())
    freq_list2 = []
    ampl_list2 = []
    for freq, ampl in zip(freq_list, ampl_list):
        mask = (freq >= min_freq) & (freq <= max_freq)
        if np.any(mask):
            freq_list2.append(freq[mask])
            ampl_list2.append(ampl[mask])
    return freq_list2, ampl_list2

# Сглаживание сигнала
# Сглаживания сигнала методом savgol_filter
def savgol_def(spectrum_list):
    spectrum_list2 = []
    window_length = int(entry5.get())
    polyorder = int(entry6.get())
    
    for i in range(len(spectrum_list)):
        spectrum_list[i] = savgol_filter(spectrum_list[i], window_length, polyorder)
        spectrum_list2.append(spectrum_list[i])
    return spectrum_list2

# Сглаживание сигнала методом средней скользящей
def moving_average_smoothing(spectrum):
    window_size = int(entry5.get())
    if window_size % 2 == 0:
        raise ValueError("Размер окна сглаживания должен быть нечетным числом")
    if window_size < 1:
        raise ValueError("Размер окна сглаживания должен быть больше нуля")
    smoothed_spectrum = np.zeros_like(spectrum)
    half_window = window_size // 2
    for i in range(half_window, len(spectrum) - half_window):
        window = spectrum[i - half_window:i + half_window + 1]
        smoothed_spectrum[i] = np.mean(window)
    # сглаживание краев спектра
    smoothed_spectrum[:half_window] = np.mean(spectrum[:window_size])
    smoothed_spectrum[-half_window:] = np.mean(spectrum[-window_size:])

    return smoothed_spectrum

# Нормализация
# Нормализация спектра методом SNV
def normalize_spectrum_snv(spectrum_list):
    normalized_spectrum = []
    for i in range(len(spectrum_list)):
        mean_spectrum = np.mean(spectrum_list[i])
        std_spectrum = np.std(spectrum_list[i])
        normalized = (spectrum_list[i] - mean_spectrum) / std_spectrum
        normalized_spectrum.append(normalized)
    return normalized_spectrum

# Нормализацию значений списка относительно их максимального значения
def normal(list):
    list = np.array(list)
    max = np.max(list)
    for i in range(len(list)):
        list[i] /= max
    return (list)
def normalized(spectrum_list):
    amplit_LIST = [0] * len(spectrum_list)
    for a in range(len(spectrum_list)):
        amplit_LIST[a] = normal(spectrum_list[a])
    return amplit_LIST

# Строительство по нажатию
def get_input():
    global remove_flag, average_flag, amplitudes_list, frequencies_list
    timer = perf_counter()
    amplit_LIST = amplitudes_list
    freque_LIST = frequencies_list
    if selection_flag:
        freque_LIST, amplit_LIST = selection(freque_LIST, amplit_LIST)
    if savgol_filter_flag:
        amplit_LIST = savgol_def(amplit_LIST)
    if moving_average_smoothing_flag:
        for i in range(len(amplit_LIST)):
            amplit_LIST[i] = moving_average_smoothing(amplit_LIST[i])
    if remove_flag:
        amplit_LIST = delet_BaseLime(amplit_LIST)
    if normalize_flag:
        amplit_LIST = normalized(amplit_LIST)
    if normalize_snv_flag:
        amplit_LIST = normalize_spectrum_snv(amplit_LIST)
    if average_flag:
        amplit_LIST = averages_spectrum(amplit_LIST)
        freque_LIST = averages_spectrum(freque_LIST)

    bilding(freque_LIST, amplit_LIST)
    print(perf_counter() - timer)




# открытие файла
def open_folder():
    global frequencies_list, amplitudes_list
    frequencies_list = []
    amplitudes_list = []
    root = tk.Tk()
    root.withdraw()
    folderpath = filedialog.askopenfilenames(title="Выберите файлы", filetypes=(
    ("ESP files", "*.esp"), ("Text files", "*.txt"), ("All files", "*.*")))
    if folderpath:
        time = perf_counter()
        for path in folderpath:
            data = np.genfromtxt(path, skip_header=1)
            frequencies_list.append(data[:, 0])
            amplitudes_list.append(data[:, 1])
        bilding(frequencies_list, amplitudes_list)
    else:
        messagebox.showwarning("Предупреждение", "Файлы не выбраны.")

    print(perf_counter() - time)


# выбор действия# выбор действия
def actions1():
    global remove_flag, frame
    remove_flag = not remove_flag


def actions2():
    global find_flag, frame, average_flag
    average_flag = not average_flag



def actions3():
    global find_flag, frame, average_flag
    find_flag = not find_flag



def actions4():
    global normalize_flag
    normalize_flag = not normalize_flag


def actions5():
    global normalize_snv_flag
    normalize_snv_flag = not normalize_snv_flag

def actions6():
    global savgol_filter_flag
    savgol_filter_flag = not savgol_filter_flag

def actions7():
    global moving_average_smoothing_flag
    moving_average_smoothing_flag = not moving_average_smoothing_flag

# пропадает надпись на поле ввода
def on_entry_click(event):
    entry = event.widget
    if entry.get() in ["min_freq", "max_freq"]:
        entry.delete(0, tk.END)


# Удаление данных
def clear_data():
    global amplitudes_list, frequencies_list, remove_flag, find_flag
    amplitudes_list = []
    frequencies_list = []
    frame.destroy()

# Объявление основных флагов
normalize_snv_flag = False
savgol_filter_flag = False
remove_flag = False
find_flag = False
bild_flag = False
new_flag = False
average_flag = False
selection_flag = True
normalize_flag = False
moving_average_smoothing_flag = False

# Создание окна
root = tk.Tk()
root.title("Spectrum")
root.state('zoomed')

# Устанавливаем размеры и положение окна на полный экран
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.attributes("-fullscreen", True)
root.geometry(f"{screen_width}x{screen_height}+0+0")


def show_message():
    messagebox.showinfo("Сообщение", "Спасение утопающих – дело рук самих утопающих")


# Панель инструментов
mainmenu = tk.Menu(root)
root.config(menu=mainmenu)
# Открытие файла с
filemenu = tk.Menu(mainmenu, tearoff=0)
filemenu.add_command(label="Открыть файлы", command=open_folder)
filemenu.add_command(label="Сохранить...")
filemenu.add_separator()
filemenu.add_command(label="Выход", command=lambda: root.destroy())
# Помощь
helpmenu = tk.Menu(mainmenu, tearoff=0)
helpmenu.add_command(label="Помощь", command=show_message)
helpmenu.add_command(label="О программе")

building = tk.Menu(mainmenu, tearoff=0)
building.add_command(label="Построить график", command=get_input)
building.add_command(label="Очистить данные о файле", command=clear_data)
# Поле ввода 1

# Создаем метку (Label) с текстом
label = tk.Label(root, text="lam:", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=140)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="p:", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=160)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="min:", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=50)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="max:", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=70)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="wlen:", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=283)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="poly:", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=303)
#Поле ввода 1 и 2
# Поле ввода 1 (min_freq)
entry1 = tk.Entry(root)
entry1.insert(0, "min_freq")
entry1.bind("<FocusIn>", on_entry_click)
entry1.pack()
entry1.place(x=40, y=50)
# Поле ввода 2 (max_freq)
entry2 = tk.Entry(root)
entry2.insert(0, "max_freq")
entry2.bind("<FocusIn>", on_entry_click)
entry2.pack()
entry2.place(x=40, y=70)
# Поле ввода 3 (lam)
entry3 = tk.Entry(root)
entry3.insert(0, "1000")
entry3.bind("<FocusIn>", on_entry_click)
entry3.pack()
entry3.place(x=40, y=142)
# Поле ввода 4 (p)
entry4 = tk.Entry(root)
entry4.insert(0, "0.001")
entry4.bind("<FocusIn>", on_entry_click)
entry4.pack()
entry4.place(x=40, y=162)
# Поле ввода 4 (window_length)
entry5 = tk.Entry(root)
entry5.insert(0, "25")
entry5.bind("<FocusIn>", on_entry_click)
entry5.pack()
entry5.place(x=40, y=285)
# Поле ввода 4 (polyorder)
entry6 = tk.Entry(root)
entry6.insert(0, "2")
entry6.bind("<FocusIn>", on_entry_click)
entry6.pack()
entry6.place(x=40, y=305)


# Поле инструментов
mainmenu.add_cascade(label="Файл", menu=filemenu)
mainmenu.add_cascade(label="Справка", menu=helpmenu)

mainmenu.add_cascade(label="Действия над файлом", menu=building)
mainmenu.add_command(label="run", command=get_input)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="Функции и параметры", font=("Arial", 13))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=5)

label = tk.Label(root, text="Выбор полосы частот", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=26)

label = tk.Label(root, text="Удаление БЛ", font=("Arial", 11))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=95)

label = tk.Label(root, text="Нормировка", font=("Arial", 11))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=180)
label = tk.Label(root, text="Сглаживание", font=("Arial", 11))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=242)


checkbox_var = tk.IntVar()
checkbox = tk.Checkbutton(root, text="Метод BL_ALS", font=("Arial", 10), variable=checkbox_var, command=actions1)
checkbox.pack()
checkbox.place(x=5, y=115)

checkbox_var2 = tk.IntVar()
checkbox2 = tk.Checkbutton(root, text="Поиск пиков", variable=checkbox_var2, command=actions3)
checkbox2.pack()
checkbox2.place(x=5, y=360)

checkbox_var4 = tk.IntVar()
checkbox4 = tk.Checkbutton(root, text="Норм. методом SNV", variable=checkbox_var4, command=actions5)
checkbox4.pack()
checkbox4.place(x=5, y=200)

checkbox_var3 = tk.IntVar()
checkbox3 = tk.Checkbutton(root, text="Норм. по макс", variable=checkbox_var3, command=actions4)
checkbox3.pack()
checkbox3.place(x=5, y=220)

checkbox_var6 = tk.IntVar()
checkbox6 = tk.Checkbutton(root, text="Фильт. Савицкого-Голая", variable=checkbox_var6, command=actions6)
checkbox6.pack()
checkbox6.place(x=5, y=260)

checkbox_var8 = tk.IntVar()
checkbox8 = tk.Checkbutton(root, text="Метод ср. скользящей", variable=checkbox_var8, command=actions7)
checkbox8.pack()
checkbox8.place(x=5, y=322)

checkbox_var7 = tk.IntVar()
checkbox7 = tk.Checkbutton(root, text="Нахожение среднего", variable=checkbox_var7, command=actions2)
checkbox7.pack()
checkbox7.place(x=5, y=342)
# Создаем фрейм для размещения downbar
bottom_frame = tk.Frame(root, height=30, bg='lightgray')
bottom_frame.pack(side='bottom', fill='x')

# Отображаем версию tkinter на полосе
Program_version = 0.3472
version_label = tk.Label(bottom_frame, text=f"Program version: {Program_version}", bg='lightgray')
version_label.pack(side='right', padx=10)


root.mainloop()
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
    lam = entry3.get()
    p = entry4.get()
    if lam == "lam = 1000":
        lam = 1000
    else:
        lam = float(entry1.get())
    if p == "p = 0.001":
        p = 0.001
    else:
        p = float(entry2.get())
    amplitudesBL_list = []
    for amplitudes in amplitudes_list:
        baseline = baseline_als(amplitudes, lam, p)
        cleaned_spectrum = amplitudes - baseline
        amplitudesBL_list.append(cleaned_spectrum)
    return amplitudesBL_list

# Строительтво графика.
def bilding(frequencies_list, amplitudes_list):
    global new_flag, frame, root
    if new_flag:
        frame.destroy()
    frame = tk.Frame(root)
    frame.pack()

    # frame.pack_propagate(False)
    fig = Figure(figsize=(11.5, 7.9))
    ax = fig.add_subplot()
    print(len(amplitudes_list))
    print(len(frequencies_list))
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


def selection(freq_list, ampl_list):
    min_freq = entry1.get()
    max_freq = entry2.get()
    if min_freq == "min_freq":
        min_freq = 0
    else:
        min_freq = float(entry3.get())
    if max_freq == "max_freq":
        max_freq = 10000
    else:
        max_freq = float(entry4.get())
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
    """ Добавить поля ввода
    if window_length == "window_length":
        window_length = 25
    else:
        window_length = float(entry3.get())
    if polyorder == "polyorder":
        polyorder = 2
    else:
        polyorder = float(entry3.get())
        """
    window_length = 25
    polyorder = 2
    
    for i in range(len(spectrum_list)):
        spectrum_list[i] = savgol_filter(spectrum_list[i], window_length, polyorder)
        spectrum_list2.append(spectrum_list[i])
    return spectrum_list2

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
def normalized(list):
    amplit_LIST = [0] * len(list)
    for a in range(len(list)):
        amplit_LIST[a] = normal(list[a])
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


# Функция выбора цвета
def selection_color():
    r = np.random.random()
    g = np.random.random()
    b = np.random.random()
    return (0, g, b)


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


# выбор действия
def actions1():
    global remove_flag, frame
    remove_flag = not remove_flag
    if remove_flag:
        actions.entryconfigure(0, label="С удалением БЛ")
    else:
        actions.entryconfigure(0, label="Без удаления БЛ")


def actions2():
    global find_flag, frame, average_flag
    average_flag = not average_flag
    if average_flag:
        actions.entryconfigure(2, label="Со средними значениями")
    else:
        actions.entryconfigure(2, label="Без среднего значения")
        find_flag = False
        actions.entryconfigure(3, label="Без поиска пиков")


def actions3():
    global find_flag, frame, average_flag
    find_flag = not find_flag
    if find_flag:
        actions.entryconfigure(3, label="С поиском пиков")
        actions.entryconfigure(2, label="Со средними значениями")
        average_flag = True
    else:
        actions.entryconfigure(3, label="Без поиска пиков")


def actions4():
    global normalize_flag
    normalize_flag = not normalize_flag
    if normalize_flag:
        actions.entryconfigure(1, label="Нормализация")
    else:
        actions.entryconfigure(1, label="Без нормализации")


# пропадает надпись на поле ввода
def on_entry_click(event):
    entry = event.widget
    if entry.get() in ["lam = 1000", "p = 0.001", "min_freq", "max_freq"]:
        entry.delete(0, tk.END)


# Удаление данных
def clear_data():
    global amplitudes_list, frequencies_list, remove_flag, find_flag
    amplitudes_list = []
    frequencies_list = []
    find_flag = False
    frame.destroy()
    actions.entryconfigure(0, label="С удалением БЛ")
    actions.entryconfigure(1, label="Поиск пиков")

# Объявление основных флагов
# Нет кнопки
normalize_snv_flag = True
# Нет кнопки
savgol_filter_flag = True
remove_flag = False
find_flag = False
bild_flag = False
new_flag = False
average_flag = False
selection_flag = True
normalize_flag = False

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
# Действия над файлом
actions = tk.Menu(mainmenu, tearoff=0)
actions.add_command(label="Без удаления БЛ", command=actions1)
actions.add_command(label="Без нормировки", command=actions4)
actions.add_command(label="Без среднего значения", command=actions2)
actions.add_command(label="Без поиска пиков", command=actions3)

building = tk.Menu(mainmenu, tearoff=0)
building.add_command(label="Построить график", command=get_input)
building.add_command(label="Очистить данные о файле", command=clear_data)
# Поле ввода 1

# Создаем метку (Label) с текстом
label = tk.Label(root, text="lam:", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=135)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="p:", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=155)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="minf", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=55)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="maxf", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=75)

entry3 = tk.Entry(root)
entry3.insert(0, "lam = 1000")
entry3.bind("<FocusIn>", on_entry_click)
entry3.pack()
entry3.place(x=40, y=95)
# Поле ввода 2
entry4 = tk.Entry(root)
entry4.insert(0, "p = 0.001")
entry4.bind("<FocusIn>", on_entry_click)
entry4.pack()
entry4.place(x=40, y=115)
# Поле ввода 3
entry1 = tk.Entry(root)
entry1.insert(0, "min_freq")
entry1.bind("<FocusIn>", on_entry_click)
entry1.pack()
entry1.place(x=40, y=55)
# Поле ввода 4
entry2 = tk.Entry(root)
entry2.insert(0, "max_freq")
entry2.bind("<FocusIn>", on_entry_click)
entry2.pack()
entry2.place(x=40, y=75)
# Поле инструментов
mainmenu.add_cascade(label="Файл", menu=filemenu)
mainmenu.add_cascade(label="Справка", menu=helpmenu)
mainmenu.add_cascade(label="Действия", menu=actions)
mainmenu.add_cascade(label="Действия над файлом", menu=building)
mainmenu.add_command(label="run", command=get_input)

# Создаем метку (Label) с текстом
label = tk.Label(root, text="Функции и параметры", font=("Arial", 13))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=5)

label = tk.Label(root, text="Полоса частот", font=("Arial", 10))
label.pack()  # Размещаем метку на окне
label.place(x=5, y=25)

checkbox_var = tk.IntVar()
checkbox = tk.Checkbutton(root, text="baseline", font=("Arial", 10), variable=checkbox_var, command=actions1)
checkbox.pack()
checkbox.place(x=5, y=115)

checkbox_var2 = tk.IntVar()
checkbox2 = tk.Checkbutton(root, text="поиск пиков", variable=checkbox_var2, command=actions3)
checkbox2.pack()
checkbox2.place(x=5, y=190)

checkbox_var3 = tk.IntVar()
checkbox3 = tk.Checkbutton(root, text="нормировка", variable=checkbox_var3, command=actions4)
checkbox3.pack()
checkbox3.place(x=5, y=210)

# Создаем фрейм для размещения downbar
bottom_frame = tk.Frame(root, height=30, bg='lightgray')
bottom_frame.pack(side='bottom', fill='x')

# Отображаем версию tkinter на полосе
Program_version = 0.3472
version_label = tk.Label(bottom_frame, text=f"Program version: {Program_version}", bg='lightgray')
version_label.pack(side='right', padx=10)


root.mainloop()
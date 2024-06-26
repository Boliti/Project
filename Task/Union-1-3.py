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

# Функция удаления БЛ
def delet_BaseLime(amplitudes_list):
    lam = entry3.get()


# Строительтво графика на экране.
def bilding(frequencies_list, amplitudes_list):
    global new_flag, frame, root


# Функция средней спектрограммы
def averages_spectrum(averaged):
    averaged2 = []


# Функция выбора полосы частот
def selection(freq_list, ampl_list):
    min_freq = entry1.get()


# Сглаживание сигнала
# Сглаживания сигнала методом savgol_filter
def savgol_def(spectrum_list):
    spectrum_list2 = []


# Нормализация
# Нормализация спектра методом SNV
def normalize_spectrum_snv(spectrum_list):
    normalized_spectrum = []


# Нормализацию значений списка относительно их максимального значения
def normal(list):
    list = np.array(list)

def normalized(spectrum_list):
    amplit_LIST = [0] * len(spectrum_list)


# Строительство по нажатию
def get_input():
    global remove_flag, average_flag, amplitudes_list, frequencies_list
    timer = perf_counter()

    print(perf_counter() - timer)



# открытие файла
def open_folder():
  time = perf_counter()

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

def actions5():
    global normalize_snv_flag
    normalize_snv_flag = not normalize_snv_flag

def actions6():
    global savgol_filter_flag
    savgol_filter_flag = not savgol_filter_flag

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
normalize_snv_flag = False
# Нет кнопки
savgol_filter_flag = False
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
mainmenu.add_cascade(label="Действия", menu=actions)
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
checkbox2.place(x=5, y=340)

checkbox_var4 = tk.IntVar()
checkbox4 = tk.Checkbutton(root, text="Метод SNV", variable=checkbox_var4, command=actions5)
checkbox4.pack()
checkbox4.place(x=5, y=200)

checkbox_var3 = tk.IntVar()
checkbox3 = tk.Checkbutton(root, text="Норм. по макс", variable=checkbox_var3, command=actions4)
checkbox3.pack()
checkbox3.place(x=5, y=220)

checkbox_var6 = tk.IntVar()
checkbox6 = tk.Checkbutton(root, text="Савгольт фильтр", variable=checkbox_var6, command=actions6)
checkbox6.pack()
checkbox6.place(x=5, y=260)

checkbox_var7 = tk.IntVar()
checkbox7 = tk.Checkbutton(root, text="Нахожение среднего", variable=checkbox_var7, command=actions3)
checkbox7.pack()
checkbox7.place(x=5, y=322)
# Создаем фрейм для размещения downbar
bottom_frame = tk.Frame(root, height=30, bg='lightgray')
bottom_frame.pack(side='bottom', fill='x')

# Отображаем версию tkinter на полосе
Program_version = 0.3472
version_label = tk.Label(bottom_frame, text=f"Program version: {Program_version}", bg='lightgray')
version_label.pack(side='right', padx=10)


root.mainloop()
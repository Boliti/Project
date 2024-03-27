#Подключение библиотек
import numpy as np 
import os
import random
import tkinter as tk 
from tkinter import filedialog 
from tkinter import messagebox 
import matplotlib.pyplot as plt 
from scipy.sparse.linalg import spsolve 
from scipy import sparse 
from tkinter import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from time import perf_counter


from scipy.signal import find_peaks

#Функции удаления базовой линии
  #Функция нахождения БЛ
def baseline_als(amplitudes, lam, p, niter=10): 
  L = len(amplitudes) 
  D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L-2)) 
  w = np.ones(L) 
  for i in range(niter): 
    W = sparse.spdiags(w, 0, L, L) 
    Z = W + float(lam) * D.dot(D.transpose()) 
    z = spsolve(Z, w*amplitudes) 
    w = p * (amplitudes > z) + (1-p) * (amplitudes < z) 
  return z 
  #Функция удаления БЛ
def  delet_BaseLime(amplitudes_list): 
  lam = entry1.get() 
  if lam == "lam = 1000":
      lam = 1000
  else:  
      lam = float(entry1.get()) 
  p = entry2.get()  
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

#Строительтво графика.
def bilding(frequencies_list, amplitudes_list ):
    global  new_flag, frame, root
    if new_flag:
      frame.destroy() 
    frame = tk.Frame(root) 
    frame.pack() 
    fig = Figure(figsize=(20, 6)) 
    ax = fig.add_subplot()
    print(len(amplitudes_list))
    print(len(frequencies_list))
    for i in range(len(amplitudes_list)):
      ax.plot(frequencies_list[i], amplitudes_list[i], color = selection_color(), alpha=0.5)
    
    ax.set_xlabel('Рамановский сдвиг, см^-1') 
    ax.set_ylabel('Интенсивность') 
    canvas = FigureCanvasTkAgg(fig, master=frame) 
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1) 
    canvas.draw() 
    toolbar = NavigationToolbar2Tk(canvas, frame) 
    toolbar.update()
    new_flag = True



#Функция средней спектрограммы
def averages_spectrum(averaged):
  averaged2 = []
  averaged = np.mean(np.array(averaged), axis=0)
  averaged2.append(averaged)
  return averaged2

def selection(frequencies_list, amplitudes_list):
  frequencies_list2 = []
  amplitudes_list2 = []
  for frequencies, amplitudes in zip(frequencies_list, amplitudes_list):
    mask = (frequencies >= min_freq) & (frequencies <= max_freq)
    if np.any(mask):
      frequencies_list2.append(frequencies[mask])
      amplitudes_list2.append(amplitudes[mask])
  return frequencies_list2, amplitudes_list2



#Нормализация
def normal(list):
  list = np.array(list)
  max = np.max(list)
  for i in range(len(list)):
      list[i] /= max
  return (list)
def normalized(list):
  for a in range(len(list)):
    amplitudes_list[a] = normal(list[a])
  return amplitudes_list



#Строительство по нажатию
def get_input():
  global remove_flag, average_flag, amplitudes_list, frequencies_list
  timer = perf_counter()
  amplitudes_LIST = amplitudes_list
  frequencies_LIST = frequencies_list
  if selection_flag:
     frequencies_LIST, amplitudes_LIST = selection(frequencies_LIST, amplitudes_LIST)
  if remove_flag:
       amplitudes_LIST = delet_BaseLime(amplitudes_LIST)
  if normalize_flag:
       amplitudes_LIST = normalized(amplitudes_LIST)
  if average_flag:
       amplitudes_LIST = averages_spectrum(amplitudes_LIST)
       frequencies_LIST = averages_spectrum(frequencies_list)

  bilding(frequencies_LIST, amplitudes_LIST)
  print(perf_counter() - timer)
  #build(frequencies_list, amplitudes_list, lam, p)

#Функция выбора цвета
def selection_color():
    r = np.random.random()
    g = np.random.random()
    b = np.random.random()
    return (0.5, g, b)

# открытие файла 
def open_folder():
    global frequencies_list, amplitudes_list
    frequencies_list = []
    amplitudes_list = []
    root = tk.Tk()
    root.withdraw()
    folderpath = filedialog.askopenfilenames(title="Выберите файлы", filetypes=(("ESP files", "*.esp"), ("Text files", "*.txt"), ("All files", "*.*")))
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
  global find_flag, frame,average_flag
  average_flag = not average_flag
  if average_flag:
    actions.entryconfigure(1, label="Со средними значениями")
  else:
    actions.entryconfigure(1, label="Без среднего значения")
    find_flag = False
    actions.entryconfigure(2, label="Без поиска пиков")    


def actions3():  
  global find_flag, frame, average_flag
  find_flag = not find_flag    
  if find_flag:
    actions.entryconfigure(2, label="С поиском пиков")
    actions.entryconfigure(1, label="Со средними значениями")
    average_flag = True
  else:
    actions.entryconfigure(2, label="Без поиска пиков")


#пропадает надпись на поле ввода
def on_entry_click(event):
  entry = event.widget
  if entry.get() in ["lam = 1000", "p = 0.001"]: 
    entry.delete(0, tk.END)
#Удаление данных
def clear_data():
  global amplitudes_list, frequencies_list, remove_flag, find_flag
  amplitudes_list = []
  frequencies_list = []
  find_flag = False
  frame.destroy()
  actions.entryconfigure(0, label="С удалением БЛ")
  actions.entryconfigure(1, label="Поиск пиков")
#Удаление графика  
def clear_plotting():
  frame.destroy()

remove_flag = False
find_flag = False
bild_flag = False
new_flag = False
average_flag = False
selection_flag = True
normalize_flag = True

#Создание окна
root = tk.Tk()
root.title("Spectrum")
root.state('zoomed')

#Панель инструментов
mainmenu = tk.Menu(root)
root.config(menu=mainmenu)
#Открытие файла с
filemenu = tk.Menu(mainmenu, tearoff=0)
filemenu.add_command(label="Открыть файлы", command=open_folder)
filemenu.add_command(label="Сохранить...")
filemenu.add_separator()
filemenu.add_command(label="Выход", command=lambda: root.destroy())
#Помощь
helpmenu = tk.Menu(mainmenu, tearoff=0)
helpmenu.add_command(label="Помощь")
helpmenu.add_command(label="О программе")
#Действия над файлом
actions = tk.Menu(mainmenu, tearoff=0)
actions.add_command(label="Без удаления БЛ", command = actions1)
actions.add_command(label="Без среднего значения", command = actions2)
actions.add_command(label="Без поиска пиков", command = actions3)


building = tk.Menu(mainmenu, tearoff=0)
building.add_command(label="Построить график", command = get_input)
building.add_command(label="Очистить данные о файле", command = clear_data)
building.add_command(label="Убрать график", command = clear_plotting)
#Поле ввода 1
entry1 = tk.Entry(root)
entry1.insert(0, "lam = 1000")
entry1.bind("<FocusIn>", on_entry_click)
entry1.pack()
#Поле ввода 2
entry2 = tk.Entry(root)
entry2.insert(0, "p = 0.001")
entry2.bind("<FocusIn>", on_entry_click)
entry2.pack()
#Поле ввода 3
entry3 = tk.Entry(root)
entry3.insert(0, "min_freq ")
entry3.bind("<FocusIn>", on_entry_click)
entry3.pack()
#Поле ввода 4
entry4 = tk.Entry(root)
entry4.insert(0, "max_freq: ")
entry4.bind("<FocusIn>", on_entry_click)
entry4.pack()
#Поле инструментов
mainmenu.add_cascade(label="Файл", menu=filemenu)
mainmenu.add_cascade(label="Справка", menu=helpmenu)
mainmenu.add_cascade(label="Действия", menu=actions)
mainmenu.add_cascade(label="Действия над файлом", menu=building)


root.mainloop()
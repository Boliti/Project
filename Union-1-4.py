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

#Функция удаления базовой линии 
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


def normalize_spectra_batch(spectra_batch):
    max_value = np.max(spectra_batch)
    min_value = np.min(spectra_batch)
    
    normalized_spectra_batch = (spectra_batch - min_value) / (max_value - min_value)
    
    return normalized_spectra_batch

def average_spectrum(spectra_batch):
    average_spectrum = np.mean(spectra_batch, axis=0)
    
    return average_spectrum

#Запоминание переменных lam и p 
def get_input():
    global lam, p, frame
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
    if new_flag:
        frame.destroy() 
    build(frequencies_list, amplitudes_list, lam, p)



#Создание графика

def build(frequencies_list, amplitudes_list, lam, p):
    global frequencies, amplitudes, remove_flag, find_flag, frame, root
    frame = tk.Frame(root) 
    frame.pack() 
    fig = Figure(figsize=(20, 6)) 
    ax = fig.add_subplot()
    ave_spectrums = []
    for i, (frequencies, amplitudes) in enumerate(zip(frequencies_list, amplitudes_list)):
        if remove_flag:
          for amplitudes in amplitudes_list:
            baseline = baseline_als(amplitudes, lam, p)  
            cleaned_spectrum = amplitudes - baseline 
            ax.plot(frequencies, cleaned_spectrum, color=(0, 0, i/(len(frequencies_list)-1)), alpha=0.5)
            ave_spectrums.append(cleaned_spectrum)
        else:
          ax.plot(frequencies, amplitudes, color=(0, 0, i/(len(frequencies_list)-1)), alpha=0.5)
          for amplitudes in amplitudes_list:
            ave_spectrums.append(amplitudes)
        if average_flag:
          ave_spectrum = average_spectrum(ave_spectrums)
          ax.plot(frequencies, ave_spectrum, color='g')
          
        if find_flag:
          peaks, _ = find_peaks(ave_spectrum, width=10, prominence=10)
          ax.plot(frequencies[peaks], ave_spectrum[peaks], 'ro')
          for i in range(len(peaks)):
            ax.text(frequencies[peaks[i]], ave_spectrum[peaks[i]], f'({frequencies[peaks[i]]:.2f},\n {ave_spectrum[peaks[i]]:.2f})', fontsize=8)    
    
    ax.set_xlabel('Рамановский сдвиг, см^-1') 
    ax.set_ylabel('Интенсивность') 
    ax.legend() 
    canvas = FigureCanvasTkAgg(fig, master=frame) 
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1) 
    canvas.draw() 
    toolbar = NavigationToolbar2Tk(canvas, frame) 
    toolbar.update()
    global new_flag
    new_flag = True


# открытие файла 
def open_file(): 
  filepath = filedialog.askopenfilename(initialdir="/", title="Select file",
                     filetypes=(("ESP files", "*.esp"), ("Text files", "*.txt"), ("All files", "*.*")))
  if filepath: 
    try: 
      data = np.loadtxt(filepath)
      global frequencies, amplitudes, label 
      frequencies = data[:, 0] 
      amplitudes = data[:, 1] 
      # Вывод названия обрабатываемого файла
      frame = tk.Frame(root)
      label = tk.Label(root, text="Обрабатываемый файл: " + filepath)
      label.config(font=("Courier", 14))
      label.pack()
      frame.pack()     
    except Exception as e: 
      messagebox.showerror("Error", f"An error occurred while opening the file: {e}") 
  else: 
    messagebox.showwarning("Warning", "No file selected.")
# открытие папки
def open_folder():
    root = Tk()
    root.withdraw()
    folderpath = filedialog.askdirectory()
    if folderpath:  
        try:  
            filepaths = []
            for root, _, files in os.walk(folderpath):  # Используем "_", чтобы проигнорировать лишние значения
                for file in files: 
                    filepaths.append(os.path.join(root, file))
            for path in filepaths: 
                data = np.genfromtxt(path, skip_header=1)
                frequencies = data[:, 0] 
                amplitudes = data[:, 1]
                frequencies_list.append(frequencies)
                amplitudes_list.append(amplitudes)
        except Exception as e:  
            messagebox.showerror("Error", f"An error occurred while opening the folder: {e}")  
    else:  
        messagebox.showwarning("Warning", "No folder selected.")

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
  global frequencies, amplitudes, remove_flag, find_flag, cleaned_spectrum
  frequencies = np.array([])
  amplitudes = np.array([])
  cleaned_spectrum = np.array([])
  find_flag = False
  frame.destroy()
  label.destroy()
  actions.entryconfigure(0, label="С удалением БЛ")
  actions.entryconfigure(1, label="Поиск пиков")
#Удаление графика  
def clear_plotting():
  frame.destroy()

remove_flag = False
find_flag = False
bild_flag = False
new_flag = False
average_flag = True
amplitudes_list=[]
frequencies_list=[]
#Создание окна
root = tk.Tk()
root.title("Spectrum")
root.state('zoomed')

#Панель инструментов
mainmenu = tk.Menu(root)
root.config(menu=mainmenu)
#Открытие файла с
filemenu = tk.Menu(mainmenu, tearoff=0)
filemenu.add_command(label="Открыть файл", command=open_file)
filemenu.add_command(label="Открыть папку", command=open_folder)
filemenu.add_command(label="Новый")
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
actions.add_command(label="Поиск среднего", command = actions2)
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
#Поле ввода 1
entry2 = tk.Entry(root)
entry2.insert(0, "p = 0.001")
entry2.bind("<FocusIn>", on_entry_click)
entry2.pack()
#Поле инструментов
mainmenu.add_cascade(label="Файл", menu=filemenu)
mainmenu.add_cascade(label="Справка", menu=helpmenu)
mainmenu.add_cascade(label="Действия", menu=actions)
mainmenu.add_cascade(label="Действия над файлом", menu=building)


root.mainloop()
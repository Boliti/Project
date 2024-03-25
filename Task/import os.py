import os
import numpy as np
import matplotlib.pyplot as plt

# Инициализация массивов для хранения данных
kika = 200
average_spectrum = np.zeros(kika)

folder_path = '2023-04-07_SERS_plasma_control_cyst'
spectra_files = os.listdir(folder_path)

all_spectra = []
step = 1
# Объединение данных всех спектров и получение минимального и максимального спектра
for file in spectra_files:
    data = np.loadtxt(os.path.join(folder_path, file))

    if data.shape[0] != 1000:
        data = np.interp(np.linspace(0, 1, kika), np.linspace(0, 1, data.shape[0]), data[:, 1])

    all_spectra.append(data)
    average_spectrum += data

# Подсчет среднего спектра
average_spectrum /= len(spectra_files)

# Найдем минимальный и максимальный спектры
min_spectrum = np.min(all_spectra, axis=0)
max_spectrum = np.max(all_spectra, axis=0)

# Построение графика среднего спектра
plt.plot(average_spectrum, label='Average Spectrum')

# Нахождение минимальных и максимальных значений спектров
for i in range(0, len(average_spectrum), step):
    min_val = np.min([spectrum[i] for spectrum in all_spectra])
    max_val = np.max([spectrum[i] for spectrum in all_spectra])
    plt.plot(i, min_val, 'ko', markersize=3)  # Отображение минимальной точки
    plt.plot(i, max_val, 'ko', markersize=3)  # Отображение максимальной точки

    plt.plot([i, i], [min_val, max_val], color='gray', linestyle='-',
             linewidth=1)  # Соединение минимальной и максимальной точек серой тонкой линией


plt.legend()
plt.show()

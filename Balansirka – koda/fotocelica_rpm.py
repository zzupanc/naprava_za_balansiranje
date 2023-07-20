import scipy.signal as sig
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np
import csv



def get_data():
    # no_of_channels = channel_count()
    no_of_channels = 1

    y_channel0 = []
    y_channel1 = []

    with open('fotocelica_meritve.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        if no_of_channels == 2:
            for i, row in enumerate(csv_reader):
                if i % 2 == 0:
                    for value in row:
                        y_channel0.append(float(value))
                else:
                    for value in row:
                        y_channel1.append(float(value))

        elif no_of_channels == 1:
            for row in csv_reader:
                for value in row:
                    y_channel0.append(float(value))

    return y_channel0


def fotocelica_rpm(sample_rate):
    
    signal_fotocelica_inverted = get_data()
    signal_fotocelica = [value * -1 for value in signal_fotocelica_inverted]
    x = np.arange(1, len(signal_fotocelica) + 1)
    peaks_array = np.array(signal_fotocelica)
    peaks, _ = find_peaks(peaks_array, height=3.5, distance=100)
    t_peaks = x[peaks]
    #plt.plot(x, y_fotocelica, label='Channel 0', c='b')
    #plt.plot(peaks, np_arr[peaks], 'x', label='Peaks', c='r')
    #plt.xlabel('Sample')
    #plt.ylabel('Sensitivity [mV/N]')
    #plt.title('Data Plot')
    #plt.legend()
    #plt.show()

    # Število vrhov v celotni meritvi (s tem dobimo frekvenco vrtenja [Hz]
    number_of_peaks = len(t_peaks)
    # Izračun obratov (razlika časov med dvema sosednjima vrhoma signala)
    measured_rpm = (sample_rate / (t_peaks[int(number_of_peaks / 2)] - t_peaks[int(number_of_peaks / 2) - 1])) * 60
    return t_peaks, measured_rpm





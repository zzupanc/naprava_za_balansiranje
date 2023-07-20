import scipy.signal as sig
import matplotlib.pyplot as plt
import numpy as np
import csv
from fotocelica_rpm import *

def filter_measurements(sample_rate, reference_peaks):
    def fft(channel):
        y_fft = np.fft.fft(channel)
        freq_step = sample_rate / len(channel)
        freq = np.arange(len(channel)) * freq_step
        amplitude = np.abs(y_fft)
        amplitude_dB = 20 * np.log10(amplitude)
        return freq[:len(channel) // 2], amplitude_dB[:len(channel) // 2]

    def find_peak(signal, min_range, max_range):
        frequency, amplitude_dB = fft(signal)
        freq_range = (frequency >= min_range) & (frequency <= max_range)
        max_amp = np.max(amplitude_dB[freq_range])
        peak_freq = frequency[np.where(amplitude_dB == max_amp)]
        return peak_freq[0]

    def bandpass_filter(signal):
        order = 2
        tolerance = 0.15
        peak = find_peak(signal, 0, 100)
        low = peak - peak * tolerance
        high = peak + peak * tolerance
        lowcut = 2 * low / sample_rate
        highcut = 2 * high / sample_rate
        cut_frequency = (lowcut, highcut)
        # noinspection PyTupleAssignmentBalance
        b, a = sig.butter(order, cut_frequency, "bandpass")
        filtered_signal_y = sig.filtfilt(b, a, signal)
        return filtered_signal_y

    def draw_graphs():
        no_of_channels = 2

        y_channel0 = []
        y_channel1 = []

        with open('silomeri_meritve.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            if no_of_channels == 2:
                for i, row in enumerate(csv_reader):
                    if i % 2 == 0:
                        for value in row:
                            y_channel0.append(float(value))
                    else:
                        for value in row:
                            y_channel1.append(float(value))

            else:
                pass

        t = range(1, len(y_channel0) + 1)

        y0_filtered = bandpass_filter(y_channel0)
        y1_filtered = bandpass_filter(y_channel1)
        y01_filtered = y0_filtered + y1_filtered

        freq0, amplitude_fft0 = fft(y_channel0)
        freq1, amplitude_fft1 = fft(y_channel1)

        freq_filtered0, amplitude_fft_filtered0 = fft(y0_filtered)
        freq_filtered1, amplitude_fft_filtered1 = fft(y1_filtered)
        
        
        plt.style.use("default")

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4)

        ax1.plot(t, y_channel0, c='r', label=f'Silomer 1 [Hz]')
        ax1.plot(t, y_channel1, c='b', label=f'Silomer 2 [Hz]')
        ax1.legend(loc='right')
        ax1.set_xlabel('Čas [s]')
        ax1.set_ylabel('Sila [N]')
        ax1.grid()

        ax2.plot(t, y0_filtered, label='Filtriran signal 1', c='r')
        ax2.plot(t, y1_filtered, label='Filtriran signal 2', c='b')
        [ax2.axvline(p, c='m', linewidth=0.5) for p in reference_peaks]
        ax2.grid(color='w', linestyle='-', linewidth=1, axis='y')
        ax2.legend(loc='right')
        ax2.set_xlabel('Čas [s]')
        ax2.set_ylabel('Sila [N]')
        ax2.grid()

        ax3.plot(freq_filtered0, amplitude_fft_filtered0, label='FFT - filtriran 1', c='r')
        ax3.plot(freq0, amplitude_fft0, label='FFT nefiltriran 1', c='r', alpha=0.5)
        ax3.axis(xmin=0, xmax=sample_rate / 20)
        ax3.legend(loc='right')
        ax3.set_xlabel('Frekvenca [Hz]')
        ax3.set_ylabel('Amplituda [dB]')
        ax3.grid()

        ax4.plot(freq_filtered1, amplitude_fft_filtered1, label='FFT - filtriran 2', c='b')
        ax4.plot(freq1, amplitude_fft1, label='FFT nefiltriran 2', c='b', alpha=0.5)
        ax4.axis(xmin=0, xmax=sample_rate / 20)
        ax4.set_xlabel('Frekvenca [Hz]')
        ax4.set_ylabel('Amplituda [dB]')
        ax4.legend(loc='right')
        ax4.grid()

        plt.show()
        return y0_filtered, y1_filtered, y01_filtered

    FA_filtriran, FB_filtriran, FAB_filtriran = draw_graphs()
    return FA_filtriran, FB_filtriran, FAB_filtriran

filter_measurements(51200,)

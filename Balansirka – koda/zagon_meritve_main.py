from time import sleep
import numpy as np
from daqhats import mcc172, mcc128, OptionFlags, SourceType, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, \
    chan_list_to_mask
from daqhats import mcc128, OptionFlags, HatIDs, HatError, AnalogInputMode, \
    AnalogInputRange
from GUI_script import entry_settings_screen, measurement_settings, graf_korekcij
from filtriranje_signalov import filter_measurements
from izracun_korekcij import *
from pogon_motorja import *
from fotocelica_rpm import fotocelica_rpm
from kontrola_servomotorja import*

CURSOR_BACK_2 = '\x1b[2D'
ERASE_TO_END_OF_LINE = '\x1b[0K'

# Funkcija za shranjevanje meritev v .csv datoteka
def save_data_csv(array, filename):
    np.savetxt(filename, array, delimiter=',', fmt='%s')


# Glavna zanka za zajem meritev na MCC172 in MCC128
def main():
    # entry_settings_screen() = Izbor za definicijo novih nastavitev ali prevzem predhodno definiranih
    (samples_per_channel, scan_rate, ch0_sensitivity, ch1_sensitivity, channel_no, desired_rpm) = entry_settings_screen()
    # measurement_settings() = Prikaz izbranih nastavitev in "button" za zagon meritve
    measurement_settings(samples_per_channel, scan_rate, ch0_sensitivity, ch1_sensitivity, channel_no, desired_rpm)
    
    # IEPE kanali prevzeti iz GUI-ja
    mcc172_channels = []
    # IEPE napajanje (0=brez napajanja, 1=napajanje)
    iepe_enable = 1
    for i in range(0, channel_no):
        mcc172_channels.append(i)
    mcc172_channel_mask = chan_list_to_mask(mcc172_channels)
    mcc172_num_channels = len(mcc172_channels)

    # Na MCC128 za fotocelico uporabljamo kanal 0
    mcc128_channels = [0]
    mcc128_channel_mask = chan_list_to_mask(mcc128_channels)
    mcc128_num_channels = len(mcc128_channels)

    options = OptionFlags.DEFAULT

    try:
        # MCC172 Class in definicija address-a boarda
        mcc172_hat = mcc172(0)  # MCC172 prvi attachan board na RPi = index 0
        mcc128_hat = mcc128(1)  # MCC128 drugi attachan board na RPi = index 1

        # Vklop IEPE napajanja za vse izbrane kanale na MCC172
        for channel in mcc172_channels:
            mcc172_hat.iepe_config_write(channel, iepe_enable)

        # Definicija občutljivosti IEPE zaznavala; (kanal, občutljivost)
        # ch0 in ch1_sensitivity prevzet it GUI-ja
        mcc172_hat.a_in_sensitivity_write(0, ch0_sensitivity)
        mcc172_hat.a_in_sensitivity_write(1, ch1_sensitivity)
        
        # Definicija input/output kanala na MCC172
        # Območje od -5V do 5V
        input_mode = AnalogInputMode.SE
        input_range = AnalogInputRange.BIP_5V
        mcc128_hat.a_in_mode_write(input_mode)
        mcc128_hat.a_in_range_write(input_range)
        
        # Sinhronizacija clocka na MCC172
        mcc172_hat.a_in_clock_config_write(SourceType.MASTER, scan_rate)

        synced = False
        while not synced:
            (_source_type, actual_scan_rate, synced) = mcc172_hat.a_in_clock_config_read()
            if not synced:
                sleep(0.005)
        
        # Vklop motorja s funkcijo motor_on() z obrati prevzetimi iz GUI inputa
        motor_on(desired_rpm)
        # Dvig ročice s servomotorjem
        move_servo_reverse(180)
        sleep(8)

        # Sinhronizacija obratov glede na zahtevane in dejansko pomerjene
        rpm_sync = False
        speed_index = 0
        while not rpm_sync:
            sleep(3)
            # Merjenje obratov na MCC128 s pomočjo fotocelice
            mcc128_hat.a_in_scan_start(mcc128_channel_mask, samples_per_channel, scan_rate, options)
            # Branje meritve s funkcijo read_and_display_data_hall()
            read_and_display_data_hall(mcc128_hat, samples_per_channel, mcc128_num_channels)
            # Vrh signala = fotocelica zazna obrat na rotorju
            signal_peaks, measured_rpm = fotocelica_rpm(scan_rate)
            # Izpis trenutnih obratov in cleanup HAT-a za naslednjo meritev
            print(f'Trenutni obrati znašajo: {measured_rpm:.2f} n/min')
            mcc128_hat.a_in_scan_cleanup()

            # Preverjanje pomerjenih obratov napram uporabniško zahtevanih obratov
            speed_correction = 0.03
            
            if (desired_rpm * (1 + 0.02)) > measured_rpm > (desired_rpm * (1 - 0.02)):
                # Če so obrati doseženi znotraj tolerance 2% od zahtevnih:
                # Spust ročice in izklop motorja
                print(f'Zahtevani obrati doseženi\n')
                move_servo_reverse(-100)
                sleep(0.5)
                motor_off()
                rpm_sync = True

            elif desired_rpm > measured_rpm:
                # Dvig obratov s pomočjo spremembe PWM Duty cikla
                speed_index += speed_correction
                motor_speed_change(desired_rpm, speed_index)
                print('Povečevanje obratov')

            else:
                # Zmanjšanje obratov s pomočjo spremembe PWM Duty cikla
                speed_index -= speed_correction
                motor_speed_change(desired_rpm, speed_index)
                print('Zmanjševanje obratov')

        # Sinhronizacija clocka MCC172 pred samo meritvijo na silomerih
        mcc172_hat.a_in_clock_config_write(SourceType.MASTER, scan_rate)

        synced = False
        while not synced:
            (_source_type, actual_scan_rate, synced) = mcc172_hat.a_in_clock_config_read()
            if not synced:
                sleep(0.005)
        
        # Zakasnitev pred zajemom veličin, da se motor v celoti izklopi in se izognemo njegovemu šumu
        sleep(4)
     
        # Konfiguracija in začetek zajema signala na silomerih in kodirniku
        mcc128_hat.a_in_scan_start(mcc128_channel_mask, samples_per_channel, scan_rate, options)
        mcc172_hat.a_in_scan_start(mcc172_channel_mask, samples_per_channel, options)

        # Branje podatkov zajema signalov na obeh HAT-ih
        read_and_display_data(mcc172_hat, mcc128_hat, samples_per_channel, mcc172_num_channels)
        # array vseh peakov (prehodov obrata fotocelica) (čas [s])
        signal_peaks, measured_rpm = fotocelica_rpm(scan_rate)
        # Število vrhov v celotni meritvi (s tem dobimo frekvenco vrtenja [Hz]
        number_of_peaks = len(signal_peaks)
        # Kotna hitrost [rad/s]
        w = (scan_rate / (signal_peaks[int(number_of_peaks / 2)] - signal_peaks[int(number_of_peaks / 2) - 1])) * 2 * np.pi

        mcc172_hat.a_in_scan_cleanup()
        mcc128_hat.a_in_scan_cleanup()

    except (HatError, ValueError) as err:
        print('\n', err)

    return scan_rate, samples_per_channel, signal_peaks, w


def read_and_display_data(iepe_hat, hall_hat, samples_per_channel, num_channels):
    # Funkcija za branje signalov iz obeh merilnih kartic
    total_samples_read = 0
    read_request_size = 1000
    timeout = 5.0
    iepe_read_data = []
    hall_read_data = []

    # While loop za branje zajetih signalov dokler niso prebrane vse meritve
    while total_samples_read < samples_per_channel:
        iepe_read_result = iepe_hat.a_in_scan_read_numpy(read_request_size, timeout)
        hall_read_result = hall_hat.a_in_scan_read_numpy(read_request_size, timeout)
        
        # Shranjevanje meritev v list
        iepe_read_data.append(iepe_read_result.data)
        hall_read_data.append(hall_read_result.data)

        # Preverjanje števila prebranih meritev
        samples_read_per_channel = int(len(iepe_read_result.data) / num_channels)
        total_samples_read += samples_read_per_channel

    # Shranjevanje izmerjenih veličin v CSV datoteko)
    iepe_csv_array = np.concatenate(iepe_read_data)
    save_data_csv(iepe_csv_array, 'silomeri_meritve.csv')
    
    hall_csv_array = np.concatenate(hall_read_data)
    save_data_csv(hall_csv_array, 'fotocelica_meritve.csv')


def read_and_display_data_hall(hall_hat, samples_per_channel, num_channels):
    # Funkcija za branje signalov iz MCC128
    # Samo za branje obratov pred samo meritvijo, namenjena za korekcijo obratov
    total_samples_read = 0
    read_request_size = 1000
    timeout = 5.0
    read_data = []

    while total_samples_read < samples_per_channel:
        read_result = hall_hat.a_in_scan_read_numpy(read_request_size, timeout)
        read_data.append(read_result.data)

        samples_read_per_channel = int(len(read_result.data) / num_channels)
        total_samples_read += samples_read_per_channel

    csv_array = np.concatenate(read_data)
    save_data_csv(csv_array, 'fotocelica_meritve.csv')


if __name__ == '__main__':
    # Variabile parametrov balansiranja za nadaljni izračun
    sample_rate, samples_channel, reference_peaks, w = main()
    # Filtriranje signalov s pomočjo bandpass filtra 
    FA_filtriran, FB_filtriran, FAB_filtriran = filter_measurements(sample_rate, reference_peaks)
    # Izračun pozicij in mas korekcij
    m1, m2, fi1, fi2, r = izracun_korekcij(sample_rate, samples_channel, FAB_filtriran, FA_filtriran, FB_filtriran, reference_peaks, w)
    # Polarni diagram za prikaz korekcij
    graf_korekcij(m1, m2, fi1, fi2, r)

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig
from math import sqrt
import csv
plt.style.use("dark_background")

def save_results(fi_Fab, phase_Fa, phase_Fb, Fx_A, Fx_B, Fy_A, Fy_B, Jx1z1, Jy1z1, m_e):

        data = [
        ["Faza F_ab", round(fi_Fab, 1), " [°]"],
        ["Faza F_a", round(phase_Fa, 1), " [°]"],
        ["Faza F_b", round(phase_Fb, 1), " [°]"],
        ["Fx_A", round(Fx_A, 4), " [N]"],
        ["Fx_B", round(Fx_B, 4), " [N]"],
        ["Fy_A", round(Fy_A, 4), " [N]"],
        ["Fy_B", round(Fy_B, 4), " [kgm^2]"],
        ["Jx1z1", "{:.4e}".format(Jx1z1), " [kgm^2]"],
        ["Jy1z1", "{:.4e}".format(Jy1z1), " [kgm^2]"],
        ["me", "{:.4e}".format(m_e), " [kgm]"]
        ]

        filename = "izračuni.csv"
        delimiter = " = "
        with open(filename, "a", newline="") as file:
            writer = csv.writer(file)
            for row in data:
                writer.writerow([row[0] + delimiter + str(row[1]) + row[2]]) 
            writer.writerow([]) # Po dadanih izračunih nova prazna vrstica

def izracun_korekcij(sample_rate, samples_per_channel, FAB_filtriran, FA_filtriran, FB_filtriran, reference_peaks, w):

    r_utezi = 0.03  # [m]
    masa_sistema = 0.800 # [kg]
    dolzina_osi = 0.127  # [m]
    dw = 0
    z1 = 0.050
    z2 = 0.076
    
    reference_times = reference_peaks/sample_rate

    def signal_view_window():
        # Array časa
        t0 = 2 * np.pi / w
        t = np.linspace(0, samples_per_channel/sample_rate, samples_per_channel)
        # Vrh pri katerem se filter stabilizira (vzeli smo sredino signala)
        vrh_stabilizacije = int((w / (2 * np.pi)) / 2)
        
        # Reference potrebujemo da lahko iz celotnega signala izrežemo array meritve enega obrata
        # Čas pri katerih fotocelica zazna nov obrat pri vrhu stabilizacije
        reference_t1 = (reference_times[vrh_stabilizacije])
        # Čas pri katerem je zaznan naslednji obrat
        reference_t2 = (reference_times[vrh_stabilizacije + 1])

        return t, t0, reference_t1, reference_t2

    def graf_filtriranega_signala(t, w, FA_filtriran, FB_filtriran, FAB_filtriran, reference_t1, reference_t2):
        # Slice časov prehoda fotocelice
        # Indeks meritve časa med posameznima obratoma
        reference_index1 = int(reference_t1 * len(t))
        reference_index2 = int(reference_t2 * len(t))

        # Slice signala silomerov za en obrat
        FA_filtriran_sliced = FA_filtriran[reference_index1:reference_index2]
        FB_filtriran_sliced = FB_filtriran[reference_index1:reference_index2]
        FAB_filtriran_sliced = FAB_filtriran[reference_index1:reference_index2]
        
        # Slice kota zasuka enega obrata rotorja (0-360 stopinj)
        theta = w * t[reference_index1:reference_index2]
        
        
        # Ker režemo meritve enega obrata iz sredine celotnega zajetega signala fotocelice,
        # Odštejemo prvo vrednost thete, da začnemo array z 0, posledično 0 stopinj
        theta -= theta[0]

        fig, ax1 = plt.subplots(1)
        ax1.plot(np.degrees(theta), FA_filtriran_sliced, c='m', label='F_A')
        ax1.plot(np.degrees(theta), FB_filtriran_sliced, c='g', label='F_B')
        ax1.plot(np.degrees(theta), FAB_filtriran_sliced, c='y', label='F_A + F_B')
        ax1.set_xlim([0, 360])  # Meje X osi (0, 360 stopinj)
        ax1.grid()
        ax1.legend()
        plt.ylabel('Sila [N]', fontsize=14)
        plt.xlabel('Kot [°]', fontsize=14)
        plt.show()
        
        return FA_filtriran_sliced, FB_filtriran_sliced, FAB_filtriran_sliced, theta


    def minimum_sile(signal, theta):

        # Funkcija za določitev minimuma signala sile pri enem obratu
        # theta[0] pri 0 stopinjah zasuka
        # theta[-1] pri 360 stopinjah zasuka

        t_range = np.where((theta >= theta[0]) & (theta <= theta[-1]))[0]
        # Velikost minimuma signala sile
        min_signala = np.min(signal[t_range])
        # Indeks array-ja pri katerem je minimum signala
        min_index = np.argmin(signal[t_range])
        # Kot pri katerem je minimum signala sile z uporabo indeksa 
        theta_min_signala = np.degrees(theta[t_range[min_index]])
    
        return min_signala, theta_min_signala
        
    def maximum_sile(signal, theta):
        
        # Funkcija za določitev maksimuma sile pri enem obratu
        # theta[0] pri 0 stopinjah zasuka
        # theta[-1] pri 360 stopinjah zasuka

        t_range = np.where((theta >= theta[0]) & (theta <= theta[-1]))[0]
        # Velikost maksimuma signala sile
        max_signala = np.max(signal[t_range])
        # Indeks array-ja pri katerem je maximum signala
        max_index = np.argmax(signal[t_range])
        # Kot pri katerem je minimum signala sile z uporabo indeksa 
        theta_max_signala = np.degrees(theta[t_range[max_index]])
        
        return max_signala, theta_max_signala

    def izracun_velicin(jx1z1, jy1z1, m, e, z_1, z_2, r):
        # Izračun masnih korekcij
        m_1 = (sqrt((jx1z1 - m*e*z_2)**2 + jy1z1**2))/(sqrt((r**2)*(z_1-z_2)**2))
        m_2 = (sqrt((jx1z1 - m*e*z_1)**2 + jy1z1**2))/(sqrt((r**2)*(z_1-z_2)**2))
        # Izračun pozicij masnih korekcij
        x1 = (r*(z_1-z_2)*(m*e*z_2-jx1z1))/(sqrt((z_1-z_2)**2)*sqrt((jx1z1-m*e*z_2)**2 + (jy1z1**2)))
        y1 = jy1z1*r*(z_2-z_1)/(sqrt((z_1-z_2)**2)*sqrt((jx1z1-masa_sistema*e*z_2)**2 + (jy1z1**2)))
        x2 = (r*(z_1-z_2)*(jx1z1 - m*e*z_1))/(sqrt((z_1-z_2)**2)*sqrt((jx1z1-m*e*z1)**2 + (jy1z1**2)))
        y2 = jy1z1*r*(z_1-z_2)/(sqrt((z_1-z_2)**2)*sqrt((jx1z1-m*e*z_1)**2 + (jy1z1**2)))
        # Izračun kotov korekcije
        # Korekcija +180 stopinj, za pozicijo mase. Pozicija merjenja na silomerih in dejanska sila rotorja.
        fi_1 = round(np.degrees(np.arctan2(y1, x1)) + fi_zasuka_ks) + 180
        fi_2 = round(np.degrees(np.arctan2(y2, x2)) + fi_zasuka_ks) + 180
        
        return m_1, m_2, fi_1, fi_2

    # Parametri vidnega okna enega obrata
    t, t0, reference_t1, reference_t2 = signal_view_window()
    # Grafični prikaz filtriranih signalov enega obrata
    FA_filtriran_sliced, FB_filtriran_sliced, FAB_filtriran_sliced, theta = graf_filtriranega_signala(t, w, FA_filtriran, FB_filtriran, FAB_filtriran, reference_t1, reference_t2)

    # Določitev pozicij minimuma sile F_AB in maksimumov sil F_A in F_B:

    FAB_y_min, FAB_t = minimum_sile(FAB_filtriran_sliced, theta) # Velikost minimum/maksimuma [N] in kot [stopinje]
    FA_y_max, FA_t = maximum_sile(FA_filtriran_sliced, theta)
    FB_y_max, FB_t = maximum_sile(FB_filtriran_sliced, theta)
    print(f'FAB_min_theta = {FAB_t:.5f} stopinj')
    print(f'FAB_min = {FAB_y_min:.8f}N\n')
    print(f'FA_max_theta  = {FA_t:.5f} stopinj')
    print(f'FA_min = {FA_y_max:.8f}N\n')
    print(f'FB_max_theta  = {FB_t:.5f} stopinj')
    print(f'FB_min = {FB_y_max:.8f}N\n')

    # Izračun kotov faznea zamika maksimumov: F_A in F_B, napramam minimumu F_AB
    fi_zasuka_ks = FAB_t # [stopinje]
    fi_A = FAB_t - FA_t
    fi_B = FAB_t - FB_t

    # Izračun sil v podporah A in B
    Fx_A_r = FA_y_max*np.cos(np.deg2rad(fi_A))
    Fx_B_r = FB_y_max*np.cos(np.deg2rad(fi_B))
    Fy_B_r = -FB_y_max*np.sin(np.deg2rad(fi_B))
    #Fy_A_r = FA_y_max*np.sin(np.deg2rad(fi_A))

    # Izračun ekscentra filtriranega signala
    e_grafa = (-(Fx_A_r+Fx_B_r)/w**2)/masa_sistema
    m_e = e_grafa*masa_sistema
    # Izračun manjkajoče sile s pomočjo ekscentra
    Fy_A_r = masa_sistema*e_grafa*dw - Fy_B_r


    # Izračun MVM Jx1z1, Jy1z1
    Jy1z1_r = -Fy_B_r*dolzina_osi/w**2
    Jx1z1_r = -Fx_B_r*dolzina_osi/w**2
    
    # Izračun korekcij
    m1, m2, fi1, fi2 = izracun_velicin(Jx1z1_r, Jy1z1_r, masa_sistema, e_grafa, z1, z2, r_utezi)

    print(f'Jx1z1 = {Jx1z1_r:.10f}, Jy1z1 = {Jy1z1_r:.10f}, Fx_A= {Fx_A_r:.5f}, Fy_A = {Fy_A_r:.5f}, Fx_B = {Fx_B_r:.5f}, Fy_B = {Fy_B_r:.5f}, e = {e_grafa*1000:.4f}')
    print('\n')
    print(f'm1 = {m1*1000:.2f} [g], na radij r = {r_utezi*1000} [mm], na poziciji {fi1:.1f}°')
    print(f'm2 = {m2*1000:.2f} [g], na radij r = {r_utezi*1000} [mm], na poziciji {fi2:.1f}°')
    
    save_results(fi_zasuka_ks, fi_A, fi_B, Fx_A_r, Fx_B_r, Fy_A_r, Fy_B_r, Jx1z1_r, Jy1z1_r, m_e)

    return 1000*m1, 1000*m2, fi1, fi2, 1000*r_utezi


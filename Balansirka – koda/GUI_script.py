import tkinter
from PIL import ImageTk, Image
from tkinter import ttk
from tkinter import messagebox
import csv
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
#import rotor_spin

# Defining basic fonts used in GUI
text_font = ("Helvetica", 12, "normal")
button_font = ("Helvetica", 16, "bold")
button_font2 = ("Helvetica", 14, "bold")
bigbutton_font = ("Helvetica", 24, "bold")
settings_font = ("Helvetica", 10, "bold")


def entry_settings_screen():
    # Settings returned in this function to main script to set HAT parameters
    old_settings_return = []
    new_settings_return = []

    def new_settings_window():

        def csv_settings_save():
            # Reading inputs from new_settings_window and storing them into a csv file
            # The settings can be then reused with load settings button on previous window
            samples_per_channel = samples_per_channel_entry.get()
            scan_rate = scan_rate_entry.get()
            ch0_sensitivity = ch0_sensitivity_entry.get()
            ch1_sensitivity = ch1_sensitivity_entry.get()
            number_of_channels = channel_count_combobox.get()
            requested_rpm = rpm_entry.get()

            if samples_per_channel and scan_rate and ch0_sensitivity and ch1_sensitivity:
                new_settings_return.append(int(samples_per_channel))
                new_settings_return.append(int(scan_rate))
                new_settings_return.append(int(ch0_sensitivity))
                new_settings_return.append(int(ch1_sensitivity))
                new_settings_return.append(int(number_of_channels))
                new_settings_return.append(int(requested_rpm))

                with open('settings.csv', 'w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    for item in new_settings_return:
                        writer.writerow([item])

            else:
                # Error if any cell is left empty befor trying to save the settings into csv
                tkinter.messagebox.showwarning(title="Napaka",
                                               message="Prosim pravilno izpolni vsa prazna polja nastavitev!")

            if samples_per_channel and scan_rate and ch0_sensitivity and ch1_sensitivity:
                # When all settings are entered and saved into csv the window is closed
                enter_new_settings_window.destroy()

        # Creating the window instance, configuring its size and window name
        settings_selection_window.destroy()
        enter_new_settings_window = tkinter.Tk()
        enter_new_settings_window.title("Vnos novih parametrov balansiranja")
        enter_new_settings_window.geometry('600x400')

        # Creating a frame for the window where measurement settings are set
        new_settings_frame = tkinter.Frame(enter_new_settings_window)
        new_settings_frame.pack()

        # LabelFrame where all Labels and Entries are positioned on the above defined Frame
        measurement_settings_frame = tkinter.LabelFrame(new_settings_frame)
        measurement_settings_frame.grid(row=0, column=0, padx=20, pady=10)

        samples_per_channel_label = tkinter.Label(measurement_settings_frame, text="Število vzorcev na kanal", font=settings_font)
        samples_per_channel_entry = tkinter.Entry(measurement_settings_frame)

        scan_rate_label = tkinter.Label(measurement_settings_frame, text="Frekvenca vzorčenja [Hz]", font=settings_font)
        scan_rate_entry = tkinter.Entry(measurement_settings_frame)

        ch0_sensitivity_label = tkinter.Label(measurement_settings_frame, text="Občutljivost - silomer 1 [mV/N]", font=settings_font)
        ch0_sensitivity_entry = tkinter.Entry(measurement_settings_frame)

        ch1_sensitivity_label = tkinter.Label(measurement_settings_frame, text="Občutljivost - silomer 2 [mV/N]", font=settings_font)
        ch1_sensitivity_entry = tkinter.Entry(measurement_settings_frame)

        channel_count_label = tkinter.Label(measurement_settings_frame, text="Število kanalov zajema", font=settings_font)
        channel_count_combobox = ttk.Combobox(measurement_settings_frame, values=["1", "2"], font=settings_font, width=14)
        
        rpm_label = tkinter.Label(measurement_settings_frame, text="Željeni obrati [n/min]", font=settings_font)
        rpm_entry = tkinter.Entry(measurement_settings_frame)

        # Positioning the Labels and Entries on LableFrame grid
        samples_per_channel_label.grid(row=1, column=0, padx=50, pady=5)
        samples_per_channel_entry.grid(row=2, column=0, padx=50, pady=5)

        scan_rate_label.grid(row=3, column=0, padx=50, pady=5)
        scan_rate_entry.grid(row=4, column=0, padx=50, pady=5)

        ch0_sensitivity_label.grid(row=5, column=0, padx=50, pady=5)
        ch0_sensitivity_entry.grid(row=6, column=0, padx=50, pady=5)

        ch1_sensitivity_label.grid(row=7, column=0, padx=50, pady=5)
        ch1_sensitivity_entry.grid(row=8, column=0, padx=50, pady=5)

        channel_count_label.grid(row=9, column=0, padx=50, pady=5)
        channel_count_combobox.grid(row=10, column=0, padx=50, pady=5)
        
        rpm_label.grid(row=11, column=0, padx=50, pady=5)
        rpm_entry.grid(row=12, column=0, padx=50, pady=5)

        # Button to save the settings entered
        button = tkinter.Button(new_settings_frame, text="Shrani nastavitve", font=button_font2, command=csv_settings_save)
        button.grid(row=1, column=0, sticky="news", padx=20, pady=20)

        enter_new_settings_window.mainloop()

    def load_settings():
        # Opening the settings CSV and reading previously stored settings
        with open('settings.csv', 'r') as csv_settings:
            for row in csv_settings:
                old_settings_return.append(int(row))

        # When all settings are acquired, the window is closed
        settings_selection_window.destroy()


    # Window to display settings choices -> new settings or load settings (last ones used)
    settings_selection_window = tkinter.Tk()
    settings_selection_window.geometry('600x400')
    settings_selection_window.title("Izbor nastavitev")

    img1 = Image.open("new_settings_img.png")
    new_settings_img = img1.resize((80, 80))
    new_settings_img_tk = ImageTk.PhotoImage(new_settings_img)

    img2 = Image.open("load_settings_img.png")
    load_settings_img = img2.resize((80, 80))
    load_settings_img_tk = ImageTk.PhotoImage(load_settings_img)



    # Creating a frame for the window where measurement settings are set
    settings_selection_frame = tkinter.Frame(settings_selection_window)
    settings_selection_frame.pack()

    new_settings_image_label = tkinter.Label(settings_selection_frame, image=new_settings_img_tk)
    load_settings_image_label = tkinter.Label(settings_selection_frame, image=load_settings_img_tk)

    # New settings button
    new_settings = tkinter.Button(settings_selection_frame, font=button_font, text="Nova konfiguracija", command=new_settings_window)
    new_settings.grid(row=1, column=0, sticky="news", padx=20, pady=0)
    new_settings_image_label.grid(row=0, column=0, sticky="news", padx=20, pady=80)


    # Load settings button
    load_settings = tkinter.Button(settings_selection_frame, font=button_font, text="Obstoječa konfiguracija", command=load_settings)
    load_settings.grid(row=1, column=1, sticky="news", padx=20, pady=0)
    load_settings_image_label.grid(row=0, column=1, sticky="news", padx=20, pady=80)

    settings_selection_window.mainloop()

    # Checking which list is empty to determine which settings will be returned with this function
    # If new_settings_return list is empty, we want to return old_settings_return list since it has all the values
    if len(new_settings_return) == 0:
        return old_settings_return
    else:
        return new_settings_return


def measurement_settings(samples_per_channel, scan_rate, ch0_sensitivity, ch1_sensitivity, channel_no, rpm):

    # Function to display the selected settings in a GUI window
    sensor_settings_window = tkinter.Tk()
    sensor_settings_window.geometry('600x400')
    sensor_settings_window.title("Zagon meritve")

    sensor_settings_frame = tkinter.Frame(sensor_settings_window)
    sensor_settings_frame.pack()

    settings_display_frame = tkinter.LabelFrame(sensor_settings_frame, text="Izbrani parametri balansiranja", font=button_font2, pady=20)
    settings_display_frame.grid(row=0, column=0, padx=20, pady=10)

    # The data passed into measurement_settings function getting Labels
    # The Labels are attached on above defined LabelFrame
    samples = tkinter.Label(settings_display_frame, font=text_font, text=f"Število vzorcev na kanal: {samples_per_channel}")
    scanrate = tkinter.Label(settings_display_frame, font=text_font, text=f"Frekvenca vzorčenja: {scan_rate} Hz")
    ch0sensitivity = tkinter.Label(settings_display_frame, font=text_font, text=f"Občutljivost - silomer 1: {ch0_sensitivity} mV/N")
    ch1sensitivity = tkinter.Label(settings_display_frame, font=text_font, text=f"Občutljivost - silomer 2: {ch1_sensitivity} mV/N")
    channels = tkinter.Label(settings_display_frame, font=text_font, text=f"Število kanalov zajema: {channel_no}")
    desired_rpm = tkinter.Label(settings_display_frame, font=text_font, text=f"Željeni obrati: {rpm} n/min")

    # Positioning the Labels on LabelFrame
    samples.grid(row=0, column=0, padx=20, pady=10)
    scanrate.grid(row=1, column=0, padx=20, pady=10)
    ch0sensitivity.grid(row=3, column=0, padx=20, pady=10)
    ch1sensitivity.grid(row=4, column=0, padx=20, pady=10)
    channels.grid(row=5, column=0, padx=20, pady=10)
    desired_rpm.grid(row=6, column=0, padx=20, pady=10)
    
    button = tkinter.Button(sensor_settings_frame, text="Poženi meritev", font=button_font2, command=sensor_settings_window.destroy)
    button.grid(row=1, column=0, sticky="news", padx=20, pady=20)
    
    sensor_settings_window.mainloop()
    


def graf_korekcij(m1, m2, fi1, fi2, r):
    fig = Figure(figsize=(10, 5))
    ax2 = fig.add_subplot(121, projection='polar')
    ax2.plot(np.radians(fi1), r, marker=".", markersize=30, c='r', label=f'Korekcija z1 = {m1:.2f} g')
    ax2.set_rmax(3 / 2 * r)
    ax2.set_theta_zero_location("N")
    ax2.set_theta_direction(-1)
    ax2.set_rticks([r / 2, r, 3 / 2 * r])
    ax2.set_rlabel_position(20)
    ax2.set_title("Ravnina Z-1", fontsize=14)
    ax2.legend(bbox_to_anchor=(0.1, -0.1), loc="lower center")

    ax3 = fig.add_subplot(122, projection='polar')
    ax3.plot(np.radians(fi2), r, marker=".", markersize=30, c='g', label=f'Korekcija z2 = {m2:.2f} g')
    ax3.set_rmax(3 / 2 * r)
    ax3.set_theta_zero_location("N")
    ax3.set_theta_direction(-1)
    ax3.set_rticks([r / 2, r, 3 / 2 * r])
    ax3.set_rlabel_position(20)
    ax3.set_title("Ravnina Z-2", fontsize=14)
    ax3.legend(bbox_to_anchor=(0.1, -0.1), loc="lower center")

    root = tkinter.Tk()
    root.title("Graf masnih korekcij")
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    tkinter.mainloop()


import RPi.GPIO as GPIO
import time

# Koda do zagona motorja z generiranjem PWM signala

GPIO.setwarnings(False)
pwm_pin = 4  # GPIO 4, pin 7 (RPi ima 2 označbi pinov, GPIO index in navadni index board pina, NISTA ENAKA!!)
pwm_frequency = 50  # Frekvenca v Hz s katero bomo modulirali širino impulzov (PWM)
pwm_stop = 0  # PWM 0 za izklop motorja

low_dutycycle = 6.5  # Duty cycle uporabljen pri nizkih obratih (cca. 1900 RPM)
mid_dutycycle = 7  # Duty cycle uporabljen pri "povprečnih" obratih (cca. 2450 RPM)

GPIO.setmode(GPIO.BCM)  # Definiramo da so indeksi pinov glede na GPIO indeks in ne board pin number
GPIO.setup(pwm_pin, GPIO.OUT)  # Konfiguracija GPIO pina na PWM output
esc_pwm = GPIO.PWM(pwm_pin, pwm_frequency)


def motor_on(desired_rpm):
    # Vklop motorja, pričnemo z PWM=0 mirovanjem, nato glede na zahtevane obrate generiramo PWM
    esc_pwm.start(pwm_stop)
    time.sleep(0.1)
    if 2800 >= desired_rpm > 1800:
        # Če so obrati med 1800 in 2800 pričnemo generiranje PWM-a z MID Duty Ciklom
        esc_pwm.ChangeDutyCycle(mid_dutycycle)
    else:
        # Else prinemo z generiranjem z LOW Duty Ciklom
        esc_pwm.ChangeDutyCycle(low_dutycycle)


def motor_off():
    # Izklop motorja
    esc_pwm.ChangeDutyCycle(pwm_stop)


def motor_speed_change(desired_rpm, speed_index):
    # Funkcija za korekcijo PWM-a (večji/manjši duty cikel) glede na pomerjene obrate
    # Z korekcijo PWM-a lahko dosežemo željene obrate rotorja
    if 2800 >= desired_rpm > 1900:
        esc_pwm.ChangeDutyCycle(mid_dutycycle + speed_index)
    else:
        esc_pwm.ChangeDutyCycle(low_dutycycle + speed_index)



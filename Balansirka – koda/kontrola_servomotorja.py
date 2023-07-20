from gpiozero import Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory


factory = PiGPIOFactory()
GPIO_pin = 7  # Indeks GPIO pina (RPi ima 2 označbi pinov, GPIO index in navadni index pina, ki nista enaka)!!!

# Servo funkcija iz knjižnice gpiozero
# Servo(gpio_pin_number, minimalna šitirna pulza, maksimalna širina pulza, pin konfiguracija
servo = Servo(GPIO_pin, min_pulse_width=0.8/1000, max_pulse_width=2.2/1000, pin_factory=factory)


def move_servo_degrees(degrees):
    # Convert degrees to value between -1 and 1 (servo.value zahteva range med -1 in 1)
    # -1 minimalni duty_cycle, +1 maksimalni duty_cycle
    duty_cycle = (degrees / 180.0) - 1.0
    # Set the servo motor's value
    servo.value = duty_cycle
    # Wait for the servo motor to move to the desired position
    sleep(0.5)

def move_servo_reverse(degrees):
    # Convert degrees to value between -1 and 1 (servo.value zahteva range med -1 in 1)
    # -1 minimalni duty_cycle, +1 maksimalni duty_cycle
    duty_cycle = ((degrees - 180) / 180.0) + 1.0
    # Set the servo motor's value
    servo.value = duty_cycle
    # Wait for the servo motor to move to the desired position
    sleep(0.5)
    



from picamera2 import Picamera2
import socket
import time
import RPi.GPIO as GPIO
import subprocess
import cv2
import datetime

get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
get_socket.connect(("", 7000))
port = int(get_socket.recv(65535).decode())
get_socket.close()
START_RECORDING = 1
STOP_RECORDING = 0
data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cam = Picamera2()
cam.preview_configuration.main.size = (3280, 2464)
cam.preview_configuration.main.format = "RGB888"
cam.configure("preview")
cam.start()
time.sleep(0.5)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN)
while GPIO.input(3) != GPIO.HIGH:
    time.sleep(0.2)
blinking_time = datetime.datetime.now()
led_on = True
subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
while GPIO.input(3) == GPIO.HIGH:
    frame = cam.capture_array()
    frame = frame[0:2464, 500:2280]
    encoded = cv2.imencode(".jpg", frame)
    for i in range(0, len(encoded), 60000):
        data_socket.sendto(encoded[i:60000], ("192.168.4.1", port))
    if(blinking_time.second-datetime.datetime.now().second > 1):
        if(led_on):
            subprocess.run("echo 0 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
            led_on = False
        else:
            subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
            led_on = True
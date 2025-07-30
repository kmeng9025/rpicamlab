from picamera2 import Picamera2
import socket
import time
import RPi.GPIO as GPIO
import subprocess
import cv2

get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
get_socket.connect(("192.168.4.1", 5000))
port = int(get_socket.recv(65535).decode())
get_socket.close()
START_RECORDING = 1
STOP_RECORDING = 0

data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cam = Picamera2()
cam.preview_configuration.main.size = (1024, 768)
cam.preview_configuration.main.format = "RGB888"
cam.configure("preview")
cam.start()
time.sleep(0.5)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN)
while GPIO.input(3) != GPIO.HIGH:
    time.sleep(0.2)

while GPIO.input(3) == GPIO.HIGH:
    frame = cam.capture_array()
    frame = frame[0, 768, ]
    cv2.imencode(".jpg", frame)
    data_socket.sendto()


def setMode(mode):
    if(mode == 1):
        subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
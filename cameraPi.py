from picamera2 import Picamera2
import socket
import time
import RPi.GPIO as GPIO
import subprocess
import cv2
import datetime
import re
import threading

print("Camera Program Started")
print("Scanning for Network")
def main():
    host_ssid = "rpicamlab"
    host_password = "rpicamlab"
    ssids = []
    Host_IP = "10.42.0.1"
    while True:
        try:
            if subprocess.check_output(["sudo", "iwgetid", "-r"], encoding="utf-8").strip() == host_ssid:
                print(f"Connected to {host_ssid}")
                break
        except:
            print("Not Connected")
        # Ask NM to connect (it will rescan if needed)
        subprocess.run(["nmcli", "dev", "disconnect", "wlan0"], check=False)
        subprocess.run(["nmcli", "dev", "wifi", "rescan"], check=False)
        subprocess.run(["sudo","nmcli","dev","wifi","connect", host_ssid, "password", host_password],
                        check=False)
        time.sleep(1)

    print("Creating Socket")
    get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Connecting to Host for Port")
    get_socket.connect((Host_IP, 7000))
    print("Connected to Port 7000")
    print("Asking for Port")
    port = int(get_socket.recv(65535).decode())
    print("Received Data Port:", port)
    get_socket.close()
    print("Closed Asking Port")
    print("Creating Socket for UDP")
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Creating Camera")
    cam = Picamera2()
    print("Camera Created")
    print("Configuring Camera")
    cam.preview_configuration.main.size = (3280, 2464)
    # cam.preview_configuration.main.size = (2592, 1944)
    cam.preview_configuration.main.format = "RGB888"
    cam.configure("preview")
    print("Camera Configured")
    print("Starting Camera")
    cam.start()
    print("Camera Started")
    time.sleep(0.5)
    threading.Thread(target=check_stop).start()
    blinking_time = datetime.datetime.now()
    led_on = True
    subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
    try:
        while not stop:
            while recording:
                print("Capturing")
                frame = cam.capture_array()
                frame = frame[0:2464, 410:2870] 
                # 0.75 2460 410 2870
                # 0.75 1944 324 2268
                # frame = frame[0:1944, 324:2268]
                print("Encoding")
                _, encoded = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),  [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                encoded_bytes = encoded.tobytes() + b"end"
                print("Sending\n")
                for i in range(0, len(encoded_bytes), 1400):
                    data_socket.sendto(encoded_bytes[i:i+1400], (Host_IP, port))
                if((datetime.datetime.now()-blinking_time).total_seconds() > 1):
                    if(led_on):
                        subprocess.run("echo 0 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
                        led_on = False
                        blinking_time = datetime.datetime.now()
                    else:
                        subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
                        led_on = True
                        blinking_time = datetime.datetime.now()
    except Exception as e:
        print("Capturing Got Error: ", e)
    data_socket.sendto(b"c", (Host_IP, port))
    cam.stop()
    cam.close()
    data_socket.close()
    GPIO.cleanup()
    # subprocess.run(["sudo", "nmcli", "connection", "delete", "static_rpicamlab"], check=False)

recording = False
stop = False
def check_stop():
    global recording
    global stop
    print("Creating Assigning Socket")
    command_listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Assigning Socket Created")
    print("Binding Socket to Port", 7000)
    command_listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    command_listening_socket.bind(("", 7000))
    print("Binded Socket")
    command_listening_socket.listen(10)
    print("Waiting for Command From Server to Start")
    command_socket, server_adr = command_listening_socket.accept()
    command_socket.send(b"namehi")
    while True:
        data = command_socket.recv(65535).decode()
        if data == "start":
            print("Received Command to Start Recording")
            recording = True
        elif data == "stop":
            print("Received Command to Stop Recording")
            recording = False
        else:
            print("Received Command to Stop Program")
            stop = True
            time.sleep(0.5)
            exit(0)

# while True:
# while GPIO.input(3) != GPIO.HIGH:
#     time.sleep(0.2)
# print("Starting, Remove from Pin to Stop\n")\
main()

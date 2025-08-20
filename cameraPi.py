from picamera2 import Picamera2
import socket
import time
import RPi.GPIO as GPIO
import subprocess
import cv2
import datetime
import re

print("Camera Program Started")
print("Scanning for Network")
host_ssid = "rpicamlab"
host_password = "rpicamlab"
ssids = []
Host_IP = "10.42.0.1"
while True:
    if subprocess.check_output(["sudo", "iwgetid", "-r"], encoding="utf-8").strip() == host_ssid:
        print(f"Connected to {host_ssid}")
        break
    # Ask NM to connect (it will rescan if needed)
    subprocess.run(["sudo","nmcli","-w","20","dev","wifi","connect", host_ssid, "password", host_password],
                    check=False)
    time.sleep(1)


# while host_ssid not in ssids:
#     result = subprocess.check_output(["sudo", "iwlist", "wlan0", "scan"], encoding="utf-8")
#     ssids = re.findall(r'ESSID:"(.*?)"', result)
# print("Host Network Found")
# print("Connecting to Host Network")
# try:
#     connected_ssid = subprocess.check_output(["sudo", "iwgetid", "-r"], encoding="utf-8").strip()
# except subprocess.CalledProcessError as e:
#     connected_ssid = ""
# if(connected_ssid != host_ssid):
#     # print("Disconnecting from Current Network")
#     # subprocess.run(["sudo", "wpa_cli", "disconnect"], check=True)
#     # network_id = subprocess.check_output(
#     #     ["sudo", "wpa_cli", "add_network"], text=True
#     # ).strip()
#     # # print(f"Network ID: {network_id}")
#     # subprocess.run(["nmcli", "dev", "disconnect"], check=True)
#     while connected_ssid != host_ssid:
#         if(connected_ssid != ""):
#             subprocess.run(["sudo", "nmcli", "device", "disconnect", "wlan0"], check=True)
#         try:
#             print("Trying to Connect")
#             # subprocess.run("nmcli device wifi connect \"rpicamlab\" password \"rpicamlab\"", shell=True)
#             subprocess.run(["sudo", "nmcli", "dev", "wifi", "connect", host_ssid, "password", host_password], check=True)
#             # subprocess.run([
#             #     "sudo", "nmcli", "connection", "add",
#             #     "type", "wifi",
#             #     "ifname", "wlan0",
#             #     "con-name", "static_rpicamlab",
#             #     "ssid", host_ssid,
#             #     "wifi-sec.key-mgmt", "wpa-psk",
#             #     "wifi-sec.psk", host_password,
#             #     "ipv4.method", "manual",
#             #     "ipv4.addresses", "10.42.0.10/24",
#             #     "ipv4.gateway", "10.42.0.1",
#             #     "ipv4.dns", "8.8.8.8"
#             # ], check=True)

#             # subprocess.run(["sudo", "nmcli", "connection", "up", "static_rpicamlab"], check=True)

#             # print("Setting SSID")
#             # subprocess.run([
#             #     "sudo", "wpa_cli", "set_network", network_id, "ssid", f'\"{host_ssid}\"'
#             # ], check=True)
#             # print("Setting Password")
#             # subprocess.run([
#             #     "sudo", "wpa_cli", "set_network", network_id, "psk", f'\"{host_password}\"'
#             # ], check=True)
#             # print("Enabling Network")
#             # subprocess.run(["sudo", "wpa_cli", "enable_network", network_id], check=True)
#             # print("Selecting Network")
#             # subprocess.run(["sudo", "wpa_cli", "select_network", network_id], check=True)
#             # print("Saving Configuration")
#             # subprocess.run(["sudo", "wpa_cli", "save_config"], check=True)
#             # print(f"Connected to Wi-Fi network: {host_ssid}")
#             connected_ssid = subprocess.check_output(["sudo", "iwgetid", "-r"], encoding="utf-8").strip()
#         except subprocess.CalledProcessError as e:
#             # connected_ssid = subprocess.check_output(["sudo", "iwgetid", "-r"], encoding="utf-8").strip()
#             if(connected_ssid != "" and connected_ssid != host_ssid):
#                 subprocess.run(["sudo", "nmcli", "device", "disconnect", "wlan0"], check=True)
#             print("Could not Connect, Trying Again...")
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
print("Initializing Pins")
time.sleep(0.5)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN)
print("Waiting to Start")
while GPIO.input(3) != GPIO.HIGH:
    time.sleep(0.2)
print("Starting, Remove from Pin to Stop\n")
blinking_time = datetime.datetime.now()
led_on = True
subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
while GPIO.input(3) == GPIO.HIGH:
    print("Capturing")
    frame = cam.capture_array()
    frame = frame[0:2464, 410:2870] 
    # 0.75 2460 410 2870
    # 0.75 1944 324 2268
    # frame = frame[0:1944, 324:2268]
    print("Encoding")
    _, encoded = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    encoded_bytes = encoded.tobytes() + b"end"
    print("Sending\n")
    for i in range(0, len(encoded_bytes), 1024):
        data_socket.sendto(encoded_bytes[i:i+1024], (Host_IP, port))
    if((datetime.datetime.now()-blinking_time).total_seconds() > 1):
        if(led_on):
            subprocess.run("echo 0 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
            led_on = False
            blinking_time = datetime.datetime.now()
        else:
            subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
            led_on = True
            blinking_time = datetime.datetime.now()
data_socket.sendto(b"c", (Host_IP, port))
cam.stop()
cam.close()
data_socket.close()
GPIO.cleanup()
subprocess.run(["sudo", "nmcli", "connection", "delete", "static_rpicamlab"], check=False)
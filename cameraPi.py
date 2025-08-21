# from picamera2 import Picamera2
# import socket
# import time
# import RPi.GPIO as GPIO
# import subprocess
# import cv2
# import datetime
# import re
# import threading

# print("Camera Program Started")
# print("Scanning for Network")
# def main():
#     host_ssid = "rpicamlab"
#     host_password = "rpicamlab"
#     ssids = []
#     Host_IP = "10.42.0.1"
#     while True:
#         try:
#             if subprocess.check_output(["sudo", "iwgetid", "-r"], encoding="utf-8").strip() == host_ssid:
#                 print(f"Connected to {host_ssid}")
#                 break
#         except:
#             print("Not Connected")
#         # Ask NM to connect (it will rescan if needed)
#         subprocess.run(["nmcli", "dev", "disconnect", "wlan0"], check=False)
#         subprocess.run(["nmcli", "dev", "wifi", "rescan"], check=False)
#         subprocess.run(["sudo","nmcli","dev","wifi","connect", host_ssid, "password", host_password],
#                         check=False)
#         time.sleep(1)

#     print("Creating Socket")
#     get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     print("Connecting to Host for Port")
#     get_socket.connect((Host_IP, 7000))
#     print("Connected to Port 7000")
#     print("Asking for Port")
#     port = int(get_socket.recv(65535).decode())
#     print("Received Data Port:", port)
#     get_socket.close()
#     print("Closed Asking Port")
#     print("Creating Socket for UDP")
#     data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     print("Creating Camera")
#     cam = Picamera2()
#     print("Camera Created")
#     print("Configuring Camera")
#     cam.preview_configuration.main.size = (3280, 2464)
#     # cam.preview_configuration.main.size = (2592, 1944)
#     cam.preview_configuration.main.format = "RGB888"
#     cam.configure("preview")
#     print("Camera Configured")
#     print("Starting Camera")
#     cam.start()
#     print("Camera Started")
#     time.sleep(0.5)
#     threading.Thread(target=check_stop).start()
#     blinking_time = datetime.datetime.now()
#     led_on = True
#     subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
#     try:
#         while not stop:
#             while recording:
#                 print("Capturing")
#                 frame = cam.capture_array()
#                 frame = frame[0:2464, 410:2870] 
#                 # 0.75 2460 410 2870
#                 # 0.75 1944 324 2268
#                 # frame = frame[0:1944, 324:2268]
#                 print("Encoding")
#                 _, encoded = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
#                 encoded_bytes = encoded.tobytes() + b"end"
#                 print("Sending\n")
#                 for i in range(0, len(encoded_bytes), 1024):
#                     data_socket.sendto(encoded_bytes[i:i+1024], (Host_IP, port))
#                 if((datetime.datetime.now()-blinking_time).total_seconds() > 1):
#                     if(led_on):
#                         subprocess.run("echo 0 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
#                         led_on = False
#                         blinking_time = datetime.datetime.now()
#                     else:
#                         subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
#                         led_on = True
#                         blinking_time = datetime.datetime.now()
#     except Exception as e:
#         print("Capturing Got Error: ", e)
#     data_socket.sendto(b"c", (Host_IP, port))
#     cam.stop()
#     cam.close()
#     data_socket.close()
#     GPIO.cleanup()
#     # subprocess.run(["sudo", "nmcli", "connection", "delete", "static_rpicamlab"], check=False)

# recording = False
# stop = False
# def check_stop():
#     global recording
#     global stop
#     print("Creating Assigning Socket")
#     command_listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     print("Assigning Socket Created")
#     print("Binding Socket to Port", 7000)
#     command_listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     command_listening_socket.bind(("", 7000))
#     print("Binded Socket")
#     command_listening_socket.listen(10)
#     print("Waiting for Command From Server to Start")
#     command_socket, server_adr = command_listening_socket.accept()
#     command_socket.send(b"namehi")
#     while True:
#         data = command_socket.recv(65535).decode()
#         if data == "start":
#             print("Received Command to Start Recording")
#             recording = True
#         elif data == "stop":
#             print("Received Command to Stop Recording")
#             recording = False
#         else:
#             print("Received Command to Stop Program")
#             stop = True
#             time.sleep(0.5)
#             exit(0)

# # while True:
# # while GPIO.input(3) != GPIO.HIGH:
# #     time.sleep(0.2)
# # print("Starting, Remove from Pin to Stop\n")\
# main()
#!/usr/bin/env python3
import socket
import time
import subprocess
import threading
import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls

# ------------- configuration -------------
CENTRAL_IP = "10.42.0.1"     # change if your central host has a different IP
ASSIGN_PORT = 7000           # central's assigner TCP port
CMD_LISTEN_PORT = 7000       # camera's command TCP port (on the CAMERA host)
CAMERA_NAME = "rpi-camera"

# ------------- camera helpers -------------
def start_camera():
    cam = Picamera2()
    # basic 640x480 MJPEG-ish workflow (we'll still jpeg-encode below)
    config = cam.create_preview_configuration({"size": (640, 480)})
    cam.configure(config)
    cam.set_controls({controls.AeEnable: True, controls.AwbEnable: True})
    cam.start()
    time.sleep(0.5)
    return cam

def capture_jpeg(cam):
    # grab frame as RGB and encode to JPEG
    frame = cam.capture_array()          # RGB
    # Encode JPEG
    ret, buf = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    if not ret:
        return None
    return buf.tobytes()

# ------------- command server -------------
recording = False
stop_flag = False

def command_server():
    """Listen on TCP 7000 for central, send name once, then accept 'start'/'stop'/'quit'."""
    global recording, stop_flag
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", CMD_LISTEN_PORT))
    srv.listen(1)
    print("[camera] Command server listening on", CMD_LISTEN_PORT)

    conn, addr = srv.accept()
    print("[camera] Command connection from", addr)
    try:
        conn.sendall(CAMERA_NAME.encode())
        while True:
            data = conn.recv(65535)
            if not data:
                break
            msg = data.decode(errors="ignore").strip().lower()
            if msg == "start":
                print("[camera] start")
                recording = True
            elif msg == "stop":
                print("[camera] stop")
                recording = False
            elif msg == "quit":
                print("[camera] quit")
                stop_flag = True
                break
    finally:
        try:
            conn.close()
        except Exception:
            pass
        try:
            srv.close()
        except Exception:
            pass
        print("[camera] Command server closed")

# ------------- main streaming logic -------------
def main():
    global recording, stop_flag

    # Ensure we're on the correct Wi‑Fi (optional, user may manage externally)
    try:
        cur = subprocess.check_output(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], text=True)
        if "yes:" not in cur:
            subprocess.run(["nmcli", "radio", "wifi", "on"], check=False)
            subprocess.run(["nmcli", "dev", "wifi", "rescan"], check=False)
    except Exception:
        pass

    # Start command server first so central can connect back promptly
    threading.Thread(target=command_server, daemon=True).start()

    # Connect to central to obtain assigned UDP port
    print("[camera] Connecting to central assigner", (CENTRAL_IP, ASSIGN_PORT))
    assign_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    assign_sock.settimeout(10.0)
    assign_sock.connect((CENTRAL_IP, ASSIGN_PORT))
    udp_port = int(assign_sock.recv(32).decode().strip())
    assign_sock.close()
    print("[camera] Assigned UDP port", udp_port)

    # Prepare UDP sender
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Start camera
    cam = start_camera()
    print("[camera] Camera started; waiting for 'start' from central")

    try:
        last = time.time()
        while not stop_flag:
            if not recording:
                time.sleep(0.01)
                continue
            # capture and send
            jpeg = capture_jpeg(cam)
            if jpeg is None:
                continue

            # Chunk into ~1000-byte datagrams and add 'end' sentinel
            CHUNK = 1000
            for i in range(0, len(jpeg), CHUNK):
                data_socket.sendto(jpeg[i:i+CHUNK], (CENTRAL_IP, udp_port))
            data_socket.sendto(b"end", (CENTRAL_IP, udp_port))

            # ~30 fps budget
            dt = time.time() - last
            if dt < (1.0 / 30.0):
                time.sleep((1.0/30.0) - dt)
            last = time.time()

    except Exception as e:
        print("[camera] streaming error:", e)
    finally:
        try:
            data_socket.sendto(b"c", (CENTRAL_IP, udp_port))
        except Exception:
            pass
        try:
            cam.stop()
            cam.close()
        except Exception:
            pass
        try:
            data_socket.close()
        except Exception:
            pass
        print("[camera] shutdown")

if __name__ == "__main__":
    print("Camera Program Started")
    main()

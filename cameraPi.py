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
#     # cam.preview_configuration.main.size = (3280, 2464)
#     cam.preview_configuration.main.size = (2592, 1944)
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
#                 # frame = frame[0:2464, 410:2870] 
#                 # 0.75 2460 410 2870
#                 # 0.75 1944 324 2268
#                 frame = frame[0:1944, 324:2268]
#                 print("Encoding")
#                 _, encoded = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
#                 encoded_bytes = encoded.tobytes() + b"end"
#                 print("Sending\n")
#                 for i in range(0, len(encoded_bytes), 1400):
#                     data_socket.sendto(encoded_bytes[i:i+1400], (Host_IP, port))
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

# -------- Config --------
HOST_SSID = "rpicamlab"       # optional auto-connect
HOST_PASS = "rpicamlab"
CENTRAL_IP = "10.42.0.1"      # set this to your central's IP
ASSIGN_PORT = 7000            # central assign TCP
CMD_LISTEN_PORT = 7000        # this camera's command TCP
CAMERA_NAME = "rpi-camera"
CHUNK = 1400                  # <= 1472 to avoid Wi-Fi fragmentation
FPS = 30
JPEG_QUALITY = 75             # lower -> smaller packets -> faster

recording = False
stop_flag = False

def ensure_wifi():
    """Optional: try to connect to known SSID if not already connected."""
    try:
        cur = subprocess.check_output(["iwgetid", "-r"], text=True).strip()
        if cur == HOST_SSID:
            return
    except Exception:
        pass
    try:
        subprocess.run(["nmcli", "dev", "disconnect", "wlan0"], check=False)
        subprocess.run(["nmcli", "dev", "wifi", "rescan"], check=False)
        subprocess.run(["nmcli", "dev", "wifi", "connect", HOST_SSID, "password", HOST_PASS], check=False)
    except Exception:
        pass

def start_camera():
    cam = Picamera2()
    # Use a fast preview configuration (720p is a good default for streaming)
    config = cam.create_preview_configuration(main={"size": (1280, 720), "format": "RGB888"})
    cam.configure(config)
    cam.set_controls({
        controls.AeEnable: True,
        controls.AwbEnable: True,
        # Optional: limit frame duration to target FPS
        # controls.FrameDurationLimits: (int(1e6/FPS), int(1e6/FPS)),
    })
    cam.start()
    time.sleep(0.2)
    return cam

def encode_jpeg(rgb_frame):
    # Convert RGB (picamera2) to BGR for OpenCV encoder
    bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
    if not ok:
        return None
    return buf.tobytes()

def command_server():
    """Listen on TCP 7000 and accept 'start'/'stop'/'quit'."""
    global recording, stop_flag
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", CMD_LISTEN_PORT))
    srv.listen(1)
    conn, addr = srv.accept()
    try:
        conn.sendall(CAMERA_NAME.encode())
        while True:
            data = conn.recv(65535)
            if not data:
                break
            msg = data.decode(errors="ignore").strip().lower()
            if msg == "start":
                recording = True
            elif msg == "stop":
                recording = False
            elif msg == "quit":
                stop_flag = True
                break
    finally:
        try: conn.close()
        except Exception: pass
        try: srv.close()
        except Exception: pass

def main():
    global recording, stop_flag

    ensure_wifi()

    # Start command server first so central can connect back immediately
    threading.Thread(target=command_server, daemon=True).start()

    # Connect to central assigner and get UDP port
    assign = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    assign.settimeout(10.0)
    assign.connect((CENTRAL_IP, ASSIGN_PORT))
    udp_port = int(assign.recv(64).decode().strip())
    assign.close()

    # UDP sender
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    cam = start_camera()
    print("[camera] ready; waiting for 'start'")

    try:
        prev = time.time()
        while not stop_flag:
            if not recording:
                time.sleep(0.005)
                continue
            # capture & encode
            rgb = cam.capture_array()           # RGB888
            jpg = encode_jpeg(rgb)
            if jpg is None:
                continue
            # send in CHUNK-sized slices + 'end' sentinel
            for i in range(0, len(jpg), CHUNK):
                udp.sendto(jpg[i:i+CHUNK], (CENTRAL_IP, udp_port))
            udp.sendto(b"end", (CENTRAL_IP, udp_port))

            # pace to target FPS
            delay = (1.0 / FPS) - (time.time() - prev)
            if delay > 0:
                time.sleep(delay)
            prev = time.time()
    except Exception as e:
        print("[camera] error:", e)
    finally:
        try: udp.sendto(b"c", (CENTRAL_IP, udp_port))
        except Exception: pass
        try: cam.stop(); cam.close()
        except Exception: pass
        try: udp.close()
        except Exception: pass
        print("[camera] shutdown"])

if __name__ == "__main__":
    print("Camera Program Started")
    main()

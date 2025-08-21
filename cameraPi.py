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
#     global streaming
#     global stream
#     host_ssid = "rpicamlab"
#     host_password = "rpicamlab"
#     ssids = []
#     Host_IP = "10.42.0.1"
#     while True:
#         try:
#             if subprocess.check_output(["sudo", "iwgetid", "-r"], encoding="utf-8").strip() == host_ssid:
#                 print(f"Connected to {host_ssid}")
#                 break
#             subprocess.run(["nmcli", "dev", "disconnect", "wlan0"], check=False)
#             subprocess.run(["nmcli", "dev", "wifi", "rescan"], check=False)
#             subprocess.run(["sudo","nmcli","dev","wifi","connect", host_ssid, "password", host_password],
#                             check=False)
#         except:
#             print("Not Connected")
#         # Ask NM to connect (it will rescan if needed)
        
#         time.sleep(1)

#     print("Creating Socket")
#     get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     print("Connecting to Host for Port")
#     while True:
#         try:
#             get_socket.connect((Host_IP, 7000))
#             break
#         except:
#             pass
#     print("Connected to Port 7000")
#     print("Asking for Port")
#     port = int(get_socket.recv(65535).decode())
#     print("Received Data Port:", port)
#     get_socket.close()
#     print("Closed Asking Port")
#     print("Creating Socket for UDP")
#     data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     # print("Creating Camera")
#     # cam = Picamera2()
#     # print("Camera Created")
#     # print("Configuring Camera")
#     # cam.preview_configuration.main.size = (3280, 2464)
#     # # cam.preview_configuration.main.size = (2592, 1944)
#     # cam.preview_configuration.main.format = "RGB888"
#     # cam.configure("preview")
#     # print("Camera Configured")
#     # print("Starting Camera")
#     # cam.start()
#     # print("Camera Started")
#     time.sleep(0.5)
#     threading.Thread(target=check_stop).start()
#     blinking_time = datetime.datetime.now()
#     led_on = True
#     subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
#     try:
#         while not stop:
#             if (streaming):
#                 stream.stop()
#                 # stream[1].stop()
#                 streaming = False
#             while recording:
#                 if (not streaming):
#                     stream = start_stream(Host_IP, port)
                
#             #     print("Capturing")
#             #     frame = cam.capture_array()
#             #     frame = frame[0:2464, 410:2870] 
#             #     # 0.75 2460 410 2870
#             #     # 0.75 1944 324 2268
#             #     # frame = frame[0:1944, 324:2268]
#             #     print("Encoding")
#             #     _, encoded = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),  [int(cv2.IMWRITE_JPEG_QUALITY), 75])
#             #     encoded_bytes = encoded.tobytes() + b"end"
#             #     print("Sending\n")
#             #     for i in range(0, len(encoded_bytes), 1400):
#             #         data_socket.sendto(encoded_bytes[i:i+1400], (Host_IP, port))
#             #     if((datetime.datetime.now()-blinking_time).total_seconds() > 1):
#             #         if(led_on):
#             #             subprocess.run("echo 0 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
#             #             led_on = False
#             #             blinking_time = datetime.datetime.now()
#             #         else:
#             #             subprocess.run("echo 1 | sudo tee /sys/class/leds/ACT/brightness", shell=True)
#             #             led_on = True
#             #             blinking_time = datetime.datetime.now()
#     except Exception as e:
#         print("Capturing Got Error: ", e)
#     data_socket.sendto(b"c", (Host_IP, port))
#     # cam.stop()
#     # cam.close()
#     data_socket.close()
#     GPIO.cleanup()
#     # subprocess.run(["sudo", "nmcli", "connection", "delete", "static_rpicamlab"], check=False)

# streaming = False
# stream = None
# def start_stream(ip, port):
#     global streaming
#     streaming = True
#     # Use the Raspberry Pi camera via v4l2 (check your device path, often /dev/video0)
#     cmd = [
#         "ffmpeg",
#         "-f", "v4l2",
#         "-framerate", "30",
#         "-video_size", "640x480",
#         "-i", "/dev/video0",
#         "-c:v", "h264_v4l2m2m",
#         "-b:v", "2M",
#         "-f", "mpegts",
#         f"udp://{ip}:{str(port)}?pkt_size=1316"
#     ]
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)



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
    global streaming_process
    host_ssid = "rpicamlab"
    host_password = "rpicamlab"
    Host_IP = "10.42.0.1"

    # Simplified network connection logic
    while True:
        try:
            if subprocess.check_output(["sudo", "iwgetid", "-r"], encoding="utf-8").strip() == host_ssid:
                print(f"Connected to {host_ssid}")
                break
            print("Attempting to connect to WiFi...")
            subprocess.run(["sudo","nmcli","dev","wifi","connect", host_ssid, "password", host_password], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("Not Connected, retrying...")
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(2)

    # TCP Socket to get the designated port
    print("Creating Socket to get port")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as get_socket:
        while True:
            try:
                get_socket.connect((Host_IP, 7000))
                break
            except socket.error:
                time.sleep(1)
        print("Connected to Port 7000")
        port = int(get_socket.recv(1024).decode())
        print("Received Data Port:", port)

    # Start the command listener thread
    threading.Thread(target=command_listener, args=(Host_IP, port), daemon=True).start()

    # Main loop to keep the script alive
    try:
        while not stop_program:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        if streaming_process:
            streaming_process.terminate()
            streaming_process.wait()
        GPIO.cleanup()
        print("Program Finished.")

streaming_process = None
stop_program = False

def start_stream(ip, port):
    global streaming_process
    if streaming_process: # If a stream is already running, do nothing
        return
    print("Starting ffmpeg stream...")
    cmd = [
        "ffmpeg",
        "-f", "v4l2",
        "-framerate", "30",
        "-video_size", "640x480",
        "-i", "/dev/video0",
        "-c:v", "h264_v4l2m2m", # Hardware accelerated encoding
        "-b:v", "2M",
        "-f", "mpegts",
        f"udp://{ip}:{port}?pkt_size=1316"
    ]
    # Start the ffmpeg process
    streaming_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_stream():
    global streaming_process
    if streaming_process:
        print("Stopping ffmpeg stream...")
        streaming_process.terminate()
        try:
            streaming_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streaming_process.kill()
        streaming_process = None

def command_listener(ip, port):
    global stop_program
    # This socket is for receiving commands like start/stop
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as command_socket:
        while True:
            try:
                command_socket.connect((ip, 7000))
                break
            except socket.error:
                time.sleep(1)
        
        command_socket.send(b"name:PiCam1") # Send a name or identifier

        while True:
            try:
                data = command_socket.recv(1024).decode()
                if not data:
                    break
                if data == "start":
                    print("Received Command to Start Recording")
                    start_stream(ip, port)
                elif data == "stop":
                    print("Received Command to Stop Recording")
                    stop_stream()
                elif data == "shutdown":
                    print("Received command to stop program.")
                    stop_stream()
                    stop_program = True
                    break
            except ConnectionResetError:
                print("Connection to central server lost.")
                break
    print("Command listener thread finished.")


if __name__ == "__main__":
    main()
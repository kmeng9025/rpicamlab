# import socket
# import threading
# import subprocess
# import os
# import errno
# import numpy
# import cv2
# import tkinter
# from PIL import Image, ImageTk
# from functools import partial
# import time


# used_ports = {}
# change_buttons = []
# buttons = {}
# server_socket = None
# stop = False
# window = "m"
# streaming_cameras = []

# queue = {}
# root_window = tkinter.Tk()
# root_window.title("Camera Control")
# root_window.geometry("600x600")

# def main():
#     # threading.Thread(target=listen_for_exit).start()
#     threading.Thread(target=listener).start()
#     initialize_main_window()
#     root_window.mainloop()
#     # display_video()
        

# def initialize_main_window():
#     text_camera = tkinter.Label(root_window, text="Cameras")
#     text_camera.place(x=10, y=30)
#     for i in buttons.keys():
#         buttons[i].pack()
#     periodic_main_window()


# def periodic_main_window():
#     for i in change_buttons:
#         if(i[2]):
#             button = tkinter.Button(root_window, text=i[1], command=partial(camera_clicked, i[0], i[1]))
#             buttons[i[0]] = button
#             button.pack()
#             change_buttons.pop(0)
#         else:
#             buttons.pop(i[0])
#     if window == "m":
#         root_window.after(10, periodic_main_window)
    

# def camera_clicked(port, name):
#     global window
#     print("Camera clicked", port, name)
#     window = "c"
#     root_window.title("Camera " + str(name))
#     buttonStream = tkinter.Button(root_window, text="Stream camera", command=partial(start_video, port))
#     buttonStream.pack()


# def start_video(port):
#     global window
#     global video_label
#     window = "v"
#     video_label = tkinter.Label(root_window)
#     video_label.place(x=0, y=0)
#     # cv2.imshow(" stream", queue[i][-1])
#     streaming_cameras.append(port)
#     display_video(port)


# def display_video(port):
#     try:
#         image = Image.fromarray(queue[port][-1])
#         image_tk = ImageTk.PhotoImage(image=image)
#         video_label.config(image=image_tk)
#         video_label.image = image_tk
#         queue[port].pop(-1)
#         queue[port] = []
#     except Exception as e:
#         print("display video error", e)
#     if(window == "v"):
#             root_window.after(10, partial(display_video, port))


# def listener():
#     global server_socket
#     binding_socket = 7000
#     print("Creating Assigning Socket")
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     print("Assigning Socket Created")
#     print("Binding Socket to Port", binding_socket)
#     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     server_socket.bind(("", binding_socket))
#     print("Binded Socket")
#     server_socket.listen(10)
#     current_port = binding_socket + 1
#     print("Starting Listener")
#     while True:
#         print("Waiting for Camera Pi")
#         client_socket, client_address = server_socket.accept()
#         print("Received Connection")
#         print("Assigning Port")
#         while (is_port_in_use(current_port)):
#             if(current_port == 65535):
#                 current_port = 0
#             current_port += 1
#         print("Found Available Port:", current_port)
#         print("Assigning Available Port:", current_port)
#         client_socket.send(str(current_port).encode())
#         # name = client_socket.recv(65535).decode()
#         print("Assigned Available Port")
#         print("Closing Camera Pi Assigning Socket")
#         client_socket.close()
#         print("Closed Camera Pi Assigning Socket")
#         print("Creating New Thread for Port:", current_port)
#         client_thread = threading.Thread(target=open_port, args=(current_port, client_address))
#         # open_port(current_port)
#         print("Created New Thread for Streaming")
#         print("Starting Streaming Thread")
#         client_thread.start()
#         print("Started Streaming Thread")


# # def listen_for_exit():
# #     while True:
        


# def clean_up():
#     global stop
#     print("CLEANING UP")
#     stop = True
#     try:
#         server_socket.close()
#     except:
#         pass
#     exit(0)


# def open_port(port, client_address):
#     global used_ports
#     print(port, "In New Streaming Thread Port")
#     print(port, "Creating UDP Streaming Socket")
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     print(port, "Created UDP Streaming socket")
#     print(port, "Binding Streaming Socket to Port")
#     client_socket.bind(("0.0.0.0", port))
#     print(port, "Binded Streaming to Port")
#     # print("Binding to Camera Command Port")
#     command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # print("Binded to Camera Command Port")
#     print("Connecting to Client")
#     time.sleep(1)
#     command_socket.connect((client_address[0], 7000))
#     print("Connected to Client Command Port")
#     print("Receiving Name from Client")
#     name = command_socket.recv(65535).decode()
#     used_ports[port] = (name)
#     change_buttons.append((port, name, True))
#     print("Name Received")
#     print("DEBUGGING, SENDING START IMMEDIATELY")
#     command_socket.send(b"start")
#     frame_data = bytearray()
#     print(port, "Starting Receiving Loop")
#     dropped = False
#     queue[port] = []
#     try:
#         while not stop:
#             print(port, "Waiting for Data")
#             data, adr = client_socket.recvfrom(1024)
#             print(port, "Data Received")
#             print(port, "Data Length:", len(data))
#             if not data:
#                 print("bad")
#             frame_data.extend(data)
#             if frame_data.endswith(b"end"):
#                 print(port, "Received End of Frame")
#                 print(port, "Decoding Frame")
#                 if dropped:
#                     frame_data = bytearray()
#                     dropped = False
#                     continue
#                 np_data = numpy.frombuffer(frame_data.removesuffix(b"end"), dtype=numpy.uint8)
#                 image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
#                 if (image is not None):
#                     print(port, "Frame Is Good")
#                     if(streaming_cameras.count(port) != 0):
#                         queue[port].append(image)
#                 else:
#                     print(port, "Dropped Frame")
#                 frame_data = bytearray()
#             elif (frame_data.endswith(b"c") and len(frame_data) == 1):
#                 print(port, "Received Request To Close Streaming Port")
#                 print(port, "Closing Port")
#                 client_socket.close()
#                 used_ports.pop(port)
#                 print(port, "Closed Port")
#                 break
#     except:
#         print("Port disconnected")
#     used_ports[port] = ""
#     change_buttons.append((port, name, False))
#     command_socket.send(b"stop")
#     command_socket.close()
#     client_socket.close()


# def is_port_in_use(port):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         try:
#             s.bind(("0.0.0.0", port))
#         except socket.error as e:
#             return True
#     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#         try:
#             s.bind(("0.0.0.0", port))
#             return False
#         except socket.error as e:
#             return True

# print("Central Program Started")
# main()

#!/usr/bin/env python3
import socket
import threading
import subprocess
import os
import errno
import tkinter as tk
from functools import partial
from PIL import Image, ImageTk
import numpy as np
import cv2

# ---------------------- globals ----------------------
used_ports = {}                   # {port: camera_name}
buttons = {}                      # {port: tk.Button}
change_buttons = []               # [(port, name, added_bool)]
queue = {}                        # {port: [np.ndarray(BGR frame), ...]}
streaming_cameras = []            # [port, ...]

server_socket = None
stop = False
window = "m"                      # 'm' main, 'v' video

# Tk UI
root_window = tk.Tk()
root_window.title("Camera Control")
video_label = tk.Label(root_window)
video_label.place(x=0, y=0)

# ---------------------- UI ----------------------
def initialize_main_window():
    text_camera = tk.Label(root_window, text="Cameras", font=("Arial", 14, "bold"))
    text_camera.place(x=10, y=10)
    root_window.after(100, periodic_main_window)

def periodic_main_window():
    # Drain cross-thread UI actions
    while change_buttons:
        port, name, added = change_buttons.pop(0)
        if added:
            if port not in buttons:
                btn = tk.Button(root_window, text=f"{name} ({port})", command=partial(camera_clicked, port, name))
                buttons[port] = btn
                # stack buttons vertically under the title
                # compute y offset as 40 + index*35
                idx = len(buttons) - 1
                btn.place(x=10, y=40 + idx * 35)
        else:
            btn = buttons.pop(port, None)
            if btn:
                btn.destroy()
                # reflow the remaining buttons
                for idx, (p, b) in enumerate(buttons.items()):
                    b.place(x=10, y=40 + idx * 35)
    # keep polling in main window
    if window == "m":
        root_window.after(100, periodic_main_window)

def camera_clicked(port, name):
    global window
    print("Camera clicked", port, name)
    window = "c"
    root_window.title(f"Camera {name}")
    # show a simple control area
    start_btn = tk.Button(root_window, text="Stream camera", command=partial(start_video, port))
    start_btn.place(x=150, y=10)

def start_video(port):
    global window, video_label
    window = "v"
    # ensure queue key exists
    queue.setdefault(port, [])
    # make sure the label exists
    if not isinstance(video_label, tk.Label):
        video_label = tk.Label(root_window)
    video_label.place(x=200, y=40)
    if port not in streaming_cameras:
        streaming_cameras.append(port)
    display_video(port)

def display_video(port):
    try:
        frames = queue.get(port, [])
        if frames:
            frame_bgr = frames.pop()  # last frame
            # Convert BGR (OpenCV) to RGB (PIL)
            try:
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            except Exception:
                frame_rgb = frame_bgr  # if already RGB
            image = Image.fromarray(frame_rgb)
            image_tk = ImageTk.PhotoImage(image=image)
            video_label.config(image=image_tk)
            video_label.image = image_tk  # keep reference
            frames.clear()  # keep only the freshest
    except Exception as e:
        print("display_video error:", e)
    if window == "v":
        root_window.after(15, partial(display_video, port))

# ---------------------- networking ----------------------
def listener():
    """Accept camera connections, assign UDP port, then spawn a receiver thread and connect command socket."""
    global server_socket
    binding_socket = 7000
    print("Creating Assigning Socket")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Binding Socket to Port", binding_socket)
    server_socket.bind(("", binding_socket))
    server_socket.listen(10)
    current_port = binding_socket + 1
    print("Started listener on TCP", binding_socket)

    while not stop:
        try:
            print("Waiting for Camera Pi")
            client_socket, client_address = server_socket.accept()
            cam_ip = client_address[0]
            print("Received connection from", cam_ip)

            # find a free UDP port
            while is_port_in_use(current_port):
                current_port += 1
                if current_port > 65535:
                    current_port = 1025
            print("Assigning Available Port:", current_port)

            # send the port as text
            try:
                client_socket.send(str(current_port).encode())
            finally:
                client_socket.close()

            # start UDP receiver thread for this camera
            client_thread = threading.Thread(target=open_port, args=(current_port, cam_ip), daemon=True)
            client_thread.start()

            # advance baseline for next
            current_port += 1
        except Exception as e:
            print("listener error:", e)

def open_port(port, client_ip):
    """Bind UDP port and receive JPEG frames delimited by 'end' sentinel. Maintain command TCP channel to camera:7000."""
    print(port, "Starting streaming thread")
    # UDP socket for video data
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.bind(("0.0.0.0", port))
    udp_sock.settimeout(3.0)

    # TCP command channel to camera
    cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(port, "Connecting to camera command channel at", client_ip, "7000")
        cmd_sock.settimeout(5.0)
        cmd_sock.connect((client_ip, 7000))
        # receive camera name
        name = cmd_sock.recv(65535).decode(errors="ignore").strip() or f"Camera@{client_ip}"
        used_ports[port] = name
        change_buttons.append((port, name, True))
        print(port, "Camera name:", name)

        # ask camera to start streaming
        try:
            cmd_sock.sendall(b"start")
        except Exception as e:
            print(port, "failed to send start:", e)
    except Exception as e:
        print(port, "command channel error:", e)
        name = f"Camera@{client_ip}"
        used_ports[port] = name
        change_buttons.append((port, name, True))

    frame_data = bytearray()
    dropped = False
    queue.setdefault(port, [])

    try:
        while not stop:
            try:
                data, adr = udp_sock.recvfrom(4096)
            except socket.timeout:
                # no data for a while; keep waiting
                continue
            if not data:
                continue

            # Close signal: a single 'c'
            if data == b"c":
                print(port, "Received request to close streaming port")
                break

            frame_data.extend(data)

            if frame_data.endswith(b"end"):
                # complete frame received
                raw = frame_data[:-3]  # strip 'end'
                frame_data.clear()

                # Drop too-large frames (very rare with UDP reordering)
                if dropped:
                    dropped = False
                    continue

                # decode to image (BGR)
                try:
                    np_data = np.frombuffer(raw, dtype=np.uint8)
                    image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                    if image is not None:
                        # Only store if this camera is selected to stream (optional: uncomment to throttle)
                        # if port in streaming_cameras:
                        queue[port].append(image)
                    else:
                        print(port, "Dropped frame (imdecode returned None)")
                except Exception as e:
                    print(port, "Decode error:", e)
    except Exception as e:
        print(port, "Stream loop error:", e)
    finally:
        try:
            cmd_sock.sendall(b"stop")
        except Exception:
            pass
        try:
            cmd_sock.close()
        except Exception:
            pass
        try:
            udp_sock.close()
        except Exception:
            pass
        # UI cleanup
        change_buttons.append((port, used_ports.get(port, f"Camera@{client_ip}"), False))
        used_ports.pop(port, None)
        print(port, "Closed streaming thread")

def clean_up():
    global stop
    print("CLEANING UP")
    stop = True
    try:
        server_socket.close()
    except Exception:
        pass
    os._exit(0)

def is_port_in_use(port):
    # Check both TCP and UDP availability
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
        except socket.error:
            return True
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return False
        except socket.error:
            return True

# ---------------------- main ----------------------
def main():
    threading.Thread(target=listener, daemon=True).start()
    initialize_main_window()
    root_window.protocol("WM_DELETE_WINDOW", clean_up)
    root_window.geometry("960x600")
    root_window.mainloop()

if __name__ == "__main__":
    print("Central Program Started")
    main()

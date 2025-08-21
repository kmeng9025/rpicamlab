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
#         image = Image.fromarray(queue[port][-1]).resize((500, 500))
#         image_tk = ImageTk.PhotoImage(image=image)
#         video_label.config(image=image_tk)
#         video_label.image = image_tk
#         queue[port].pop(-1)
#         queue[port] = []
#     except Exception as e:
#         print("display video error", e)
#     if(window == "v"):
#         root_window.after(10, partial(display_video, port))


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
#             data, adr = client_socket.recvfrom(1400)
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
import os
import tkinter as tk
from functools import partial
from collections import deque
from PIL import Image, ImageTk
import numpy as np
import cv2
import time

# ----------------- Globals -----------------
used_ports = {}                   # {port: camera_name}
cmd_socks = {}                    # {port: TCP command socket}
latest_jpeg = {}                  # {port: deque(maxlen=1) of bytes}  (store compressed JPEG to reduce CPU)
server_socket = None
stop = False

# UI state
CURRENT_PORT = None
root = tk.Tk()
root.title("Camera Control")
root.geometry("960x640")

# Simple layout: header + content
header = tk.Frame(root)
header.pack(side="top", fill="x")
content = tk.Frame(root)
content.pack(side="top", fill="both", expand=True)

title_lbl = tk.Label(header, text="Cameras", font=("Arial", 14, "bold"))
title_lbl.pack(side="left", padx=10, pady=6)

btn_back = tk.Button(header, text="Back", command=lambda: show_main())
btn_exit = tk.Button(header, text="Exit", command=lambda: clean_up())

# ----------------- UI helpers -----------------
def clear_content():
    for w in content.winfo_children():
        w.destroy()

def show_main():
    global CURRENT_PORT
    CURRENT_PORT = None
    title_lbl.config(text="Cameras")
    btn_back.pack_forget()    # only show Back outside main
    btn_exit.pack(side="right", padx=8, pady=6)
    clear_content()

    # Build/refresh camera buttons
    y = 10
    for port, name in sorted(used_ports.items()):
        tk.Button(content, text=f"{name} ({port})",
                  command=partial(show_camera_controls, port, name),
                  width=28).place(x=10, y=y)
        y += 40

def show_camera_controls(port, name):
    global CURRENT_PORT
    CURRENT_PORT = port
    title_lbl.config(text=f"Camera: {name}")
    btn_back.pack(side="left", padx=8, pady=6)
    btn_exit.pack(side="right", padx=8, pady=6)
    clear_content()

    tk.Button(content, text="Start stream", width=18,
              command=partial(start_stream, port)).place(x=10, y=10)
    tk.Button(content, text="Stop stream", width=18,
              command=partial(stop_stream, port)).place(x=150, y=10)
    tk.Button(content, text="Open viewer", width=18,
              command=partial(show_stream_view, port)).place(x=290, y=10)

def show_stream_view(port):
    title_lbl.config(text=f"Streaming: {used_ports.get(port, port)}")
    btn_back.config(command=lambda: back_from_stream(port))
    btn_back.pack(side="left", padx=8, pady=6)
    btn_exit.pack(side="right", padx=8, pady=6)
    clear_content()

    # video label
    video = tk.Label(content)
    video.pack(side="left", padx=10, pady=10)

    # Controls on the right
    ctrl = tk.Frame(content)
    ctrl.pack(side="left", fill="y", padx=10, pady=10)
    tk.Button(ctrl, text="Stop stream", command=partial(stop_stream, port), width=14).pack(pady=4)
    tk.Button(ctrl, text="Back to cameras", command=lambda: back_from_stream(port), width=14).pack(pady=4)
    tk.Button(ctrl, text="Exit", command=clean_up, width=14).pack(pady=4)

    # Start the update loop
    def update_frame():
        dq = latest_jpeg.get(port)
        if dq and len(dq) > 0:
            jpg = dq[-1]
            try:
                arr = np.frombuffer(jpg, dtype=np.uint8)
                frame_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if frame_bgr is not None:
                    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img_tk = ImageTk.PhotoImage(img)
                    video.config(image=img_tk)
                    video.image = img_tk
            except Exception as e:
                print("display decode error:", e)
        # keep refreshing at ~30 fps
        if CURRENT_PORT == port:
            root.after(33, update_frame)

    update_frame()

def back_from_stream(port):
    # Leave the stream view; do not necessarily stop the stream (user can choose)
    show_camera_controls(port, used_ports.get(port, str(port)))

# ----------------- Networking -----------------
def listener():
    """Accept camera connections, assign unique UDP ports, and spawn receiver threads."""
    global server_socket
    bind_port = 7000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", bind_port))
    server_socket.listen(10)
    print("[central] listening on TCP", bind_port)

    next_udp = bind_port + 1
    while not stop:
        try:
            client_sock, client_addr = server_socket.accept()
            cam_ip = client_addr[0]
            # Find free UDP port
            while is_port_in_use(next_udp):
                next_udp += 1
                if next_udp >= 65535:
                    next_udp = 1025
            # Send UDP port to camera
            client_sock.send(str(next_udp).encode())
            client_sock.close()

            # Start receiver thread
            th = threading.Thread(target=receiver_thread, args=(next_udp, cam_ip), daemon=True)
            th.start()

            next_udp += 1
        except Exception as e:
            if not stop:
                print("[central] accept error:", e)

def receiver_thread(port, cam_ip):
    """Receive UDP JPEG frames terminated by 'end'. Keep only latest compressed frame for display."""
    print(f"[central:{port}] starting receiver from {cam_ip}")
    # UDP socket
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(("0.0.0.0", port))
    udp.settimeout(3.0)

    # Command socket
    cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cmd.settimeout(5.0)
    name = f"Camera@{cam_ip}"
    try:
        time.sleep(0.5)  # small grace for the camera to open its listener
        cmd.connect((cam_ip, 7000))
        got = cmd.recv(65535)
        if got:
            name = got.decode(errors="ignore").strip() or name
        used_ports[port] = name
        latest_jpeg[port] = deque(maxlen=1)
        cmd_socks[port] = cmd
        # Start stream automatically
        try:
            cmd.sendall(b"start")
        except Exception:
            pass
        # Refresh main view title in UI thread
        root.after(0, show_main)
        print(f"[central:{port}] connected to command channel; name={name}")
    except Exception as e:
        print(f"[central:{port}] command channel error:", e)
        used_ports[port] = name
        latest_jpeg[port] = deque(maxlen=1)
        root.after(0, show_main)

    frame = bytearray()
    try:
        while not stop:
            try:
                pkt, _ = udp.recvfrom(2048)   # matches camera chunk size (<= ~1400 recommended; 2048 okay)
            except socket.timeout:
                continue
            if not pkt:
                continue
            if pkt == b"c":
                break
            frame.extend(pkt)
            # complete frame?
            if len(frame) >= 3 and frame[-3:] == b"end":
                jpg = bytes(frame[:-3])
                frame.clear()
                dq = latest_jpeg.get(port)
                if dq is not None:
                    dq.append(jpg)  # keep only latest via maxlen=1
    except Exception as e:
        if not stop:
            print(f"[central:{port}] receiver error:", e)
    finally:
        # tidy
        try:
            if cmd_socks.get(port):
                try:
                    cmd_socks[port].sendall(b"stop")
                except Exception:
                    pass
                cmd_socks[port].close()
        except Exception:
            pass
        try:
            udp.close()
        except Exception:
            pass
        used_ports.pop(port, None)
        latest_jpeg.pop(port, None)
        cmd_socks.pop(port, None)
        root.after(0, show_main)
        print(f"[central:{port}] receiver ended")

def start_stream(port):
    s = cmd_socks.get(port)
    if s:
        try:
            s.sendall(b"start")
        except Exception as e:
            print("[central] start_stream error:", e)

def stop_stream(port):
    s = cmd_socks.get(port)
    if s:
        try:
            s.sendall(b"stop")
        except Exception as e:
            print("[central] stop_stream error:", e)

# ----------------- Utils -----------------
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
        except OSError:
            return True
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return False
        except OSError:
            return True

def clean_up():
    global stop
    stop = True
    try:
        for s in list(cmd_socks.values()):
            try:
                s.sendall(b"stop")
            except Exception:
                pass
            try:
                s.close()
            except Exception:
                pass
    except Exception:
        pass
    try:
        if server_socket:
            server_socket.close()
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        pass
    os._exit(0)

# ----------------- Main -----------------
def main():
    threading.Thread(target=listener, daemon=True).start()
    show_main()
    root.protocol("WM_DELETE_WINDOW", clean_up)
    root.mainloop()

if __name__ == "__main__":
    print("Central Program Started")
    main()

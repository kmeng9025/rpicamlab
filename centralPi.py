import socket
import threading
import subprocess
import os
import errno
import numpy
import cv2
import tkinter
from PIL import Image, ImageTk
from functools import partial
import time


used_ports = {}
change_buttons = []
buttons = {}
server_socket = None
stop = False
window = "m"
streaming_cameras = []

queue = {}
root_window = tkinter.Tk()
root_window.title("Camera Control")
root_window.geometry("600x600")

def main():
    # threading.Thread(target=listen_for_exit).start()
    threading.Thread(target=listener).start()
    initialize_main_window()
    root_window.mainloop()
    # display_video()
        

def initialize_main_window():
    global window
    clear_window()
    window = "m"
    text_camera = tkinter.Label(root_window, text="Cameras")
    text_camera.place(x=10, y=30)
    start_all_camera = tkinter.Button(root_window, text="Start All Cameras", command=start_all_cameras)
    start_all_camera.place(x=10, y=50)
    stop_all_camera = tkinter.Button(root_window, text="Stop All Cameras", command=stop_all_cameras)
    stop_all_camera.place(x=10, y=80)
    print(buttons.keys())
    for i in buttons.keys():
        # color = "green" if used_ports[i[0]][2] else "red"
        # buttons[i].config(background=color)
        buttons[i].pack()
    periodic_main_window()

def start_all_cameras():
    for i in used_ports.keys():
        used_ports[i][1].send(b"start")
        used_ports[i][2] = True

def stop_all_cameras():
    for i in used_ports.keys():
        used_ports[i][1].send(b"stop")
        used_ports[i][2] = False


def periodic_main_window():
    for i in change_buttons:
        if(i[2]):
            color = "green" if used_ports[i[0]][2] else "red"
            button = tkinter.Button(root_window, text=i[1], background=color, highlightbackground=color, command=partial(camera_clicked, i[0], i[1]))
            buttons[i[0]] = button
            button.pack()
            change_buttons.pop(0)
        else:
            buttons.pop(i[0])
    if window == "m":
        root_window.after(10, periodic_main_window)
    

def camera_clicked(port, name):
    global window
    clear_window()
    print("Camera clicked", port, name)
    window = "c"
    root_window.title("Camera " + str(name))
    buttonStream = tkinter.Button(root_window, text="Stream camera", command=partial(start_video, port))
    buttonStream.pack()
    startCamera = tkinter.Button(root_window, text="Start Camera", command=partial(start_camera, port))
    startCamera.pack()
    stopCamera = tkinter.Button(root_window, text="Stop Camera", command=partial(stop_camera, port))
    stopCamera.pack()

def start_camera(port):
    used_ports[port][1].send(b"start")
    used_ports[port][2] = True

def stop_camera(port):
    used_ports[port][1].send(b"stop")
    used_ports[port][2] = False


def start_video(port):
    clear_window()
    global window
    global video_label
    window = "v"
    video_label = tkinter.Label(root_window)
    video_label.place(x=0, y=0)
    # cv2.imshow(" stream", queue[i][-1])
    streaming_cameras.append(port)
    back_button = tkinter.Button(root_window, text="Back", command=initialize_main_window)
    back_button.pack()
    display_video(port)


def display_video(port):
    # clear_window()
    try:
        image = Image.fromarray(queue[port][-1]).resize((500, 500))
        image_tk = ImageTk.PhotoImage(image=image)
        video_label.config(image=image_tk)
        video_label.image = image_tk
        queue[port].pop(-1)
        queue[port] = []
    except Exception as e:
        print("display video error", e)
    if(window == "v"):
        root_window.after(10, partial(display_video, port))


def listener():
    global server_socket
    binding_socket = 7000
    print("Creating Assigning Socket")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Assigning Socket Created")
    print("Binding Socket to Port", binding_socket)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", binding_socket))
    print("Binded Socket")
    server_socket.listen(10)
    current_port = binding_socket + 1
    print("Starting Listener")
    while True:
        print("Waiting for Camera Pi")
        client_socket, client_address = server_socket.accept()
        print("Received Connection")
        print("Assigning Port")
        while (is_port_in_use(current_port)):
            if(current_port == 65535):
                current_port = 0
            current_port += 1
        print("Found Available Port:", current_port)
        print("Assigning Available Port:", current_port)
        client_socket.send(str(current_port).encode())
        # name = client_socket.recv(65535).decode()
        print("Assigned Available Port")
        print("Closing Camera Pi Assigning Socket")
        client_socket.close()
        print("Closed Camera Pi Assigning Socket")
        print("Creating New Thread for Port:", current_port)
        client_thread = threading.Thread(target=open_port, args=(current_port, client_address))
        # open_port(current_port)
        print("Created New Thread for Streaming")
        print("Starting Streaming Thread")
        client_thread.start()
        print("Started Streaming Thread")


# def listen_for_exit():
#     while True:
        


def clean_up():
    global stop
    print("CLEANING UP")
    stop = True
    try:
        server_socket.close()
    except:
        pass
    exit(0)


def clear_window():
    for widget in root_window.winfo_children():
        widget.destroy()


def open_port(port, client_address):
    global used_ports
    print(port, "In New Streaming Thread Port")
    print(port, "Creating UDP Streaming Socket")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(port, "Created UDP Streaming socket")
    print(port, "Binding Streaming Socket to Port")
    client_socket.bind(("0.0.0.0", port))
    print(port, "Binded Streaming to Port")
    # print("Binding to Camera Command Port")
    command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print("Binded to Camera Command Port")
    print("Connecting to Client")
    time.sleep(1)
    command_socket.connect((client_address[0], 7000))
    print("Connected to Client Command Port")
    print("Receiving Name from Client")
    name = command_socket.recv(65535).decode()
    used_ports[port] = (name, command_socket, False)
    change_buttons.append((port, name, True))
    print("Name Received")
    # print("DEBUGGING, SENDING START IMMEDIATELY")
    # command_socket.send(b"start")
    frame_data = bytearray()
    print(port, "Starting Receiving Loop")
    dropped = False
    queue[port] = []
    try:
        while not stop:
            # print(port, "Waiting for Data")
            data, adr = client_socket.recvfrom(1400)
            # print(port, "Data Received")
            # print(port, "Data Length:", len(data))
            if not data:
                print("bad")
            frame_data.extend(data)
            if frame_data.endswith(b"end"):
                # print(port, "Received End of Frame")
                # print(port, "Decoding Frame")
                if dropped:
                    frame_data = bytearray()
                    dropped = False
                    continue
                np_data = numpy.frombuffer(frame_data.removesuffix(b"end"), dtype=numpy.uint8)
                image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                if (image is not None):
                    print(port, "Frame Is Good")
                    if(streaming_cameras.count(port) != 0):
                        queue[port].append(image)
                else:
                    print(port, "Dropped Frame")
                frame_data = bytearray()
            elif (frame_data.endswith(b"c") and len(frame_data) == 1):
                print(port, "Received Request To Close Streaming Port")
                print(port, "Closing Port")
                client_socket.close()
                used_ports.pop(port)
                print(port, "Closed Port")
                break
    except:
        print("Port disconnected")
    used_ports[port] = ""
    change_buttons.append((port, name, False))
    command_socket.send(b"stop")
    command_socket.close()
    client_socket.close()


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
        except socket.error as e:
            return True
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return False
        except socket.error as e:
            return True

print("Central Program Started")
main()
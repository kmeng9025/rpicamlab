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
sessionStarted = False
sessionName = None
session_changed = False

queue = {}
root_window = tkinter.Tk()
root_window.title("Camera Control")
root_window.geometry("600x600")
def on_close():
    clean_up()
    kill_all_cameras()
    root_window.destroy()
    exit(0)
root_window.protocol("WM_DELETE_WINDOW", on_close)

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
    if(sessionStarted):
        root_window.title("Session: " + sessionName)
    else:
        root_window.title("NOT IN SESSION")
    text_camera = tkinter.Label(root_window, text="Cameras")
    text_camera.place(x=10, y=30)
    start_all_camera = tkinter.Button(root_window, text="Start All Cameras", command=start_all_cameras)
    start_all_camera.place(x=10, y=50)
    stop_all_camera = tkinter.Button(root_window, text="Stop All Cameras", command=stop_all_cameras)
    stop_all_camera.place(x=10, y=80)
    if(sessionStarted):
        stop_session_button = tkinter.Button(root_window, text="Stop Session and Export Data", command=stop_session)
        stop_session_button.place(x=10, y=110)
        export_data_button = tkinter.Button(root_window, text="Export Data", command=export_data)
        export_data_button.place(x=10, y=140)
    else:
        start_session_button = tkinter.Button(root_window, text="Start New Session", command=start_new_session)
        start_session_button.place(x=10, y=110)
    print(buttons.keys())
    for i in buttons.keys():
        try:
            button = buttons[i]
            color = "green" if used_ports[button[0]][2] else "red"
            actual_button = tkinter.Button(root_window, text=button[1], background=color, highlightbackground=color, command=partial(camera_clicked, button[0], button[1]))
            actual_button.pack()
        except:
            continue
    periodic_main_window()

def validate_input(char):
    return char.isalnum() or char == ""

def start_new_session():
    global window
    clear_window()
    window = "s"
    name_label = tkinter.Label(root_window, text="Enter Session Name:")
    name_label.place(x=10, y=50)
    vcmd = (root_window.register(validate_input), "%P")
    name = tkinter.Entry(root_window, width=80, validate="key", validatecommand=vcmd)
    name.place(x=10, y=80)
    name_submit = tkinter.Button(root_window, text="Start Session", command=partial(create_new_session, name.get()))
    name_submit.place(x=10, y=110)
    fail_label = tkinter.Label(root_window, text="can't have spaces or special characters. Must be under 20 characters")
    fail_label.pack()
    # notify_recorders()


def create_new_session(name):
    global sessionName
    global sessionStarted
    global session_changed
    if(len(name) > 20):
        start_new_session()
    if(sessionStarted):
        return
    sessionName = name
    sessionStarted = True
    session_changed = True
    start_all_cameras()
    

def stop_session():
    global sessionName
    global sessionStarted
    sessionName = None
    sessionStarted = False
    # export_data()
    stop_all_cameras()


def export_data():
    pass



def start_all_cameras():
    for i in used_ports.keys():
        used_ports[i][1].send(b"start")
        used_ports[i][2] = True
    initialize_main_window()

def kill_all_cameras():
    for i in used_ports.keys():
        try:
            used_ports[i][1].send(b"stop")
        except:
            continue

def stop_all_cameras():
    for i in used_ports.keys():
        used_ports[i][1].send(b"stop")
        used_ports[i][2] = False
    initialize_main_window()

def periodic_main_window():
    for i in change_buttons:
        if(i[2]):
            color = "green" if used_ports[i[0]][2] else "red"
            button = tkinter.Button(root_window, text=i[1], background=color, highlightbackground=color, command=partial(camera_clicked, i[0], i[1]))
            buttons[i[0]] = i
            button.pack()
            change_buttons.pop(0)
        else:
            buttons.pop(i[0])
            change_buttons.pop(0)
            initialize_main_window()
    if window == "m":
        root_window.after(10, periodic_main_window)


def process_images(port, lock):
    # print("hola")
    # global current_image
    while not stop:
        session_changed = False
        next_time = time.time()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        while not not used_ports[port][2]:
            time.sleep(0.2)
        if sessionStarted:
            name = "./output/" + sessionName + "/" + used_ports[port][0] + "/" + str(time.time())
            os.makedirs(os.path.dirname(name), exist_ok=True)
            name += used_ports[port][0] + ".mp4"
            print(name)
            out = cv2.VideoWriter(name, fourcc, 20, (1392, 1944))
        else:
            name = "./output/" + used_ports[port][0] + "/" + str(time.time())
            os.makedirs(os.path.dirname(name), exist_ok=True)
            name += used_ports[port][0] + ".mp4"
            print(name)
            out = cv2.VideoWriter(name, fourcc, 20, (1392, 1944))
        while not session_changed and not stop:
            # print(name)

            # print("hi")
            # for i in queue.keys():
                # next_time = time.time()
            try:
                if(not used_ports[port][2]):
                    continue
                with lock:
                    current_image = queue[port][0].copy()
            except Exception as e:
                print("cam not started", e)
                continue
            # queue[port][1].write(current_image)
            out.write(cv2.resize(current_image, (1944, 1392)))
            # last_time = queue[port][2]
            next_time += 1.0/20.0
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                out.write(current_image)
                next_time += 1.0/20.0
            # next_time = time.time()
            # if sleep_time > 0:
            #     time.sleep(sleep_time)
                    # continue
                    # continue

                # if(len(current_list) != 1):
                #     # current_list = 
        out.release()


    

def camera_clicked(port, name):
    global window
    clear_window()
    print("Camera clicked", port, name)
    window = "c"
    root_window.title("Camera " + str(name))
    if(used_ports[buttons[port][0]][2]):
        buttonStream = tkinter.Button(root_window, text="Stream camera", command=partial(start_video, port, name))
        buttonStream.pack()
        stopCamera = tkinter.Button(root_window, text="Stop Camera", command=partial(stop_camera, port, name))
        stopCamera.pack()
    else:
        startCamera = tkinter.Button(root_window, text="Start Camera", command=partial(start_camera, port, name))
        startCamera.pack()
    back = tkinter.Button(root_window, text="Back", command=initialize_main_window)
    back.pack()

def start_camera(port, name):
    used_ports[port][1].send(b"start")
    used_ports[port][2] = True
    camera_clicked(port, name)

def stop_camera(port, name):
    used_ports[port][1].send(b"stop")
    used_ports[port][2] = False
    camera_clicked(port, name)


def start_video(port, name):
    clear_window()
    global window
    global video_label
    window = "v"
    video_label = tkinter.Label(root_window)
    video_label.place(x=0, y=0)
    # cv2.imshow(" stream", queue[i][-1])
    # streaming_cameras.append(port)
    back_button = tkinter.Button(root_window, text="Back", command=partial(camera_clicked, port, name))
    back_button.pack()
    display_video(port)


def display_video(port):
    # clear_window()
    try:
        with used_ports[port][3]:
            image_npy = queue[port][0].copy()
        image = Image.fromarray(image_npy).resize((500, 500))
        image_tk = ImageTk.PhotoImage(image=image)
        video_label.config(image=image_tk)
        video_label.image = image_tk
        # queue[port].pop(-1)
        # queue[port] = []
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
    server_socket.settimeout(5)
    while not stop:
        print("Waiting for Camera Pi")
        try:
            client_socket, client_address = server_socket.accept()
        except:
            continue
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


def clean_up():
    global stop
    print("CLEANING UP")
    stop = True
    try:
        server_socket.close()
    except:
        pass

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
    change_buttons.append([port, name, True])
    print("Name Received")
    # print("DEBUGGING, SENDING START IMMEDIATELY")
    # command_socket.send(b"start")
    frame_data = bytearray()
    print(port, "Starting Receiving Loop")
    dropped = False
    queue[port] = []
    lock = threading.Lock()
    used_ports[port] = [name, command_socket, False, lock]
    # queue[port].append(threading.Lock())
    
    # queue[port].append(out)
    # queue[port].append(time.time())
    queue[port].append(None)
    threading.Thread(target=process_images, args=(port, lock)).start()
    client_socket.settimeout(5)
    try:
        while not stop:
            # print(port, "Waiting for Data")
            try:
                data, adr = client_socket.recvfrom(1400)
            except:
                continue
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
                try:
                    np_data = numpy.frombuffer(frame_data.removesuffix(b"end"), dtype=numpy.uint8)
                    image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                except:
                    print("ohoh")
                if (image is not None):
                    # print(port, "Frame Is Good")
                    # if(streaming_cameras.count(port) != 0):
                    with lock:
                        queue[port][0] = (image)
                else:
                    print(port, "Dropped Frame")
                frame_data = bytearray()
            elif (data == b"c"):
                print(port, "Received Request To Close Streaming Port")
                print(port, "Closing Port")
                client_socket.close()
                used_ports.pop(port)
                print(port, "Closed Port")
                break
    except Exception as e:
        print("Port disconnected", e)
    # used_ports.pop(port)
    change_buttons.append([port, name, False])
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
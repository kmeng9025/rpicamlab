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
#     # print(port, "In New Streaming Thread Port")
#     # print(port, "Creating UDP Streaming Socket")
#     # client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     # print(port, "Created UDP Streaming socket")
#     # print(port, "Binding Streaming Socket to Port")
#     # client_socket.bind(("0.0.0.0", port))
#     # print(port, "Binded Streaming to Port")
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
#     try:
#         print("HASsd")
#         command_socket.send(b"start")
#     except:
#         print("HASUHKH")
#     # frame_data = bytearray()
#     # print(port, "Starting Receiving Loop")
#     # dropped = False
#     print("hisdasdf")
#     queue[port] = []
#     print("dgfhjd")
#     try:
#         cap = cv2.VideoCapture("udp://0.0.0.0:" + str(port))
#         print("hisd")
#         while not stop:
#             ret, frame = cap.read()
#             print("hi")
#             if ret:
#                 print("hiagain")
#                 frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 # cv2.imshow("hi", frame)
#                 if(streaming_cameras.count(port) != 0):
#                     queue[port].append(frame)
#             # print(port, "Waiting for Data")
#             # data, adr = client_socket.recvfrom(1400)
#             # print(port, "Data Received")
#             # print(port, "Data Length:", len(data))
#             # if not data:
#             #     print("bad")
#             # frame_data.extend(data)
#             # if frame_data.endswith(b"end"):
#             #     print(port, "Received End of Frame")
#             #     print(port, "Decoding Frame")
#             #     if dropped:
#             #         frame_data = bytearray()
#             #         dropped = False
#             #         continue
#             #     np_data = numpy.frombuffer(frame_data.removesuffix(b"end"), dtype=numpy.uint8)
#             #     image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
#             #     if (image is not None):
#             #         print(port, "Frame Is Good")
#             #         if(streaming_cameras.count(port) != 0):
#             #             queue[port].append(image)
#             #     else:
#             #         print(port, "Dropped Frame")
#             #     frame_data = bytearray()
#             # elif (frame_data.endswith(b"c") and len(frame_data) == 1):
#             #     print(port, "Received Request To Close Streaming Port")
#             #     print(port, "Closing Port")
#             #     client_socket.close()
#             #     used_ports.pop(port)
#             #     print(port, "Closed Port")
#             #     break
#     except:
#         print("Port disconnected")
#     used_ports[port] = ""
#     change_buttons.append((port, name, False))
#     command_socket.send(b"stop")
#     command_socket.close()
#     # client_socket.close()


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

import socket
import threading
import subprocess
import cv2
import tkinter
from PIL import Image, ImageTk
from functools import partial
import time

# --- Globals ---
camera_connections = {}  # {port: {'name': name, 'socket': socket, 'address': addr}}
gui_elements = {} # {port: {'button': button_widget}}
root_window = tkinter.Tk()
root_window.title("Camera Control")
root_window.geometry("800x600")

# --- Main Application Logic ---
def main():
    # Start the listener for new camera connections
    threading.Thread(target=connection_listener, daemon=True).start()
    
    # Setup initial GUI
    setup_main_window()
    
    # Start the Tkinter main loop
    root_window.mainloop()
    
    # Cleanup on exit
    shutdown_all_cameras()

def setup_main_window():
    title_label = tkinter.Label(root_window, text="Connected Cameras", font=("Helvetica", 16))
    title_label.pack(pady=10)
    
def connection_listener():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", 7000))
    server_socket.listen(5)
    print("Listening for new cameras on port 7000...")
    
    port_counter = 7001
    
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")
        
        # Assign a new UDP port for the video stream
        stream_port = port_counter
        port_counter += 1
        
        # Send the assigned port back to the camera
        client_socket.send(str(stream_port).encode())
        
        # Wait for the camera to send its name
        camera_name = client_socket.recv(1024).decode().split(":")[1]
        
        camera_connections[stream_port] = {
            'name': camera_name,
            'socket': client_socket,
            'address': client_address
        }
        
        # Add a button for the new camera to the GUI
        add_camera_button(stream_port, camera_name)

def add_camera_button(port, name):
    button = tkinter.Button(root_window, text=f"{name} ({port})", command=lambda: open_camera_window(port, name))
    button.pack(pady=5)
    gui_elements[port] = {'button': button}

def open_camera_window(port, name):
    # Create a new top-level window for the camera stream
    cam_window = tkinter.Toplevel(root_window)
    cam_window.title(f"Stream from {name}")
    
    video_label = tkinter.Label(cam_window)
    video_label.pack()
    
    # Send start command
    camera_connections[port]['socket'].send(b"start")
    print(f"Sent 'start' to {name}")
    
    # Start a thread to display the video
    threading.Thread(target=display_video_stream, args=(port, video_label), daemon=True).start()

    def on_close():
        # Send stop command when window is closed
        camera_connections[port]['socket'].send(b"stop")
        print(f"Sent 'stop' to {name}")
        cam_window.destroy()

    cam_window.protocol("WM_DELETE_WINDOW", on_close)

def display_video_stream(port, video_label):
    # The video stream URL for OpenCV
    video_url = f"udp://0.0.0.0:{port}"
    cap = cv2.VideoCapture(video_url)
    
    if not cap.isOpened():
        print(f"Error: Could not open video stream for port {port}")
        return
        
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1) # Wait a bit if no frame
            continue
        
        # Convert the frame for Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Update the label in the GUI
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
        
        # Check if the window still exists
        if not video_label.winfo_exists():
            break # Exit thread if window is closed
            
    cap.release()
    print(f"Released video capture for port {port}")

def shutdown_all_cameras():
    for port in camera_connections:
        try:
            camera_connections[port]['socket'].send(b"shutdown")
            camera_connections[port]['socket'].close()
        except Exception as e:
            print(f"Could not shut down camera at port {port}: {e}")

if __name__ == "__main__":
    main()
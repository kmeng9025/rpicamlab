import socket
import threading
import subprocess
import os
import errno
import numpy
import cv2


used_ports = []
server_socket = None

queue = {}


def main():
    # threading.Thread(target=listen_for_exit).start()
    threading.Thread(target=listener).start()
    while True:
        for i in queue.keys():
            if(queue[i] != []):
                cv2.imshow(i + " stream", queue[i][0])
                queue[i].pop(0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            clean_up()


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
        print("Assigned Available Port")
        print("Closing Camera Pi Assigning Socket")
        client_socket.close()
        print("Closed Camera Pi Assigning Socket")
        print("Creating New Thread for Port:", current_port)
        client_thread = threading.Thread(target=open_port, args=(current_port,))
        # open_port(current_port)
        print("Created New Thread for Streaming")
        print("Starting Streaming Thread")
        client_thread.start()
        print("Started Streaming Thread")


# def listen_for_exit():
#     while True:
        


def clean_up():
    print("CLEANING UP")
    try:
        server_socket.close()
    except:
        pass
    for i in used_ports:
        try:
            i.close()
        except:
            pass
    exit(0)


def open_port(port):
    global used_ports
    print(port, "In New Streaming Thread Port")
    print(port, "Creating UDP Streaming Socket")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    used_ports.append(client_socket)
    print(port, "Created UDP Streaming socket")
    print(port, "Binding Streaming Socket to Port")
    client_socket.bind(("0.0.0.0", port))
    print(port, "Binded Streaming to Port")
    frame_data = bytearray()
    print(port, "Starting Receiving Loop")
    dropped = False
    queue[str(port)] = []
    try:
        while True:
            print(port, "Waiting for Data")
            data, adr = client_socket.recvfrom(1024)
            print(port, "Data Received")
            print(port, "Data Length:", len(data))
            if not data:
                print("bad")
            frame_data.extend(data)
            if frame_data.endswith(b"end"):
                print(port, "Received End of Frame")
                print(port, "Decoding Frame")
                if dropped:
                    frame_data = bytearray()
                    dropped = False
                    continue
                np_data = numpy.frombuffer(frame_data.removesuffix(b"end"), dtype=numpy.uint8)
                image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                if (image is not None):
                    print(port, "Frame Is Good")
                    queue[str(port)].append(image)
                else:
                    print(port, "Dropped Frame")
                frame_data = bytearray()
            elif (frame_data.endswith(b"c") and len(frame_data) == 1):
                print(port, "Received Request To Close Streaming Port")
                print(port, "Closing Port")
                client_socket.close()
                used_ports.remove(client_socket)
                print(port, "Closed Port")
                break
            # elif(len(data) < 1024):
            #     frame_data = bytearray()
            #     dropped = True
            #     print(port, "Dropped Frame")
    except:
        print("Port disconnected")


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
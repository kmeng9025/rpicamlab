import socket
import threading
import subprocess
import os
import errno
import numpy
import cv2


def main():
    binding_socket = 7000
    print("Creating Assigning Socket")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Assigning Socket Created")
    print("Binding Socket to Port", binding_socket)
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
        client_thread = threading.Thread(targe=open_port)
        print("Created New Thread for Streaming")
        print("Starting Streaming Thread")
        client_thread.start()
        print("Started Streaming Thread")


def open_port(port):
    print(port, "In New Streaming Thread Port")
    print(port, "Creating UDP Streaming Socket")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(port, "Created UDP Streaming socket")
    print(port, "Binding Streaming Socket to Port")
    client_socket.bind(("192.168.4.1", port))
    print(port, "Binded Streaming to Port")
    frame_data = b""
    print(port, "Starting Receiving Loop")
    while True:
        print(port, "Waiting for Data")
        data, adr = client_socket.recvfrom(65535)
        print(port, "Data Received")
        print(port, "Data Length:", len(data))
        frame_data += data
        if(data.decode()[-3:] == "e"):
            print(port, "Received End of Frame")
            print(port, "Decoding Frame")
            np_data = numpy.frombuffer(frame_data, dtype=numpy.uint8)
            image = cv2.imdecode(np_data, cv2.IMREAD_COLOR_RGB)
            if (image is not None):
                print(port, "Frame Is Good")
                cv2.imshow(str(port) + " stream", image)
            else:
                print(port, "Dropped Frame")
            frame_data = b""
        elif(data.decode() == "c"):
            print(port, "Received Request To Close Streaming Port")
            print(port, "Closing Port")
            client_socket.close()
            print(port, "Closed Port")
            break
        elif(len(data) < 60000):
            frame_data = b""
            print(port, "Dropped Frame")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except socket.error as e:
            return True

print("Central Program Started")
main()
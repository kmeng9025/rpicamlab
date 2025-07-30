import socket
import threading
import subprocess
import os
import errno
import numpy
import cv2

# subprocess.run("sudo nmcli device wifi hotspot ssid rpicamlab password rpicamlab ifname wlan0")
# subprocess.run("ifconfig")
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.4.1", 7000))
    server_socket.listen(10)
    current_port = 7001
    while True:
        client_socket, client_address = server_socket.accept()
        while (is_port_in_use(current_port)):
            if(current_port == 65535):
                current_port = 0
            current_port += 1
        client_socket.send(str(current_port).encode())
        client_socket.close()
        client_thread = threading.Thread(open_port)
        client_thread.start()

def open_port(port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(("192.168.4.1", port))
    frame_data = b""
    while True:
        data, adr = client_socket.recvfrom(65535)
        frame_data += data
        if(len(data) < 60000):
            np_data = numpy.frombuffer(frame_data, dtype=numpy.uint8)
            image = cv2.imdecode(np_data, cv2.IMREAD_COLOR_RGB)
            if (image is not None):
                cv2.imshow("stream", image)
            else:
                print("dropeed frame")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False  # Port is available
        except socket.error as e:
            return True

main()
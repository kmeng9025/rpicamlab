import socket
import cv2
import struct
import time

CENTRAL_PI_IP = '192.168.4.1'  # Change to your central Pi IP

# Step 1: Connect to control channel
control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_sock.connect((CENTRAL_PI_IP, 5000))
print("Connected to control port 5000")

# Step 2: Ask for data port
control_sock.sendall(b'REQUEST_PORT')
assigned_port = int(control_sock.recv(16).decode())
print(f"Assigned data port: {assigned_port}")
control_sock.close()

# Step 3: Connect to assigned port for data streaming
data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_sock.connect((CENTRAL_PI_IP, assigned_port))
print(f"Connected to data port {assigned_port}")

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Encode as JPEG
    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    data = buffer.tobytes()
    # Send length first, then data
    data_sock.sendall(struct.pack('>I', len(data)) + data)
    time.sleep(0.05)  # ~20 FPS; adjust as needed

cap.release()
data_sock.close()

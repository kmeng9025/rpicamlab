import socket
import threading
import struct
import cv2
import numpy as np

HOST = '0.0.0.0'
CONTROL_PORT = 5000
START_DATA_PORT = 5001
MAX_CAMERAS = 10

assigned_ports = set()
lock = threading.Lock()

def handle_control(conn, addr):
    with lock:
        # Find first available port
        port = START_DATA_PORT
        while port in assigned_ports and port < START_DATA_PORT + MAX_CAMERAS:
            port += 1
        if port >= START_DATA_PORT + MAX_CAMERAS:
            conn.sendall(b'0')  # Indicate no available port
            conn.close()
            return
        assigned_ports.add(port)
    # Send port number as string
    conn.sendall(str(port).encode())
    conn.close()
    # Start receiver thread on that port
    threading.Thread(target=frame_receiver, args=(port,), daemon=True).start()

def frame_receiver(port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, port))
    server_sock.listen(1)
    print(f"Listening for frames on port {port}")
    conn, addr = server_sock.accept()
    print(f"Camera connected on port {port} from {addr}")
    data = b''
    payload_size = struct.calcsize('>I')
    while True:
        while len(data) < payload_size:
            packet = conn.recv(4096)
            if not packet:
                print(f"Camera {addr} disconnected")
                assigned_ports.discard(port)
                return
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack('>I', packed_msg_size)[0]
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        if frame is not None:
            cv2.imshow(f'Camera {port}', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    conn.close()
    server_sock.close()
    assigned_ports.discard(port)

# Control channel for port requests
control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_sock.bind((HOST, CONTROL_PORT))
control_sock.listen(5)
print(f"Control server listening on port {CONTROL_PORT}")

while True:
    conn, addr = control_sock.accept()
    print(f"Control connection from {addr}")
    threading.Thread(target=handle_control, args=(conn, addr), daemon=True).start()

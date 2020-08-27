# Echo server program
import socket

HOST = ''  # Symbolic name meaning all available interfaces
PORT = 50007  # Arbitrary non-privileged port
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        data = conn.recv(1024)
        if data:
        	print(data.decode('utf-8'))
        	conn.sendall(data)

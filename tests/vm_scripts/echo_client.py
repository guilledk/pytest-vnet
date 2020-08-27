# Echo client program
import sys
import socket

HOST = '10.0.0.1'  # The remote host
PORT = 50007  # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(sys.argv[1].encode('utf-8'))
    print(s.recv(1024).decode('utf-8'))
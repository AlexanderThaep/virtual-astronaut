import socket

# Set up the client
SERVER_IP = "192.168.1.100"  # Change this to your Raspberry Pi's IP
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))

print(f"Connected to server {SERVER_IP}:{PORT}")

while True:
    message = input("Client: ")
    if not message:
        break
    client_socket.sendall(message.encode())
    data = client_socket.recv(1024)
    print(f"Server: {data.decode()}")

client_socket.close()
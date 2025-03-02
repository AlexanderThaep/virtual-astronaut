import socket

# Set up the client
SERVER_IP = "10.42.0.23"  # Change this to your Raspberry Pi's IP
PORT = 3000

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
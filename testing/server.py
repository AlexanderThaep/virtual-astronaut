import socket

# Set up the server
HOST = "0.0.0.0"  # Listen on all available interfaces
PORT = 3000       # Port to listen on

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        break
    print(f"Client: {data.decode()}")
    response = input("Server: ")
    conn.sendall(response.encode())

conn.close()
server_socket.close()
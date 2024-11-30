import socket
import cv2 as cv

img = cv.imread("doge.png")
img_data = cv.imencode('.png', img)[1].tobytes()

def run_video(main):
    udp_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    text = "Hello, world!"
    byte_data = text.encode()

    while main.active:
        if main.client_udp_port and main.current_client:
            udp_socket.sendto(byte_data, 
                              (main.current_client.remote_address[0], 
                               main.client_udp_port))
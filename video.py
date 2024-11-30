import socket
import cv2 as cv

img = cv.imread("doge.png")
img_data = cv.imencode('.jpg', img, [int(cv.IMWRITE_JPEG_QUALITY), 50])[1].tobytes()

def run_video(main):
    udp_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    text = "Hello, world!"
    byte_data = text.encode()

    while main.active:
        if main.client_udp_port and main.current_client:
            total_chunks = (len(img_data) + 1024 - 1) // 1024
            main.log_print(f"Size {len(img_data)}\n", False)
            for i in range(total_chunks):
                start = i * 1024
                end = start + 1024
                udp_socket.sendto(img_data[start:end], 
                                (main.current_client.remote_address[0], 
                                main.client_udp_port))
            return
import time
import socket
import cv2 as cv
from picamera2.picamera2 import Picamera2

# img = cv.imread("doge.png")
# img_data = cv.imencode('.jpg', img, [int(cv.IMWRITE_JPEG2000_COMPRESSION_X1000), 50])[1].tobytes()

TARGET_FRAMERATE = 1/30
CHUNK_SIZE = 1024

def run_video(main):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    cam = Picamera2()
    config = cam.create_preview_configuration()
    cam.configure(config)

    cam.start()

    while main.active:
        time.sleep(TARGET_FRAMERATE)
        if main.client_udp_port and main.current_client:
            client = main.current_client
            frame = cam.capture_array()
            img_bytes = cv.imencode('.jpg', frame, [int(cv.IMWRITE_JPEG2000_COMPRESSION_X1000), 50])[1].tobytes()
            end_buffer = bytearray(1)

            total_chunks = len(img_bytes) // CHUNK_SIZE + 1
            for i in range(total_chunks):
                start = i * CHUNK_SIZE
                end = start + CHUNK_SIZE
                udp_socket.sendto(img_bytes[start:end], 
                                (client.remote_address[0], 
                                main.client_udp_port))
            
            udp_socket.sendto(end_buffer, (client.remote_address[0], main.client_udp_port))
            # print(f"Image sent to {client.remote_address[0]} at {main.client_udp_port}") 

    cam.release()
    print("Cutting video...\n")

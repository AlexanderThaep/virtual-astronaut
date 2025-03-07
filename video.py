import time
import socket
import cv2 as cv
import picamera2 as pi

# img = cv.imread("doge.png")
# img_data = cv.imencode('.jpg', img, [int(cv.IMWRITE_JPEG2000_COMPRESSION_X1000), 50])[1].tobytes()

TARGET_FRAMERATE = 1/30

def run_video(main):
    udp_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    cam = pi.Picamera2()
    cam.start()

    while main.active:
        time.sleep(TARGET_FRAMERATE)
        if main.client_udp_port and main.current_client:
            client = main.current_client
            frame = cam.capture_array()
            img_bytes = cv.imencode('.jpg', frame, [int(cv.IMWRITE_JPEG2000_COMPRESSION_X1000), 50])[1].tobytes()
            end_buffer = bytearray(1)

            total_chunks = (len(img_bytes) + 1024 - 1) // 1024
            for i in range(total_chunks):
                start = i * 1024
                end = start + 1024
                udp_socket.sendto(img_bytes[start:end], 
                                (client.remote_address[0], 
                                main.client_udp_port))
            udp_socket.sendto(end_buffer, (client.remote_address[0], main.client_udp_port))

    cam.stop()
    print("Cutting video...\n")
import cv2 as cv

img = cv.imread("doge.png")
img_data = cv.imencode('.png', img)[1].tobytes()

def run_video(main):
    pass 
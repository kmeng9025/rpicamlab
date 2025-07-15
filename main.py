import cv2
from picamera2 import Picamera2 as picam
import time
cam = picam()
cam.start()
while True:
    frame = cam.capture_array()
    cv2.imshow("show", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cam.close()
cv2.destroyAllWindows()
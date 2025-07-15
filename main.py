from picamera2 import Picamera2
import cv2
import time

# Initialize camera
picam2 = Picamera2()

# picam2.preview_configuration.main.size = (640, 480)
# picam2.preview_configuration.main.format = "RGB888"

# picam2.start()
# picam2.configure("preview")
# frame = picam2.capture_array()
# cv2.imshow("PiCamera2 Preview", frame)
# time.sleep(2)

# while True:
#     frame = picam2.capture_array()
#     cv2.imshow("PiCamera2 Preview", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Clean up
# cv2.destroyAllWindows()
picam2.close()

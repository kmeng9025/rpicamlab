from picamera2 import Picamera2
import cv2
import time

# Initialize camera
picam2 = Picamera2()

# Configure camera preview
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")

# Start the camera
picam2.start()
time.sleep(1)  # Give the camera time to warm up

while True:
    # Capture a frame
    frame = picam2.capture_array()

    # Display using OpenCV
    cv2.imshow("PiCamera2 Preview", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
picam2.close()

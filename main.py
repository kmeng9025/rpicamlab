from picamera2 import Picamera2
import cv2
import time
try:
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    time.sleep(0.1)
    frame = picam2.capture_array()
    cv2.imshow("PiCamera2 Preview", frame)
    time.sleep(2)

    while True:
        frame = picam2.capture_array()
        cv2.imshow("PiCamera2 Preview", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    picam2.close()
    cv2.destroyAllWindows()

except:
    print("hi")
    cv2.destroyAllWindows()
    picam2.close()
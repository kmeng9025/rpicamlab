from picamera2 import Picamera2
import cv2
import time
import datetime
# try:
lastMovement = datetime.datetime.now()
start = datetime.datetime.now()
movements = []
notMove = False
movement = 0
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(0.1)
frame = picam2.capture_array()
cv2.imshow("PiCamera2 Preview", frame)
time.sleep(2)
previousFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    diff = cv2.absdiff(previousFrame, gray)
    movement += diff.sum()
    if(movement<0):
        print("INTEGER OVERFLOW ARGHHHHHHH")
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=60)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if(len(contours) > 0):
        cv2.putText(frame, "Movement: True", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2, cv2.LINE_AA)
        lastMovement = datetime.datetime.now()
        notMove = True
    else:
        cv2.putText(frame, "Movement: False", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2, cv2.LINE_AA)
        if ((datetime.datetime.now() - lastMovement).total_seconds() > 10):
            cv2.putText(frame, "Movement: False", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2, cv2.LINE_AA)
            if(notMove):
                movements.append((lastMovement, datetime.datetime.now(), movement))
                movement = 0
                notMove = False

        
    for contour in contours:
        if cv2.contourArea(contour) < 100:
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow("PiCamera2 Preview", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    previousFrame = gray.copy()

if(notMove):
    movements.append((lastMovement, datetime.datetime.now(), movement))
# Clean up
picam2.close()
cv2.destroyAllWindows()
print(movements)
print("Total Time in sec: " + str((start-datetime.datetime.now()).total_seconds()))

# except Exception as e:
#     print(e)
#     cv2.destroyAllWindows()
#     picam2.close()
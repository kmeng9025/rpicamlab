from picamera2 import Picamera2
import cv2
import time
import datetime
import numpy
# try:
lastMovement = datetime.datetime.now()
start = datetime.datetime.now()
movements = []
notMove = False
movement = 0
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1024, 768)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(0.1)
frame = picam2.capture_array()
cv2.imshow("PiCamera2 Preview", frame)
time.sleep(2)
previousFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
previousContours = numpy.zeros(frame.shape, dtype=numpy.uint8)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(str(start.timestamp()) + ".mp4", fourcc, 30, (1024, 768))
while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    diff = cv2.absdiff(previousFrame, gray)
    movement += diff[80:670][300:650].sum()
    if(movement<0):
        print("INTEGER OVERFLOW ARGHHHHHHH")
    _, thresh = cv2.threshold(diff, 60, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=60)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    validMovement = False
    for contour in contours:
        if cv2.contourArea(contour) < 100:
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        if (300 < x < 650) and (80 < y < 670):
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            validMovement = True
        elif(310 < x+w < 650) and (90 < y+h < 670):
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            validMovement = True
        else:
            continue
    if(validMovement):
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
    
    cv2.imshow("Camera Preview", frame)
    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    previousFrame = gray.copy()

if(notMove):
    movements.append((lastMovement, datetime.datetime.now(), movement))
# Clean up
file = open(str(start.date()) + str(start.time()) + ".txt", "w")
out.release()
picam2.close()
cv2.destroyAllWindows()
file.write(str(movements) + "\n" + str((datetime.datetime.now()-start).total_seconds()))
print(movements)
file.close()
print("Total Time in sec: " + str((datetime.datetime.now()-start).total_seconds()))

# except Exception as e:
#     print(e)
#     cv2.destroyAllWindows()
#     picam2.close()
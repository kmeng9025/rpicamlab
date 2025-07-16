from picamera2 import Picamera2
import cv2
import time
import datetime
import numpy
def main():
    # lastMovement = datetime.datetime.now()
    start = datetime.datetime.now()
    # movements = []
    # notMove = False
    # movement = 0
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (1024, 768)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    time.sleep(0.1)
    frame = picam2.capture_array()
    cv2.imshow("Camera Preview", frame)
    time.sleep(2)
    # previousFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # previousContours = numpy.zeros(frame.shape, dtype=numpy.uint8)
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # out = cv2.VideoWriter("./data/" + str(start.date()) + " " + str(start.time())[:-7] + ".mp4", fourcc, 30, (1024, 768))
    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        # diff = cv2.absdiff(previousFrame[90:670, 310:690], gray[90:670, 310:690])
        # print(previousFrame)
        # print(gray[90:670, 310:690].shape)
        # print(diff.shape)
        # movement += diff.sum()
        # if(movement<0):
        #     print("INTEGER OVERFLOW ARGHHHHHHH")
        _, thresh = cv2.threshold(gray[60:720, 285:690], 40, 255, cv2.THRESH_BINARY_INV)
        dilated = cv2.dilate(thresh, None, iterations=15)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        miceFound = False
        for contour in contours:
            if cv2.contourArea(contour) < 100:
                continue
            (x, y, w, h) = cv2.boundingRect(contour)
            # if (300 < x < 650) and (80 < y < 670):
            #     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            #     validMovement = True
            # elif(300 < x+w < 730) and (80 < y+h < 780) and (250 < x < 650) and (35 < y < 670):
            #     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            #     validMovement = True
            # else:
            #     continue
            cv2.rectangle(frame, (x+285, y+60), (x+285+w, y+60+h), (0, 255, 0), 2)
            miceFound = True
        if(miceFound):
            cv2.putText(frame, "Mouse Detected: True", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2, cv2.LINE_AA)
            # lastMovement = datetime.datetime.now()
            # notMove = True
        else:
            cv2.putText(frame, "Mouse Detected: False", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2, cv2.LINE_AA)
            # if ((datetime.datetime.now() - lastMovement).total_seconds() > 10):
            #     if(notMove):
            #         movements.append((lastMovement, datetime.datetime.now(), movement))
            #         movement = 0
            #         notMove = False
        cv2.putText(frame, str(datetime.datetime.now().date()) + " " + str(datetime.datetime.now().time())[:-7], (230, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.imshow("Camera Preview", frame)
        # out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # previousFrame = gray.copy()

    # if(notMove):
    #     movements.append((lastMovement, datetime.datetime.now(), movement))
    # Clean up
    # file = open("./data/" + str(start.date()) + " " + str(start.now().time())[:-7] + ".txt", "w")
    # out.release()
    # picam2.close()
    # cv2.destroyAllWindows()
    # file.write(str(movements) + "\n" + str((datetime.datetime.now()-start).total_seconds()))
    # print(movements)
    # file.close()
    print("Total Time in sec: " + str((datetime.datetime.now()-start).total_seconds()))
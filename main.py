from picamera2 import Picamera2
import cv2
import time
import datetime
import numpy
import test
import threading
import subprocess
# try:
def main():
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
    cv2.imshow("Camera Preview", frame)
    time.sleep(2)
    previousFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    previousContours = numpy.zeros(frame.shape, dtype=numpy.uint8)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("./data/" + str(start.date()) + " " + str(start.time())[:-7] + ".mp4", fourcc, 30, (1024, 768))
    fourccc = cv2.VideoWriter_fourcc(*'mp4v')
    outraw = cv2.VideoWriter("./data/raw" + str(start.date()) + " " + str(start.time())[:-7] + ".mp4", fourccc, 30, (1024, 768))
    fourcccc = cv2.VideoWriter_fourcc(*'mp4v')
    out2 = cv2.VideoWriter("./data/micedetection" + str(start.date()) + " " + str(start.time())[:-7] + ".mp4", fourcccc, 30, (1024, 768))
    while True:
        theframe = picam2.capture_array()
        frame = theframe.copy()
        outraw.write(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        diff = cv2.absdiff(previousFrame[90:670, 310:690], gray[90:670, 310:690])
        # print(previousFrame)
        # print(gray[90:670, 310:690].shape)
        # print(diff.shape)
        movement += diff.sum()
        if(movement<0):
            print("INTEGER OVERFLOW ARGHHHHHHH")
        _, thresh = cv2.threshold(diff, 80, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=60)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        validMovement = False
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
            cv2.rectangle(frame, (x+310, y+90), (x+310+w, y+90+h), (0, 255, 0), 2)
            validMovement = True
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
        cv2.putText(frame, str(datetime.datetime.now().date()) + " " + str(datetime.datetime.now().time())[:-7], (230, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.imshow("Camera Preview", frame)
        out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        previousFrame = gray.copy()




        #TEST


        frame = theframe.copy()
        # frame = picam2.capture_array()
        # cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        # _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        # diff = cv2.absdiff(previousFrame[90:670, 310:690], gray[90:670, 310:690])
        # print(previousFrame)
        # print(gray[90:670, 310:690].shape)
        # print(diff.shape)
        # movement += diff.sum()
        # if(movement<0):
        #     print("INTEGER OVERFLOW ARGHHHHHHH")
        _, thresh = cv2.threshold(gray[60:720, 285:690], 50, 255, cv2.THRESH_BINARY_INV)
        dilated = cv2.dilate(thresh, None, iterations=0)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        miceFound = False
        for contour in contours:
            if cv2.contourArea(contour) < 500:
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
            cv2.rectangle(frame, (int(x), int(y)), (int(x) + int(w), int(y) + int(h)) (0, 255, 0), 2)
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
        cv2.imshow("Camera Preview test", frame)
        out2.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if(notMove):
        movements.append((lastMovement, datetime.datetime.now(), movement))
    # Clean up
    file = open("./data/" + str(start.date()) + " " + str(start.now().time())[:-7] + ".txt", "w")
    out.release()
    outraw.release()
    picam2.close()
    cv2.destroyAllWindows()
    file.write(str(movements) + "\n" + str((datetime.datetime.now()-start).total_seconds()))
    print(movements)
    file.close()
    print("Total Time in sec: " + str((datetime.datetime.now()-start).total_seconds()))
    out2.release()
# except Exception as e:
#     print(e)
#     cv2.destroyAllWindows()
#     picam2.close()
if __name__ == "__main__":
    # test.main()
    
    # script_thread = threading.Thread(target=main)
    # # Start the thread
    # script_thread.start()
    main()
    # script_thread2 = threading.Thread(target=test.main)
    # # Start the thread
    # script_thread2.start()

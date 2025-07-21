import cv2
import time
import datetime
import numpy
import copy

fromFile = True
videoPath = "3WMice.mp4"
currentFrame = 0

if not fromFile:
    from picamera2 import Picamera2

xd, yd = 200, 0
wd, hd = 600, 768

def main():   
    if(fromFile):
        for i in range(total_frames):
            logic()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        while True:
            logic()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    if(not fromFile):
        file = open("./data/" + str(start.date()) + " " + str(start.now().time())[:-7] + ".txt", "w")
        outraw.release()
        cam.close()
        cv2.destroyAllWindows()
        file.close()
        print("Total Time in sec: " + str((datetime.datetime.now()-start).total_seconds()))
        out2.release()


def logic():
    theframe = getFrame()
    frameBlack = copy.deepcopy(theframe)
    frameWhite = copy.deepcopy(theframe)
    frameBoth = copy.deepcopy(theframe)
    
    grayBlack = cv2.cvtColor(frameBlack, cv2.COLOR_RGB2GRAY)
    grayWhite = cv2.cvtColor(frameWhite, cv2.COLOR_RGB2GRAY)
    # equalized = cv2.equalizeHist(grayWhite)
    # final = cv2.convertScaleAbs(equalized, alpha=1.)

    _, threshBlack = cv2.threshold(grayBlack[yd:yd+hd, xd:xd+wd], 40, 255, cv2.THRESH_BINARY_INV)
    _, threshWhite = cv2.threshold(grayWhite[yd:yd+hd, xd:xd+wd], 150, 255, cv2.THRESH_BINARY)
    
    cv2.imshow("hi", threshWhite)

    annotatedBlack = annotateFrame(threshBlack, frameBlack, True)
    annotatedWhite = annotateFrame(threshWhite, frameWhite, False)

    annotatedCombined = annotateFrame(threshBlack, frameBoth, True)
    annotatedCombined = annotateFrame(threshWhite, annotatedCombined, False)

    cv2.imshow("Camera Preview Black", annotatedBlack)
    cv2.imshow("Camera Preview White", annotatedWhite)
    cv2.imshow("Camera Preview Combined", annotatedCombined)

    if(not fromFile):
        out2.write(annotatedCombined)
    

def getFrame():
    global currentFrame
    if(fromFile):
        cam.set(cv2.CAP_PROP_POS_FRAMES, currentFrame)
        currentFrame += 1
        _, frame = cam.read()
        return frame
    else:
        frame = cam.capture_array()
        outraw.write(frame)
        return frame
    

def annotateFrame(thresh, frame, black):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))

    opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    dilated = cv2.dilate(opened, None, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    miceFound = False
    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        
        cv2.rectangle(frame, (x+xd, y+yd), (x+xd+w, y+yd+h), (0, 255, 0), 2)
        miceFound = True

    if black:
        color = "Black"
        location = (10, 20)
    else:
        color = "White"
        location = (frame.shape[0]-70, 20)

    if(miceFound):
        cv2.putText(frame, color + " Mouse Detected: True", location, cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, color + " Mouse Detected: False " + str(len(contours)), location, cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.putText(frame, str(datetime.datetime.now().date()) + " " + str(datetime.datetime.now().time())[:-7], (230, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3, cv2.LINE_AA)

    return frame


start = datetime.datetime.now()

if(fromFile):
    cam = cv2.VideoCapture(videoPath)
    total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))

else:
    cam = Picamera2()
    cam.preview_configuration.main.size = (1024, 768)
    cam.preview_configuration.main.format = "RGB888"
    cam.configure("preview")
    cam.start()
    time.sleep(0.5)
    fourccc = cv2.VideoWriter_fourcc(*'mp4v')
    outraw = cv2.VideoWriter("./data/raw" + str(start.date()) + " " + str(start.time())[:-7] + ".mp4", fourccc, 30, (1024, 768))
    fourcccc = cv2.VideoWriter_fourcc(*'mp4v')
    out2 = cv2.VideoWriter("./data/micedetection" + str(start.date()) + " " + str(start.time())[:-7] + ".mp4", fourcccc, 30, (1024, 768))



if __name__ == "__main__":
    main()

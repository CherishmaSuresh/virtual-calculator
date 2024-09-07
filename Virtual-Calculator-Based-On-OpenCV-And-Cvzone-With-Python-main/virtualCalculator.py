import cv2
from cvzone.HandTrackingModule import HandDetector

class Button:
    def __init__(self, pos, width, height, value, button_type):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value
        self.button_type = button_type  # Additional attribute to distinguish button types

    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (250, 251, 217), cv2.FILLED)  # background
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)  # border
        cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 40),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)  # text

    def checkClicking(self, x, y, img):
        if self.pos[0] < x < self.pos[0] + self.width and self.pos[1] < y < self.pos[1] + self.height:
            cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                          (255, 255, 255), cv2.FILLED)  # highlight background
            cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                          (50, 50, 50), 3)  # border
            cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 50),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 4)  # highlight text
            return True
        else:
            return False

print("Initializing webcam...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Initializing hand detector...")
detector = HandDetector(detectionCon=0.8, maxHands=1)

buttonListValue = [["1", "2", "3", "+"],
                   ["4", "5", "6", "-"],
                   ["7", "8", "9", "*"],
                   ["0", "/", ".", "="],
                   ["C", "<-", "", ""]]  # Added "C" button for Clear and "<-" for Delete

buttonList = []
for y in range(len(buttonListValue)):
    for x in range(len(buttonListValue[y])):
        xPos = x * 70 + 350  # starting from 350 pixel in the width
        yPos = y * 70 + 100  # starting from 100 pixel in the height
        buttonList.append(Button((xPos, yPos), 70, 70, buttonListValue[y][x], "number" if buttonListValue[y][x].isdigit() else "operator"))

equation = ""
delayCounter = 0

print("Starting main loop...")
while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to capture image.")
        break

    img = cv2.flip(img, 1)

    hand, img = detector.findHands(img, flipType=False)

    cv2.rectangle(img, (350, 30), (350 + 280, 100),
                  (250, 251, 217), cv2.FILLED)  # display background
    cv2.rectangle(img, (350, 30), (350 + 280, 100),
                  (50, 50, 50), 3)  # display border

    for button in buttonList:
        button.draw(img)

    if hand:
        lmList = hand[0]["lmList"]
        if len(lmList) > 12:
            x1, y1 = lmList[8][:2]
            x2, y2 = lmList[12][:2]
            distance, _, img = detector.findDistance((x1, y1), (x2, y2), img)
            x, y = lmList[8][:2]
            if distance < 50:
                for button in buttonList:
                    if button.checkClicking(x, y, img) and delayCounter == 0:
                        if button.value == "=":
                            try:
                                equation = str(eval(equation))
                            except Exception as e:
                                equation = "Error"
                                print("Error in evaluation:", e)
                        elif button.value == "C":  # Clear button
                            equation = ""
                        elif button.value == "<-":  # Delete button
                            equation = equation[:-1]
                        else:
                            equation += button.value
                        delayCounter = 1

    if delayCounter != 0:
        delayCounter += 1
        if delayCounter > 10:
            delayCounter = 0

    cv2.putText(img, equation, (355, 80),
                cv2.FONT_HERSHEY_PLAIN, 2, (50, 50, 50), 2)
    cv2.imshow("image", img)
    key = cv2.waitKey(1)
    if key == ord("c"):  # clear display
        equation = ""
    if key == ord('q'):  # quit program
        break

print("Releasing webcam and closing windows...")
cap.release()
cv2.destroyAllWindows()

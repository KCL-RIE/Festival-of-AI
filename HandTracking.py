import cv2 
import math
import mediapipe as mp
import HandModule as htm

pTime = 0
cTime = 0
cap = cv2.VideoCapture(0)
default_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
default_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
detector = htm.handDetector()
print("Default Resolution:", default_width, "x", default_height)

def draw_left_circle(img):
    circle_center = (55, 240)  # Coordinates of the center of the circle
    circle_radius = 50  # Radius of the circle
    circle_color = (0, 255, 255)  # Color of the circle, in BGR format
    circle_thickness = 2  # Thickness of the circle boundary
    cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)
    
def point_inside_circle(point, center, radius):
    distance = math.sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)
    return distance <= radius
    
def draw_right_circle(img):
    circle_center = (580, 240)  # Coordinates of the center of the circle
    circle_radius = 50  # Radius of the circle
    circle_color = (0, 255, 255)  # Color of the circle, in BGR format
    circle_thickness = 2  # Thickness of the circle boundary
    cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)



while True: 
    success, img = cap.read()
    img = cv2.resize(img, (default_width, default_height))
    img = cv2.flip(img, 1)
    draw_left_circle(img)
    draw_right_circle(img)
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:  
        index_finger_tip = lmList[8][1], lmList[8][2]
        cv2.circle(img, index_finger_tip, 15, (0, 255, 0), cv2.FILLED)
        print("Index finger tip coordinates:", index_finger_tip)
        
        if point_inside_circle(index_finger_tip, (55, 240), 50):
            print("Turning left")
        elif point_inside_circle(index_finger_tip, (580, 240), 50):
            print("Turning right")

    cv2.imshow("Image", img)
    cv2.waitKey(1)
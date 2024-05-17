import cv2
import math
import time
import mediapipe as mp
import HandModule as htm
import socket

# Setup connection outside the loop
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
esp_ip = '192.168.149.116'  # IP of the ESP32
port = 80
s.connect((esp_ip, port))

# Function to send data to ESP32
def send_to_esp32(message):
    message += '\n'
    s.sendall(message.encode())

# Camera and hand detection initialization
cap = cv2.VideoCapture(0)
default_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
default_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
detector = htm.handDetector()
print("Default Resolution:", default_width, "x", default_height)

# Drawing functions for interface
def draw_left_circle(img):
    circle_center = (150, 250)
    circle_radius = 50
    circle_color = (0, 255, 255)
    circle_thickness = 2
    cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)
    cv2.putText(img, 'Left', (circle_center[0] - 40, circle_center[1] + 75), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

def draw_right_circle(img):
    circle_center = (480, 250)
    circle_radius = 50
    circle_color = (0, 255, 255)
    circle_thickness = 2
    cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)
    cv2.putText(img, 'Right', (circle_center[0] - 40, circle_center[1] + 75), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

def draw_top_circle(img):
    circle_center = (320, 100)
    circle_radius = 50
    circle_color = (0, 255, 255)
    circle_thickness = 2
    cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)
    cv2.putText(img, 'Up', (circle_center[0] - 30, circle_center[1] - 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

def draw_bottom_circle(img):
    circle_center = (320, 360)
    circle_radius = 50
    circle_color = (0, 255, 255)
    circle_thickness = 2
    cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)
    cv2.putText(img, 'Down', (circle_center[0] - 50, circle_center[1] + 75), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

# Utility function to check if a point is inside a circle
def point_inside_circle(point, center, radius):
    distance = math.sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)
    return distance <= radius

try:
    while True:
        success, img = cap.read()
        img = cv2.resize(img, (default_width, default_height))
        img = cv2.flip(img, 1)
        draw_left_circle(img)
        draw_right_circle(img)
        draw_top_circle(img)
        draw_bottom_circle(img)
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        
        if len(lmList) != 0:
            index_finger_tip = lmList[8][1], lmList[8][2]
            cv2.circle(img, index_finger_tip, 15, (0, 255, 0), cv2.FILLED)
            print(f"{lmList[8][1]},{lmList[8][2]}")
            if point_inside_circle(index_finger_tip, (150, 250), 50):
                print("Turning left")
                send_to_esp32("Left")
                time.sleep(0.1)
            elif point_inside_circle(index_finger_tip, (480, 250), 50):
                print("Turning right")
                send_to_esp32("Right")
                time.sleep(0.1)
            elif point_inside_circle(index_finger_tip, (320, 100), 50):
                print("Moving up")
                send_to_esp32("Forward")
                time.sleep(0.1)
            elif point_inside_circle(index_finger_tip, (320, 360), 50):
                print("Moving down")
                send_to_esp32("Backward")
                time.sleep(0.1)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break

finally:
    s.close()  # Ensure the socket is closed on exit
    cap.release()
    cv2.destroyAllWindows()

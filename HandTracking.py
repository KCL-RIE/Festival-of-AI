import cv2
import math
import time
import tkinter as tk
from tkinter import ttk
import mediapipe as mp
import HandModule as htm
from PIL import Image, ImageTk
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

# Utility function to check if a point is inside a circle
def point_inside_circle(point, center, radius):
    distance = math.sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)
    return distance <= radius

class HandDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Detection App")
        self.root.attributes('-fullscreen', True)  # Make the window full screen

        # Timer variables
        self.start_time = None
        self.timer_running = False
        self.robot_moving = False

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Adjust video dimensions to fit the screen height while maintaining aspect ratio
        self.video_width = int(self.screen_height * (default_width / default_height))
        self.video_height = self.screen_height

        # Create a frame for the video
        self.video_frame = tk.Frame(root, width=self.video_width, height=self.video_height)
        self.video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a canvas to display the video
        self.canvas = tk.Canvas(self.video_frame, width=self.video_width, height=self.video_height)
        self.canvas.pack()

        # Create a frame for the buttons
        self.button_frame = tk.Frame(root, width=self.screen_width - self.video_width, height=self.screen_height)
        self.button_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add Start and Stop buttons
        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_timer, font=("Helvetica", 16), width=15, height=2, highlightbackground='black', highlightcolor='black', highlightthickness=2)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_timer, font=("Helvetica", 16), width=15, height=2, highlightbackground='black', highlightcolor='black', highlightthickness=2)
        self.stop_button.pack(pady=20)

        # Label to display timer
        self.timer_label = tk.Label(self.button_frame, text="Timer: 0m 0s", font=("Helvetica", 24))
        self.timer_label.pack(pady=20)

        # Add New Player button
        self.new_player_button = tk.Button(self.button_frame, text="New Player", command=self.show_name_entry_popup, font=("Helvetica", 16), width=15, height=2, highlightbackground='black', highlightcolor='black', highlightthickness=2)
        self.new_player_button.pack(pady=20)

        # Start the video loop
        self.update_video()

    def show_name_entry_popup(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Enter Name")

        # Center the popup window
        popup_width = 300
        popup_height = 150
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        self.popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        self.popup_label = tk.Label(self.popup, text="Enter your name:", font=("Helvetica", 14))
        self.popup_label.pack(pady=10)

        self.name_entry = tk.Entry(self.popup, font=("Helvetica", 14), width=20)
        self.name_entry.pack(pady=10)

        self.submit_button = tk.Button(self.popup, text="Submit", command=self.submit_name, font=("Helvetica", 14))
        self.submit_button.pack(pady=10)

    def submit_name(self):
        self.player_name = self.name_entry.get()
        if self.player_name:
            self.popup.destroy()
            self.reset_timer()

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.robot_moving = True
        self.update_timer()

    def stop_timer(self):
        self.timer_running = False
        self.robot_moving = False
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.show_finish_popup(elapsed_time)

    def show_finish_popup(self, elapsed_time):
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        elapsed_time_formatted = f"{minutes}m {seconds}s"

        self.finish_popup = tk.Toplevel(self.root)
        self.finish_popup.title("Race Finished")

        # Center the popup window
        popup_width = 300
        popup_height = 150
        screen_width = self.finish_popup.winfo_screenwidth()
        screen_height = self.finish_popup.winfo_screenheight()
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        self.finish_popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        self.finish_popup_label = tk.Label(self.finish_popup, text=f"{self.player_name}, you finished in {elapsed_time_formatted}!", font=("Helvetica", 14))
        self.finish_popup_label.pack(pady=10)

        self.new_player_button_popup = tk.Button(self.finish_popup, text="New Player", command=self.new_player, font=("Helvetica", 14))
        self.new_player_button_popup.pack(pady=10)

    def new_player(self):
        self.finish_popup.destroy()
        self.reset_timer()
        self.show_name_entry_popup()

    def reset_timer(self):
        self.start_time = None
        self.timer_running = False
        self.robot_moving = False
        self.timer_label.config(text="Timer: 0m 0s")

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            self.timer_label.config(text=f"Timer: {minutes}m {seconds}s")
            self.root.after(100, self.update_timer)

    def update_video(self):
        success, img = cap.read()
        if not success:
            return

        # Mirror the image horizontally
        img = cv2.flip(img, 1)

        img = cv2.resize(img, (self.video_width, self.video_height))
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if lmList:
            index_finger_tip = lmList[8][1:]
            cv2.circle(img, (index_finger_tip[0], index_finger_tip[1]), 10, (255, 0, 255), cv2.FILLED)

            if self.timer_running:
                if point_inside_circle(index_finger_tip, (150, 250), 50):
                    print("Left")
                    send_to_esp32("Left")
                    time.sleep(0.1)
                elif point_inside_circle(index_finger_tip, (480, 250), 50):
                    print("Right")
                    send_to_esp32("Right")
                    time.sleep(0.1)
                elif point_inside_circle(index_finger_tip, (320, 100), 50):
                    print("Forward")
                    send_to_esp32("Forward")
                    time.sleep(0.1)
                elif point_inside_circle(index_finger_tip, (320, 360), 50):
                    print("Backward")
                    send_to_esp32("Backward")
                    time.sleep(0.1)

        # Draw control circles
        self.draw_left_circle(img)
        self.draw_right_circle(img)
        self.draw_top_circle(img)
        self.draw_bottom_circle(img)

        # Convert the image to PhotoImage
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        # Update the canvas image
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.canvas.img_tk = img_tk  # Keep a reference to avoid garbage collection

        # Call update_video again after 10 ms
        self.root.after(10, self.update_video)

    def draw_left_circle(self, img):
        circle_center = (150, 250)
        circle_radius = 50
        circle_color = (0, 255, 255)
        circle_thickness = 2
        cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)
        cv2.putText(img, 'Left', (circle_center[0] - 40, circle_center[1] + 75), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2, cv2.LINE_AA)

    def draw_right_circle(self, img):
        circle_center = (480, 250)
        circle_radius = 50
        circle_color = (0, 255, 255)
        circle_thickness = 2
        cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)
        cv2.putText(img, 'Right', (circle_center[0] - 40, circle_center[1] + 75), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2, cv2.LINE_AA)

    def draw_top_circle(self, img):
        circle_center = (320, 100)
        circle_radius = 50
        circle_color = (0, 255, 255)
        circle_thickness = 2
        cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)
        cv2.putText(img, 'Up', (circle_center[0] - 30, circle_center[1] - 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2, cv2.LINE_AA)

    def draw_bottom_circle(self, img):
        circle_center = (320, 360)
        circle_radius = 50
        circle_color = (0, 255, 255)
        circle_thickness = 2
        cv2.circle(img, circle_center, circle_radius, circle_color, circle_thickness)
        cv2.putText(img, 'Down', (circle_center[0] - 50, circle_center[1] + 75), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2, cv2.LINE_AA)

if __name__ == "__main__":
    root = tk.Tk()
    app = HandDetectionApp(root)
    root.mainloop()
    cap.release()
    cv2.destroyAllWindows()

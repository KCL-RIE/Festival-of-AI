import cv2
import math
import time
import tkinter as tk
from tkinter import ttk
import mediapipe as mp
import HandModule as htm
from PIL import Image, ImageTk

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
        self.times = []

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

        # Create a frame for the welcome screen
        self.welcome_frame = tk.Frame(root, width=self.screen_width - self.video_width, height=self.screen_height)
        self.welcome_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add welcome screen components
        self.new_player_button = tk.Button(self.welcome_frame, text="New Player", command=self.show_name_entry_popup, font=("Helvetica", 16), width=15, height=2, highlightbackground='black', highlightcolor='black', highlightthickness=2)
        self.new_player_button.pack(pady=20)

        # Create a frame for the buttons (hidden initially)
        self.button_frame = tk.Frame(root, width=self.screen_width - self.video_width, height=self.screen_height)
        
        # Add Start and Stop buttons (hidden initially)
        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_timer, font=("Helvetica", 16), width=15, height=2, highlightbackground='black', highlightcolor='black', highlightthickness=2)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_timer, font=("Helvetica", 16), width=15, height=2, highlightbackground='black', highlightcolor='black', highlightthickness=2)
        self.stop_button.pack(pady=20)

        # Label to display timer
        self.timer_label = tk.Label(self.button_frame, text="Timer: 0m 0s", font=("Helvetica", 24))
        self.timer_label.pack(pady=20)

        # Labels to display top three times
        self.first_label = tk.Label(self.button_frame, text="1st: N/A", font=("Helvetica", 18))
        self.first_label.pack(pady=10)
        self.second_label = tk.Label(self.button_frame, text="2nd: N/A", font=("Helvetica", 18))
        self.second_label.pack(pady=10)
        self.third_label = tk.Label(self.button_frame, text="3rd: N/A", font=("Helvetica", 18))
        self.third_label.pack(pady=10)

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
        player_name = self.name_entry.get()
        if player_name:
            self.popup.destroy()
            self.welcome_frame.pack_forget()
            self.button_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.times.append(elapsed_time)
            self.times.sort()
            self.times = self.times[:3]  # Keep only the top 3 times
            self.update_top_times()

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            self.timer_label.config(text=f"Timer: {minutes}m {seconds}s")
            self.root.after(100, self.update_timer)

    def update_top_times(self):
        top_times = ["N/A"] * 3
        for i, t in enumerate(self.times):
            minutes = int(t // 60)
            seconds = int(t % 60)
            top_times[i] = f"{minutes}m {seconds}s"
        self.first_label.config(text=f"1st: {top_times[0]}")
        self.second_label.config(text=f"2nd: {top_times[1]}")
        self.third_label.config(text=f"3rd: {top_times[2]}")

    def update_video(self):
        success, img = cap.read()
        img = cv2.resize(img, (self.video_width, self.video_height))
        img = cv2.flip(img, 1)
        
        # Draw circles and labels
        self.draw_left_circle(img)
        self.draw_right_circle(img)
        self.draw_top_circle(img)
        self.draw_bottom_circle(img)

        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        
        if len(lmList) != 0:
            index_finger_tip = lmList[8][1], lmList[8][2]
            cv2.circle(img, index_finger_tip, 15, (0, 255, 0), cv2.FILLED)
            print(f"{lmList[8][1]},{lmList[8][2]}")
            if point_inside_circle(index_finger_tip, (150, 250), 50):
                print("Turning left")
            elif point_inside_circle(index_finger_tip, (480, 250), 50):
                print("Turning right")
            elif point_inside_circle(index_finger_tip, (320, 100), 50):
                print("Moving up")
            elif point_inside_circle(index_finger_tip, (320, 360), 50):
                print("Moving down")

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

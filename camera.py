import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import tkinter as tk
import pyautogui as pag

# Define hand connections based on MediaPipe Hand Landmarks
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16), (13, 17),
    (0, 17), (17, 18), (18, 19), (19, 20)
]

# Initialize webcam
cap = cv2.VideoCapture(0)

# Define screen dimensions
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Define quit flag
running = True

def quit_app(event):
    global running
    running = False

root.bind('<Control-q>', quit_app)
root.withdraw()

# Allow for mouse to reach corner of screen without triggering failsafe
pag.FAILSAFE = False

# cv2.namedWindow('Webcam', cv2.WINDOW_NORMAL)
# cv2.setWindowProperty('Webcam', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Define MediaPipe Hand Landmarker
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
hands = vision.HandLandmarker.create_from_options(options)

# Initialize variables for location calculations
mid_x, mid_y, avg_x, avg_y, prev_x, prev_y = 0, 0, 0, 0, 0, 0
threshold = ((screen_width)**2 + (screen_height)**2)**0.5 * 0.0005

# Main loop
while running:
    success, frame = cap.read()
    if success:
        RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=RGB_frame)
        result = hands.detect(mp_image)

        if result.hand_landmarks:
            height, width, _ = frame.shape
            # for hand_landmarks in result.hand_landmarks:
            #     for landmark in hand_landmarks:
            #         x = int(landmark.x * width)
            #         y = int(landmark.y * height)
            #         cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

            #     for connection in HAND_CONNECTIONS:
            #         start_idx, end_idx = connection
            #         start = hand_landmarks[start_idx]
            #         end = hand_landmarks[end_idx]
            #         start_x = int(start.x * width)
            #         start_y = int(start.y * height)
            #         end_x = int(end.x * width)
            #         end_y = int(end.y * height)
            #         cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

            avg_x = result.hand_landmarks[0][9].x
            avg_y = result.hand_landmarks[0][9].y
            # hand_mid_x = int(avg_x * width)
            # hand_mid_y = int(avg_y * height)
            # cv2.circle(frame, (hand_mid_x, hand_mid_y), 10, (255, 0, 0), -1)

            mid_x = int((avg_x-0.5) * screen_width)
            mid_y = int((avg_y-0.5) * screen_height)

            thumb_tip = result.hand_landmarks[0][4]
            index_tip = result.hand_landmarks[0][8]
            middle_tip = result.hand_landmarks[0][12]
            I_pinch_distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2 + (thumb_tip.z - index_tip.z)**2)**0.5
            M_pinch_distance = ((thumb_tip.x - middle_tip.x)**2 + (thumb_tip.y - middle_tip.y)**2 + (thumb_tip.z - middle_tip.z)**2)**0.5
            print(f"Middle pinch Z: {middle_tip.z}")

            if I_pinch_distance < threshold * abs(middle_tip.z):
                pag.click()
            
            if M_pinch_distance < threshold * abs(middle_tip.z):
                pag.rightClick()

        # cv2.imshow('Webcam', frame)

        move_distance = ((mid_x - prev_x)**2 + (mid_y - prev_y)**2)**0.5
        
        if move_distance > threshold:
            pag.moveTo(screen_width//2 - mid_x * 1.5, screen_height//2 + mid_y * 1.5)
            prev_x, prev_y = mid_x, mid_y

        root.update()

cap.release()
root.destroy()
# cv2.destroyAllWindows()
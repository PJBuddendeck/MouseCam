import sys
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import tkinter as tk
import pyautogui as pag
import keyboard

# Define hand connections based on MediaPipe Hand Landmarks
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16), (13, 17),
    (0, 17), (17, 18), (18, 19), (19, 20)
]

# Find screen dimensions
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.withdraw()

# Define mouse up and down booleans
L_mouse_down = False
R_mouse_down = False

# Define MediaPipe Hand Landmarker
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
hands = vision.HandLandmarker.create_from_options(options)

# Initialize variables for location calculations
mid_x, mid_y, avg_x, avg_y, prev_x, prev_y = 0, 0, 0, 0, 0, 0
threshold = ((screen_width)**2 + (screen_height)**2)**0.5

# Function to exit the application when ctrl+shift+q is pressed
running = True

def quit_app():
    global running
    running = False

keyboard.add_hotkey('ctrl+shift+q', quit_app)

# Function to initialize the webcam and check if it is accessible
def init_webcam():
    for i in range(5):
        test_cap = cv2.VideoCapture(i)
        if test_cap.isOpened():
            test_cap.release()
            return i
    raise Exception("No accessible webcam found.")

# Function to draw hand landmarks and connections
def draw_Landmarks(frame, r_hand_landmarks):
    height, width, _ = frame.shape
    for hand_landmarks in r_hand_landmarks:
        for landmark in hand_landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

        for connection in HAND_CONNECTIONS:
            start_idx, end_idx = connection
            start = hand_landmarks[start_idx]
            end = hand_landmarks[end_idx]
            start_x = int(start.x * width)
            start_y = int(start.y * height)
            end_x = int(end.x * width)
            end_y = int(end.y * height)
            cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

# Main loop
def main():
    try:
        args = sys.argv[1:]
    except:
        args = None
    show_cam_mode = '-show' in args

    # Initialize webcam
    # Default uses function, but index can be specified as a command line argument
    webcam_index = None
    for i in args:
        if i.isdigit():
            webcam_index = int(i)
            break
    if webcam_index is not None:
        cap = cv2.VideoCapture(webcam_index)
        if not cap.isOpened():
            print("Specified webcam index is inaccessible. Using default webcam initializer.")
            cap = cv2.VideoCapture(init_webcam())
    else:
        cap = cv2.VideoCapture(init_webcam())
    
    while running:
        # Define window needed for webcam display if show_cam_mode is enabled
        if show_cam_mode:
            cv2.namedWindow('Webcam', cv2.WINDOW_NORMAL)

        # Read frame from webcam
        success, frame = cap.read()
        if success:
            RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=RGB_frame)
            result = hands.detect(mp_image)

            # Process hand landmarks if detected
            if result.hand_landmarks:

                # Draw landmarks if show_cam_mode is enabled
                if show_cam_mode:
                    draw_Landmarks(frame, result.hand_landmarks)

                # Use base of middle finger as reference point for cursor movement
                # On a scale of 0 to 1
                global avg_x, avg_y
                avg_x = result.hand_landmarks[0][9].x
                avg_y = result.hand_landmarks[0][9].y

                # Calculate cursor position based on average hand position
                # Scale translated so 0,0 is the center of the screen
                global mid_x, mid_y
                mid_x = int((avg_x-0.5) * screen_width)
                mid_y = int((avg_y-0.5) * screen_height)

                # Find positions of thumb tip, index tip, and middle tip to calculate pinch distance for mouse clicks
                thumb_tip = result.hand_landmarks[0][4]
                index_tip = result.hand_landmarks[0][8]
                middle_tip = result.hand_landmarks[0][12]
                I_pinch_distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2 + (thumb_tip.z - index_tip.z)**2)**0.5
                M_pinch_distance = ((thumb_tip.x - middle_tip.x)**2 + (thumb_tip.y - middle_tip.y)**2 + (thumb_tip.z - middle_tip.z)**2)**0.5
                pinch_threshold = threshold * 0.0005 * abs(middle_tip.z)

                # Check if pinch conditions are met for left and right clicks, and update mouse button states accordingly
                global L_mouse_down, R_mouse_down
                if I_pinch_distance < pinch_threshold:
                    if not L_mouse_down:
                        pag.mouseDown()
                        L_mouse_down = True
                else:
                    if L_mouse_down:
                        pag.mouseUp()
                        L_mouse_down = False
                
                if M_pinch_distance < pinch_threshold:
                    if not R_mouse_down:
                        pag.mouseDown(button='right')
                        R_mouse_down = True
                else:
                    if R_mouse_down:
                        pag.mouseUp(button='right')
                        R_mouse_down = False

            # Open the webcam window if show_cam_mode is enabled
            if show_cam_mode:
                cv2.imshow('Webcam', frame)

            # Calculate movement distance and move cursor if it exceeds the threshold
            # Allows for more stable cursor movement by ignoring small jitters in hand position
            global prev_x, prev_y
            move_distance = ((mid_x - prev_x)**2 + (mid_y - prev_y)**2)**0.5
            
            if move_distance > threshold * 0.003:
                pag.moveTo(screen_width//2 - mid_x * 1.5, screen_height//2 + mid_y * 1.5)
                prev_x, prev_y = mid_x, mid_y

            root.update()

    # Raise mouse buttons
    pag.mouseUp()
    pag.mouseUp(button='right')

    # Cleanup
    root.destroy()
    cap.release()
    hands.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
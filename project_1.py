import tkinter as tk
from datetime import datetime
import cv2
from PIL import Image, ImageTk
import time
from ultralytics import YOLO

# ---------------- WINDOW ---------------- #
root = tk.Tk()
root.title("Smart Office Presence Monitoring System (YOLO + DND)")
root.geometry("800x700")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

# ---------------- GLOBAL VARIABLES ---------------- #
cap = None
present = False
last_status = None

last_seen_time = 0
last_not_seen_time = 0
DETECTION_DELAY = 3

dnd_active = False  # Do Not Disturb flag

# ---------------- LOAD YOLO ---------------- #
model = YOLO("yolov8n.pt")

# ---------------- FUNCTIONS ---------------- #

def log_history(message, color=None):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = f"{time_now} | {message}\n"

    # Save to file
    with open("status_history.txt", "a") as file:
        file.write(record)

    # Display in GUI
    if color:
        history_box.insert(tk.END, record, color)
        history_box.tag_config(color, foreground=color)
    else:
        history_box.insert(tk.END, record)

    history_box.see(tk.END)


def clear_history():
    history_box.delete(1.0, tk.END)


def set_do_not_disturb():
    global dnd_active
    dnd_active = True
    log_history("Do Not Disturb", "red")


def resume_detection():
    global dnd_active
    dnd_active = False
    log_history("Detection Resumed")


# ---------------- CAMERA ---------------- #

def start_camera():
    global cap
    url = "http://192.168.1.6:4747/video"
    cap = cv2.VideoCapture(url)
    show_frame()


def show_frame():
    global present, last_status
    global last_seen_time, last_not_seen_time

    if cap is not None:
        ret, frame = cap.read()

        if ret:
            frame = cv2.resize(frame, (640, 480))

            # ---------------- DND MODE ---------------- #
            if dnd_active:
                cv2.putText(frame, "DO NOT DISTURB",
                            (40, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3)

            else:
                # ---------------- YOLO DETECTION ---------------- #
                results = model(frame, verbose=False)

                person_detected = False

                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])

                        if cls == 0:  # person
                            person_detected = True
                            x1, y1, x2, y2 = map(int, box.xyxy[0])

                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, "Person",
                                        (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.7, (0, 255, 0), 2)

                current_time = time.time()

                # -------- ENTRY -------- #
                if person_detected:
                    last_seen_time = current_time

                    if not present and (current_time - last_not_seen_time > DETECTION_DELAY):
                        present = True
                        if last_status != "entered":
                            log_history("Miss Entered")
                            last_status = "entered"

                    cv2.putText(frame, "Miss is Present",
                                (40, 50),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 0), 3)

                # -------- EXIT -------- #
                else:
                    last_not_seen_time = current_time

                    if present and (current_time - last_seen_time > DETECTION_DELAY):
                        present = False
                        if last_status != "left":
                            log_history("Miss Left")
                            last_status = "left"

                    cv2.putText(frame, "No Person Detected",
                                (40, 50),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 3)

            # ---------------- DISPLAY ---------------- #
            frame = cv2.resize(frame, (400, 250))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)

        camera_label.after(10, show_frame)


# ---------------- UI ---------------- #

tk.Label(root, text="SMART FACULTY PRESENCE SYSTEM (YOLO + DND)",
         font=("Arial", 18, "bold")).pack(pady=10)

tk.Button(root, text="Start Camera",
          command=start_camera, bg="blue", fg="white").pack(pady=10)

tk.Button(root, text="Do Not Disturb",
          command=set_do_not_disturb, bg="black", fg="white").pack(pady=5)

tk.Button(root, text="Resume",
          command=resume_detection, bg="green", fg="white").pack(pady=5)

tk.Button(root, text="Clear History",
          command=clear_history, bg="red", fg="white").pack(pady=5)

camera_label = tk.Label(root)
camera_label.pack(pady=10)

tk.Label(root, text="Status History:").pack(pady=5)

history_box = tk.Text(root, height=15, width=90)
history_box.pack()

# ---------------- RUN ---------------- #
root.mainloop()
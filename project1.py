import tkinter as tk
from tkinter import messagebox
from datetime import datetime

root = tk.Tk()
root.title("Smart Office Presence Monitoring System")
root.geometry("500x500")
root.resizable(False, False)
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))



# ---------------- FUNCTIONS ---------------- #

def update_status():
    name = name_entry.get().strip()
    status = status_var.get()
    time = exit_time.get().strip()

    if name == "":
        messagebox.showwarning("Input Error", "Please enter faculty name!")
        return

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if time:
        record = f"{time_now} | {name} | {status} | Will be available in {time}\n"
    else:
        record = f"{time_now} | {name} | {status}\n"

    # Save to file
    with open("status_history.txt", "a") as file:
        file.write(record)

    # Display in history box
    history_box.insert(tk.END, record)

    name_entry.delete(0, tk.END)


def clear_history():
    history_box.delete(1.0, tk.END)


# ---------------- UI DESIGN ---------------- #

title_label = tk.Label(root, text="SMART FACULTY PRESENCE SYSTEM",
                       font=("Arial", 16, "bold"))
title_label.pack(pady=15)

# Faculty Name
tk.Label(root, text="Faculty Name:").pack()
name_entry = tk.Entry(root, width=30)
name_entry.pack(pady=5)

#exit time
tk.Label(root, text="Ending Time (optional):").pack()
exit_time = tk.Entry(root, width=30)
exit_time.pack(pady=5)

# Status Dropdown
tk.Label(root, text="Select Status:").pack()
status_var = tk.StringVar()
status_var.set("On table")

status_menu = tk.OptionMenu(root, status_var,
                            "On table", "Specific Work", "Meeting", "Leave")
status_menu.pack(pady=5)

# Buttons
tk.Button(root, text="Update Status",
          command=update_status, bg="green", fg="white").pack(pady=10)

tk.Button(root, text="Clear History",
          command=clear_history, bg="red", fg="white").pack(pady=5)

# History Display
tk.Label(root, text="Status History:").pack(pady=5)

history_box = tk.Text(root, height=35, width=85)
history_box.pack()

root.mainloop()

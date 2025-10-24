import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def launch_tracker(file_path, title):
    subprocess.Popen(["python", "tracker_updated.py", file_path, title])

def proceed():
    choice = option.get()
    if choice == "new":
        title = title_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a title for the new expense sheet.")
            return
        file_path = f"{title}.xlsx"
        if os.path.exists(file_path):
            error_label.config(text="*File already existing with this name")
            return
        launch_tracker(file_path, title)
        root.destroy()
    elif choice == "load":
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            title = os.path.splitext(os.path.basename(file_path))[0]
            launch_tracker(file_path, title)
            root.destroy()
        else:
            messagebox.showwarning("No file selected", "Please select an existing expense sheet.")

def toggle_input():
    if option.get() == "new":
        title_entry.config(state="normal")
    else:
        title_entry.delete(0, tk.END)
        title_entry.config(state="disabled")
        error_label.config(text="")  # Clear error when switching to load

def clear_error_on_typing(event):
    error_label.config(text="")  # Clear error only when typing or deleting

# GUI Setup
root = tk.Tk()
root.title("Expense Tracker Launcher")
root.geometry("500x220")  # Increased horizontal size

option = tk.StringVar(value="new")

# Radio buttons side by side
radio_frame = tk.Frame(root)
radio_frame.pack(pady=20)

tk.Label(radio_frame, text="Choose an option:").pack(side=tk.LEFT, padx=10)
tk.Radiobutton(radio_frame, text="New Expense Sheet", variable=option, value="new", command=toggle_input).pack(side=tk.LEFT, padx=10)
tk.Radiobutton(radio_frame, text="Load Existing Sheet", variable=option, value="load", command=toggle_input).pack(side=tk.LEFT, padx=10)

# Entry box below radio buttons
entry_frame = tk.Frame(root)
entry_frame.pack(pady=10)

tk.Label(entry_frame, text="Expense Sheet Title:").pack()
title_entry = tk.Entry(entry_frame, width=40)
title_entry.pack()

# Error label below entry
error_label = tk.Label(entry_frame, text="", fg="red")
error_label.pack()

# Bind any key press to clear error
title_entry.bind("<Key>", clear_error_on_typing)

# Continue button below entry
tk.Button(root, text="Continue", command=proceed).pack(pady=10)

toggle_input()
root.bind("<Return>", lambda event: proceed())  # Enable Enter key functionality
root.mainloop()
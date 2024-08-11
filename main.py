import cv2
import numpy as np
import pyautogui
import tkinter as tk
from tkinter import ttk, filedialog
import threading
import time
import os

class ScreenRecorder:
    def __init__(self, master):
        self.master = master
        self.master.title("Screen Recorder")
        self.master.geometry("300x280")

        self.recording = False
        self.paused = False
        self.frames = []
        self.frame_rate = 10  # Adjust this value to change the frame rate (frames per second)

        self.setup_ui()

    def setup_ui(self):
        self.start_button = ttk.Button(self.master, text="Start", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(self.master, text="Stop", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.pause_button = ttk.Button(self.master, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.pack(pady=5)

        self.delete_button = ttk.Button(self.master, text="Delete", command=self.delete_recording, state=tk.DISABLED)
        self.delete_button.pack(pady=5)

        self.save_button = ttk.Button(self.master, text="Save", command=self.save_recording, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.status_label = tk.Label(self.master, text="Ready")
        self.status_label.pack(pady=5)

        self.indicator_canvas = tk.Canvas(self.master, width=20, height=20)
        self.indicator_canvas.pack(pady=5)
        self.indicator = self.indicator_canvas.create_oval(5, 5, 15, 15, fill="grey")

    def start_recording(self):
        self.start_button.config(state=tk.DISABLED)
        self.status_label.config(text="Starting in 5 seconds...")
        self.master.after(1000, lambda: self.countdown(4))

    def countdown(self, count):
        if count > 0:
            self.status_label.config(text=f"Starting in {count} seconds...")
            self.master.after(1000, lambda: self.countdown(count - 1))
        else:
            self.recording = True
            self.status_label.config(text="Recording")
            self.indicator_canvas.itemconfig(self.indicator, fill="red")
            self.stop_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
            threading.Thread(target=self.record_screen, daemon=True).start()

    def stop_recording(self):
        self.recording = False
        self.status_label.config(text="Stopped")
        self.indicator_canvas.itemconfig(self.indicator, fill="grey")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")
        self.status_label.config(text="Paused" if self.paused else "Recording")
        self.indicator_canvas.itemconfig(self.indicator, fill="yellow" if self.paused else "red")

    def record_screen(self):
        last_capture_time = time.time()
        while self.recording:
            current_time = time.time()
            if not self.paused and (current_time - last_capture_time) >= 1 / self.frame_rate:
                screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                self.frames.append(frame)
                last_capture_time = current_time
            time.sleep(0.01)  # Short sleep to prevent excessive CPU usage

    def delete_recording(self):
        self.frames = []
        self.delete_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.status_label.config(text="Deleted")

    def save_recording(self):
        if self.frames:
            try:
                output_file = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                           filetypes=[("MP4 files", "*.mp4")])
                if output_file:
                    height, width, _ = self.frames[0].shape
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output_file, fourcc, self.frame_rate, (width, height))

                    for frame in self.frames:
                        out.write(frame)

                    out.release()
                    self.status_label.config(text=f"Saved as {output_file}")
                    print(f"Video saved as {output_file}")
                else:
                    self.status_label.config(text="Save cancelled")
            except Exception as e:
                self.status_label.config(text=f"Error: {str(e)}")
                print(f"Error saving video: {str(e)}")
        else:
            self.status_label.config(text="No frames to save")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.mainloop()
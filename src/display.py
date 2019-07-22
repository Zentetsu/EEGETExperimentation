from tkinter import Tk, Canvas, Button, Entry, StringVar, messagebox, Checkbutton, Frame
from screen_recording import ScreenRecording
from eye_tracker import EyeTracker
from copy import deepcopy
import threading
import time


class Display:
    def __init__(self):
        self.eye_tracker = None
        self.screen_recording = None

        self.windows = Tk()

        self.screen_width = self.windows.winfo_screenwidth()
        self.screen_height = self.windows.winfo_screenheight()

        xFig, yFig = self.screen_width, self.screen_height
        self.canvas_fig = Canvas(self.windows, width=xFig, height=yFig, background='white')
        self.canvas_fig.pack()

        self.link_et = Button(self.windows, text="Unlink Eye-Tracker", command=self.linkET, width=25)
        self.link_sr = Button(self.windows, text="Enable screen recording", command=self.enableScreenRecording, width=25)
        self.link_et_w = self.canvas_fig.create_window(self.screen_width/2, self.screen_height/2, window=self.link_et)
        self.link_et_w = self.canvas_fig.create_window(self.screen_width/2, self.screen_height/2+30, window=self.link_sr)

        self.value = StringVar(self.windows)
        self.name = Entry(self.windows, textvariable=self.value, width=10)

        self.canvas_fig.bind("<Configure>", self.resize)
        self.canvas_fig.bind_all("<KeyPress>", self.keyboard)

        self.windows.mainloop()

    def resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.screen_width
        hscale = float(event.height)/self.screen_height
        self.screen_width = event.width
        self.screen_height = event.height
        # resize the canvas 
        self.canvas_fig.config(width=self.screen_width, height=self.screen_height)
        # rescale all the objects tagged with the "all" tag
        self.canvas_fig.scale("all", 0, 0, wscale, hscale)

        string_info = self.windows.winfo_geometry()
        string_info = string_info.split("+")
        self.info = string_info[0].split("x")
        self.info.extend(string_info[1:])
        self.info = [int(x) for x in self.info]

    def keyboard(self, event):
        if event.keysym == "Return":
            self.screen_width = self.windows.winfo_screenwidth()
            self.screen_height = self.windows.winfo_screenheight()

            # print(self.screen_width)
            # print(self.screen_height)
    
    def linkET(self):
        if self.eye_tracker is None:
            self.eye_tracker = EyeTracker()
            if self.eye_tracker.started():
                self.link_et.config(text="Unlink Eye-Tracker")
                self.read = True
                self.gaze_focus = self.canvas_fig.create_oval(10-50, 10-50, 10+50, 10+50)
                self.thread_et = threading.Thread(target=self.readGaze)
                self.thread_et.start()
            else:
                messagebox.showinfo("ERROR", "No device connected !")
                self.eye_tracker = None
        else:
            self.read = False
            # self.thread.join()
            self.eye_tracker.stop()
            self.eye_tracker = None
            self.canvas_fig.delete(self.gaze_focus)
            self.link_et.config(text="Link Eye-Tracker")

    def enableScreenRecording(self):
        if self.screen_recording is None:
            self.screen_recording = ScreenRecording(self.info)
            self.record = True
            self.thread_sr = threading.Thread(target=self.launchScreenRecording)
            self.thread_sr.start()
            self.link_sr.config(text="Desable screen recording")
        else:
            self.record = False
            self.screen_recording.stop()
            self.thread_sr.join()
            self.screen_recording = None
            self.link_sr.config(text="Enable screen recording")

    def readGaze(self):
        while(self.read):
            time.sleep(0.02)
            try:
                gaze = self.eye_tracker.getGaze()
            except Exception:
                break

            x, y = self.screen_width*(gaze["Right"][0] + gaze["Left"][0])/2, self.screen_height*(gaze["Right"][1] + gaze["Left"][1])/2
            self.canvas_fig.coords(self.gaze_focus, x-50, y-50, x+50, y+50)
            
            # print((gaze["Right"][0] + gaze["Left"][0])/2, (gaze["Right"][1] + gaze["Left"][1])/2)

    def launchScreenRecording(self):
        self.screen_recording.record()
        self.screen_recording.createVideo()
from tkinter import Tk, Canvas, Button, Entry, StringVar, messagebox
from eye_tracker import EyeTracker
from copy import deepcopy
import threading
import time


class Display:
    def __init__(self):
        self.eye_tracker = None

        self.fenetre = Tk()

        self.screen_width = self.fenetre.winfo_screenwidth()
        self.screen_height = self.fenetre.winfo_screenheight()

        # print(self.screen_width)
        # print(self.screen_height)

        xFig, yFig = self.screen_width, self.screen_height
        self.canvas_fig = Canvas(self.fenetre, width=xFig, height=yFig, background='white')
        self.canvas_fig.pack()

        self.link_et = Button(self.fenetre, text="  Link Eye-Tracker ", command=self.linkET)
        self.link_et_w = self.canvas_fig.create_window(self.screen_width/2, self.screen_height/2, window=self.link_et)

        self.value = StringVar(self.fenetre)
        self.name = Entry(self.fenetre, textvariable=self.value, width=10)

        self.canvas_fig.bind("<Configure>", self.resize)
        self.canvas_fig.bind_all("<KeyPress>", self.keyboard)

        self.fenetre.mainloop()

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

    def keyboard(self, event):
        if event.keysym == "Return":
            self.screen_width = self.fenetre.winfo_screenwidth()
            self.screen_height = self.fenetre.winfo_screenheight()

            print(self.screen_width)
            print(self.screen_height)
    
    def linkET(self):
        if self.eye_tracker is None:
            self.eye_tracker = EyeTracker()
            if self.eye_tracker.started():
                self.link_et.config(text="Unlink Eye-Tracker")
                self.read = True
                self.gaze_focus = self.canvas_fig.create_oval(10-50, 10-50, 10+50, 10+50)
                self.thread = threading.Thread(target=self.readGaze)
                self.thread.start()
            else:
                self.eye_tracker = None
        else:
            self.read = False
            # self.thread.join()
            self.eye_tracker.stop()
            self.eye_tracker = None
            self.canvas_fig.delete(self.gaze_focus)
            self.link_et.config(text="  Link Eye-Tracker ")

    def readGaze(self):
        while(self.read):
            time.sleep(0.05)
            try:
                gaze = self.eye_tracker.getGaze()
            except Exception:
                break
            x, y = self.screen_width*(gaze["Right"][0] + gaze["Left"][0])/2, self.screen_height*(gaze["Right"][1] + gaze["Left"][1])/2
            self.canvas_fig.coords(self.gaze_focus, x-50, y-50, x+50, y+50)
            print((gaze["Right"][0] + gaze["Left"][0])/2, (gaze["Right"][1] + gaze["Left"][1])/2)
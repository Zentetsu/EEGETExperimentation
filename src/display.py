from tkinter import *
from screen_recording import ScreenRecording
from tkinter import filedialog, messagebox
from eye_tracker import EyeTracker
from PIL import ImageTk, Image
from copy import deepcopy
from pathlib import Path
import threading
import time
import glob


class Display:
    def __init__(self):
        self.next = False
        self.cur_exp = None
        self.path_obj = None
        self.eye_tracker = None
        self.screen_recording = None

        self.windows = Tk()

        self.screen_width = self.windows.winfo_screenwidth()
        self.screen_height = self.windows.winfo_screenheight()

        self.initMenuScreen()
        self.initExperienceScreen()

        self.canvas_fig.bind("<Configure>", self.resize)
        self.canvas_fig.bind_all("<KeyPress>", self.keyboard)

        self.windows.mainloop()

    def initMenuScreen(self):
        xFig, yFig = self.screen_width, self.screen_height
        self.canvas_fig = Canvas(self.windows, width=xFig, height=yFig, background='white')
        self.canvas_fig.pack()

        self.link_et = Button(self.windows, text="Link Eye-Tracker", command=self.linkET, width=25)
        self.link_sr = Button(self.windows, text="Enable screen recording", command=self.enableScreenRecording, width=25)
        self.link_pa = Button(self.windows, text="Select object folder", command=self.selectPath, width=25)
        self.link_se = Button(self.windows, text="Start experience", command=self.initExperience, width=25)
        self.link_et_w = self.canvas_fig.create_window(self.screen_width/2, self.screen_height/2-30, window=self.link_et)
        self.link_et_w = self.canvas_fig.create_window(self.screen_width/2, self.screen_height/2, window=self.link_sr)
        self.link_pa_w = self.canvas_fig.create_window(self.screen_width/2, self.screen_height/2+30, window=self.link_pa)
        self.link_se_w = self.canvas_fig.create_window(self.screen_width/2, self.screen_height/2+60, window=self.link_se)

    def initExperienceScreen(self):
        xFig, yFig = self.screen_width, self.screen_height
        self.canvas_test = Canvas(self.windows, width=xFig, height=yFig, background='white')

        self.link_se2 = Button(self.windows, text="Stop experience", command=self.stopExperience, width=15)
        self.link_se3 = Button(self.windows, text="Wait", command=self.initExperience, width=15)
        self.link_se2_w = self.canvas_test.create_window(self.screen_width/8, 30, window=self.link_se2)
        self.link_se3_w = self.canvas_test.create_window(7*self.screen_width/8, 30, window=self.link_se3)

        self.img_show = self.canvas_test.create_image(self.screen_width/2, self.screen_height/2, anchor=CENTER, image=None)

        self.img_inst = self.canvas_test.create_text(self.screen_width/2, 30, text="")

    def resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.screen_width
        hscale = float(event.height)/self.screen_height
        self.screen_width = event.width
        self.screen_height = event.height
        # resize the canvas 
        self.canvas_fig.config(width=self.screen_width, height=self.screen_height)
        self.canvas_test.config(width=self.screen_width, height=self.screen_height)
        # rescale all the objects tagged with the "all" tag
        self.canvas_fig.scale("all", 0, 0, wscale, hscale)
        self.canvas_test.scale("all", 0, 0, wscale, hscale)

        string_info = self.windows.winfo_geometry()
        string_info = string_info.split("+")
        self.info = string_info[0].split("x")
        self.info.extend(string_info[1:])
        self.info = [int(x) for x in self.info]

    def keyboard(self, event):
        if event.keysym == "Return":
            self.screen_width = self.windows.winfo_screenwidth()
            self.screen_height = self.windows.winfo_screenheight()
    
    def linkET(self):
        if self.eye_tracker is None:
            self.eye_tracker = EyeTracker()
            if self.eye_tracker.started():
                self.link_et.config(text="Unlink Eye-Tracker")
                self.read = True
                self.gaze_focus = self.canvas_fig.create_oval(10-50, 10-50, 10+50, 10+50)
                self.gaze_focus = self.canvas_test.create_oval(10-50, 10-50, 10+50, 10+50)
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
            self.canvas_test.delete(self.gaze_focus)
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
            
            self.canvas_fig.coords(self.gaze_focus, x-50, y-50-int(self.info[3]), x+50, y+50-int(self.info[3]))
            self.canvas_test.coords(self.gaze_focus, x-50, y-50-int(self.info[3]), x+50, y+50-int(self.info[3]))
            
            # print((gaze["Right"][0] + gaze["Left"][0])/2, (gaze["Right"][1] + gaze["Left"][1])/2)

    def launchScreenRecording(self):
        self.screen_recording.record()
        self.screen_recording.createVideo()

    def selectPath(self):
        self.path_obj = filedialog.askdirectory(parent=self.windows, initialdir= "/", title='Please select a directory')
        # self.path_obj = "../experiment"

        self.list_exp = [Path(i).stem for i in glob.glob(self.path_obj + "/*")]
        self.tot_exp = len([i for i in self.list_exp if "exp" in i])
        self.cur_exp = 0

    def initExperience(self):
        if self.path_obj is None:
            messagebox.showinfo("ERROR", "No folder selected !")
            return

        if self.cur_exp < self.tot_exp:
            if self.cur_exp == 0:
                self.canvas_fig.pack_forget()
                self.canvas_test.pack()

            self.startExperience(self.list_exp[self.cur_exp])

    def startExperience(self, path):
        list_temp = [Path(i).stem for i in glob.glob(self.path_obj + "/" + path + "/*")]
        
        self.list_img = None
        self.list_ins = None

        for i in list_temp:
            if i == "object":
                self.list_img = glob.glob(self.path_obj + "/" + path + "/" + i + "/*")
                self.list_img = sorted([Path(i).stem for i in self.list_img])
            elif i == "instruction":
                self.list_ins = glob.glob(self.path_obj + "/" + path + "/" + i + "/*")
                self.list_ins = sorted([Path(i).stem for i in self.list_ins])
            else:
                messagebox.showinfo("ERROR", "Unknown folder !")

                self.stopExperience()

        self.displayWaitScreen(self.path_obj + "/" + path)

    def displayWaitScreen(self, path):
        self.canvas_test.itemconfig(self.img_inst, text="")
        self.canvas_test.delete(self.img_show)
        self.focus = self.canvas_test.create_oval(self.screen_width/2-50, self.screen_height/2-50, self.screen_width/2+50, self.screen_height/2+50, fill="black")
        self.canvas_test.after(1000, self.displayImage, path)

    def displayImage(self, path):
        self.windows.update()
        self.canvas_test.delete(self.focus)

        if self.list_ins is not None:
            with open(path + "/instruction/" + self.list_ins[0] + ".txt", 'r') as file:
                data = file.read().replace('\n', '')
                self.canvas_test.itemconfig(self.img_inst, text=data)

        if self.list_img is not None:
            img_temp = Image.open(path + "/object/" + self.list_img[0] + ".jpg").resize((500, 500), Image.ANTIALIAS)
            self.img = ImageTk.PhotoImage(img_temp)

            self.img_show = self.canvas_test.create_image(self.screen_width/2, self.screen_height/2, anchor=CENTER, image=self.img)
            self.canvas_test.tag_lower(self.img_show)

        if len(self.list_img) > 1:
            if self.list_img is not None:
                self.list_img.pop(0)

            if self.list_ins is not None:
                self.list_ins.pop(0)

            self.canvas_test.after(500, self.displayImage, path)
        else:
            self.next = True
            self.cur_exp += 1
            self.link_se3.config(text="Continue")
        
    def stopExperience(self):
        self.canvas_fig.pack()
        self.canvas_test.pack_forget()
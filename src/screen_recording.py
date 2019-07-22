import time
import mss
import numpy
import skvideo.io


class ScreenRecording:
    def __init__(self, info):
        self.start = True
        self.nb_image = 0
        self.monitor = {'top': info[3], 'left': info[2], 'width': info[0], 'height': info[1]}

        print(self.monitor)
        self.outputdata = []

    def record(self):
        sct = mss.mss()

        while self.start:
            # last_time = time.time()

            self.outputdata.append(numpy.asarray(sct.grab(self.monitor)))

            # print("fps: {}".format(1 / (time.time() - last_time)))

    def stop(self):
        self.start = False

    def createVideo(self):
        self.outputdata = numpy.array(self.outputdata)

        writer = skvideo.io.FFmpegWriter("../record/record.mp4")

        for i in range(self.outputdata.shape[0]):
            writer.writeFrame(self.outputdata[i, :, :, :])
        writer.close()
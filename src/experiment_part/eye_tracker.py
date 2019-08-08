import tobii_research as tr


class EyeTracker:
    def __init__(self):
        self.start = False
        self.gaze = {"Left": [0, 0], "Right": [0, 0]}

        found_eyetrackers = tr.find_all_eyetrackers()

        if len(found_eyetrackers) > 0:
            print(found_eyetrackers)
            self.my_eyetracker = found_eyetrackers[0]
            self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary=True)
            self.start = True
        else:
            print("ERROR: No device connected")
            self.start = False
    
    def gaze_data_callback(self, gaze_data):
        # Print gaze points of left and right eye
        # print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
        #     gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
        #     gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))

        self.gaze["Left"] = gaze_data['left_gaze_point_on_display_area']
        self.gaze["Right"] = gaze_data['right_gaze_point_on_display_area']


    def stop(self):
        self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback)

    def started(self):
        return self.start

    def getGaze(self):
        return self.gaze
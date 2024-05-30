import cv2


class Tracker(object):
    def __init__(self, **argkw):
        """Need keyword: tid,method,img,roi,start."""
        self.TID = argkw.get("tid")
        self.Start = argkw.get("start")
        self.ROI = argkw.get("roi")
        self.Method = argkw.get("method")
        self.FlagEnable = True

        if self.Method == "KCF":
            func = cv2.TrackerKCF_create
        elif self.Method == "CSRT":
            func = cv2.TrackerCSRT_create
        elif self.Method == "MOSSE":
            func = cv2.legacy.TrackerMOSSE_create

        self.Tracker = func()
        self.init(argkw.get("img"), self.ROI)
        return

    def init(self, img, roi=None):
        if roi is None:
            roi = self.ROI
        self.Tracker.init(img, roi)
        return

    def track(self, image):
        if not self.FlagEnable:
            return False, None
        success, roi = self.Tracker.update(image)
        if success:
            self.ROI = [int(v) for v in roi]
        return success, roi

    pass


class VideoControl:
    def __init__(self, path: str) -> None:
        self.Path = path
        self.Cap = cv2.VideoCapture(path)
        self.Count = int(self.Cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.Fps = int(self.Cap.get(cv2.CAP_PROP_FPS))
        self.Width = int(self.Cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.Height = int(self.Cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.Frame = None
        self.Index = 0
        self.Time = self.Count / self.Fps
        self.Now = self.Index / self.Fps
        self.DictTracker = dict()
        return

    def readFrame(self, index=-1):
        if index == -1 or self.Frame is None:
            ret, self.Frame = self.Cap.read()
            # self.Index += 1
            pass
        else:
            self.Cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            self.Index = index
            ret, self.Frame = self.Cap.read()
        self.Now = self.Index / self.Fps
        return self.Frame

    pass

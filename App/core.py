import json, os, sys
import shutil
import PyQt6.QtWidgets as qtw


class TrackLabel(object):
    def __init__(self) -> None:
        from App import VideoControl

        self.Video: VideoControl = None
        self.VideoName = ""
        self.VideoFolder = ""
        self.CW = 720
        self.CH = 640
        self.Speed = 1
        self.Option = dict()
        self.Status = "Idle"
        self.IdxLabel = -1
        self.IdxTrack = -1
        self.DictTracker = dict()
        self.FlagAutoSave = False
        self.FlagVerify = False
        self.ScaledWidth = 0
        self.ScaledHeight = 0
        self.FrameWidth = 0
        self.FrameHeight = 0
        self.FlagWidth = True
        return

    def isOpened(self):
        return self.Video is not None

    def getVideoSize(self):
        return self.Video.Width, self.Video.Height

    def initApp(self):
        from App import TLWindow

        self.App = qtw.QApplication(sys.argv)
        self.Window = TLWindow()

        self.Window.init()

        return

    def runApp(self):
        self.initApp()
        exit(self.App.exec())
        return

    def loadVideo(self, path: str):
        from App import VideoControl

        self.Video = VideoControl(path)
        pos = path.rfind("/")
        self.VideoName = path[pos + 1 : path.rfind(".")]
        self.VideoFolder = path[: path.rfind(".")]

        self.updateWH()

        if not os.path.exists(self.VideoFolder):
            os.mkdir(self.VideoFolder)
            os.mkdir(self.VideoFolder + "/labels")
            os.mkdir(self.VideoFolder + "/images")
            shutil.copy("./Conf/vtl.json", self.VideoFolder + "/vtl.json")

        with open(self.VideoFolder + "/vtl.json", "r") as f:
            self.Option = json.loads(f.read())
        self.Window.loadLabels(self.Option)
        return True

    def readImage(self, index=-1, skip=False):
        from App import Tracker

        if skip or index == -1:
            return self.Video.readFrame(index)
        if index > self.Video.Index:
            r = range(self.Video.Index + 1, index + 1)
        else:
            r = range(index, self.Video.Index)
            r = reversed(r)

        for i in r:
            img = self.Video.readFrame(i)
            for tid, tracker in self.DictTracker.items():
                tracker: Tracker
                tracker.track(img)
        return img

    def editLabel(self, label, name):
        for i in range(len(self.Option["ClassLabel"])):
            if label == self.Option["ClassLabel"][i]:
                self.Option["ClassName"][i] = name
                break
        self.saveOption()
        return

    def addLabel(self):
        label = max(self.Option["ClassLabel"]) + 1
        self.Option["ClassLabel"].append(label)
        self.Option["ClassName"].append("Label")
        self.saveOption()
        return

    def delLabel(self, label):
        for i in range(len(self.Option["ClassLabel"])):
            if label == self.Option["ClassLabel"][i]:
                self.Option["ClassLabel"].pop(i)
                self.Option["ClassName"].pop(i)
                break
        self.saveOption()
        return

    def saveOption(self):
        with open(self.VideoFolder + "/vtl.json", "w") as f:

            s = json.dumps(self.Option, indent=4)
            f.write(s)
        return

    def createTracker(self, **argkw):
        """Need keyword: tid,method,roi."""
        from App import Tracker

        argkw.update({"start": self.Video.Index, "img": self.Video.Frame})
        tracker = Tracker(**argkw)
        self.DictTracker[argkw.get("tid")] = tracker
        return tracker

    def enableTracker(self, tid, flag):
        self.DictTracker[tid].FlagEnable = flag
        return

    def cvtoFramePos(self, x, y):
        sw = self.ScaledWidth
        sh = self.ScaledHeight
        fw = self.FrameWidth
        fh = self.FrameWidth
        pw, ph = self.getVideoSize()
        if self.FlagWidth:
            k = ph / sh
            b = k * (sh - fh) / 2
            px = int(x * pw / sw)
            py = int(k * y + b)
            if py < 0 or py > ph:
                px = py = -1
        else:
            k = pw / sw
            b = k * (sw - fw) / 2
            py = int(y * ph / sh)
            px = int(k * x + b)
            if px < 0 or px > pw:
                px = py = -1
        return px, py

    def cvtoImagePos(self, x, y):

        return

    def updateWH(self):
        pw = self.Video.Width
        ph = self.Video.Height
        fw = self.Window.Frame.width()
        fh = self.Window.Frame.height()
        self.FrameWidth = fw
        self.FrameHeight = fh
        self.FlagWidth = pw > ph
        if self.FlagWidth:
            self.ScaledWidth = fw
            self.ScaledHeight = int(ph * fw / pw)
        else:
            self.ScaledWidth = int(pw * fh / ph)
            self.ScaledHeight = fh
        return

    def cvtoFrameRect(self, x, y, w, h, f=False):
        vw = self.Video.Width
        vh = self.Video.Height
        sw = self.ScaledWidth
        sh = self.ScaledHeight
        if f:
            fx = float(x)
            fy = float(y)
            fw = float(w)
            fh = float(h)
            if VTLC.FlagWidth:
                x = (fx - fw / 2) * sw
                y = (fy - fh / 2) * sh + (self.FrameHeight - sh) / 2
            else:
                x = (fx - fw / 2) * sw + (self.FrameWidth - sw) / 2
                y = (fy - fh / 2) * sh
            w = fw * sw
            h = fh * sh
        else:
            if sw > sh:
                x = x / vw * sw
                y = y / vh * sh + (self.FrameHeight - sh) / 2
            else:
                x = x / vw * sw + (self.FrameWidth - sw) / 2
                y = y / vh * sh
            w = w / vw * sw
            h = h / vh * sh
        return int(x), int(y), int(w), int(h)

    def cvtoImageRect(self, x, y, w, h):
        vw = self.Video.Width
        vh = self.Video.Height
        sw = self.ScaledWidth
        sh = self.ScaledHeight
        if sw > sh:
            x = x * vw / sw
            y = (y - (self.FrameHeight - sh) / 2) * vh / sh
        else:
            x = (x - (self.FrameWidth - sw) / 2) * vw / sw
            y = y * vh / sh
        w = w * vw / sw
        h = h * vh / sh
        return int(x), int(y), int(w), int(h)

    pass


VTLC = TrackLabel()


def getCore():
    global VTLC
    return VTLC

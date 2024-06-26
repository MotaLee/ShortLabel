import json
import os
import sys
import random
import shutil
import PyQt6.QtWidgets as qtw
import cv2
import numpy as np


class CircleVariable(object):
    def __init__(self, max, min=0):
        self.Value = min
        self.Min = min
        self.Max = max
        return

    def next(self):
        if self.Value + 1 > self.Max:
            self.Value = self.Min
        else:
            self.Value += 1
        return self.Value

    pass


class ShortLabelCore(object):
    def __init__(self) -> None:
        # from . import VideoControl

        print(sys.argv)

        self.Video = None
        self.VideoName = ""
        self.VideoFolder = ""
        self.FlagVerify = False

        self.TrackerMethod = "CSRT"

        self.CW = 720
        self.CH = 640
        self.Speed = 1
        self.Status = "Idle"

        self.IdxLabel = -1
        self.IdxTrack = -1
        self.Data = dict()
        self.DictTracker = dict()
        self.DictColor: dict[str, str] = dict()

        self.FlagWidth = True
        self.FlagSetMode = False

        self.ScaledWidth = 0
        self.ScaledHeight = 0
        self.FrameWidth = 0
        self.FrameHeight = 0

        self.SetImage = None
        self.IndexSetImage = -1

        self.ListImage: list[int] = list()

        return

    def initAI(self, model, method):
        from . import AIControl

        self.AI = AIControl()
        res = self.AI.init(model, method)
        return res

    def getAIStatus(self):
        if "AI" in self.__dict__:
            if self.AI.Process is None:
                ret = "NotLoad"
            elif self.AI.Process.poll() is None:
                if self.AI.isIdle():
                    ret = "Idle"
                else:
                    ret = "Busy"
            else:
                ret = "Failed"
        else:
            ret = "NotLoad"
        return ret

    def isOpened(self):
        return self.Video is not None

    def getVideoSize(self, index=-1):
        if index == -1:
            index = self.Video.Index
        if self.FlagSetMode and index in self.ListImage:
            if self.IndexSetImage != index:
                path = self.getPath(index)
                self.IndexSetImage = index
                self.SetImage = cv2.imread(path)
            pw = self.SetImage.shape[1]
            ph = self.SetImage.shape[0]
        else:
            pw = self.Video.Width
            ph = self.Video.Height
            if self.Data["Rotate"] not in {0, 2}:
                tmp = int(ph)
                ph = int(pw)
                pw = int(tmp)

        return pw, ph

    def initApp(self):
        from App import SLWindow

        self.App = qtw.QApplication(sys.argv)
        self.Shell = SLWindow()
        self.Shell.init()

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

        if not os.path.exists(self.VideoFolder):
            os.mkdir(self.VideoFolder)
            os.mkdir(self.VideoFolder + "/labels")
            os.mkdir(self.VideoFolder + "/images")
            shutil.copy("./Conf/data.json", self.VideoFolder + "/data.json")

        self.ListImage.clear()
        for p in os.listdir(self.VideoFolder + "/images"):
            self.ListImage.append(int(p[: p.find(".")]))

        with open("./Conf/option.json", "r") as f:
            self.Option = json.loads(f.read())
        with open(self.VideoFolder + "/data.json", "r") as f:
            self.Data = json.loads(f.read())
        # self.updateWH()
        return True

    def readImage(self, index=-1, skip=False):
        from App import Tracker

        self.updateWH(index)

        if index == -1:
            index = self.Video.Index

        if self.FlagSetMode and index in self.ListImage:
            img = np.copy(self.SetImage)
            self.Video.Index = index
        else:
            if skip or index == self.Video.Index:
                img = self.Video.readFrame(index)
            else:
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

            if self.Data["Rotate"] == 1:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            elif self.Data["Rotate"] == 2:
                img = cv2.rotate(img, cv2.ROTATE_180)
            elif self.Data["Rotate"] == 3:
                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

            if self.Data["FlagClip"]:
                x, y, w, h = self.Data["Clip"]
                img2 = (img * 0.5).astype(np.uint8)
                img2[y : y + h, x : x + w] = img[y : y + h, x : x + w]
                img = img2

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.ScaledWidth, self.ScaledHeight))

        if self.FlagWidth:
            h = (self.FrameHeight - self.ScaledHeight) // 2
            img = cv2.copyMakeBorder(
                img, h, h, 0, 0, cv2.BORDER_CONSTANT, value=[128, 128, 128]
            )
        else:
            w = (self.FrameWidth - self.ScaledWidth) // 2
            img = cv2.copyMakeBorder(
                img, 0, 0, w, w, cv2.BORDER_CONSTANT, value=[128, 128, 128]
            )

        return img

    def saveImage(self, lines=None):
        if self.Video.Index not in self.ListImage:
            self.ListImage.append(self.Video.Index)
            self.ListImage.sort()

        img_name = self.getPath()
        lbl_name = self.getPath(img=False)
        if not self.FlagSetMode:
            if self.Data["Rotate"] == 1:
                img = cv2.rotate(self.Video.Frame, cv2.ROTATE_90_CLOCKWISE)
            elif self.Data["Rotate"] == 2:
                img = cv2.rotate(self.Video.Frame, cv2.ROTATE_180)
            elif self.Data["Rotate"] == 3:
                img = cv2.rotate(self.Video.Frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            else:
                img = self.Video.Frame
            if self.Data["FlagClip"]:
                x, y, w, h = self.Data["Clip"]
                img = img[y : y + h, x : x + w]
            cv2.imwrite(img_name, img)

        if lines is not None:
            with open(lbl_name, "w") as fd:
                fd.writelines(lines)
        return img_name

    def removeImage(self, index=-1):
        if index == -1:
            index = self.Video.Index

        if index in self.ListImage:
            self.ListImage.remove(index)

        txt = self.getPath(index, img=False)
        img = self.getPath(index)
        if os.path.exists(txt):
            os.remove(txt)
        if os.path.exists(img):
            os.remove(img)
        if index in self.Data["Verified"]:
            self.Data["Verified"].remove(index)
        return

    def findNextImage(self, index, next=True):
        i = -1
        if next:
            for i in self.ListImage:
                if i > index:
                    break
        else:
            for i in reversed(self.ListImage):
                if i < index:
                    break
        return i

    def editLabel(self, index, label):
        self.Data["Class"][str(index)] = label
        self.saveOption()
        return

    def addLabel(self):
        l = [int(k) for k in self.Data["Class"].keys()]
        index = max(l) + 1
        self.Data["Class"][str(index)] = "Label"
        self.saveOption()
        return

    def delLabel(self, index):
        del self.Data["Class"][str(index)]
        self.saveOption()
        return

    def getLabel(self, index=-1):
        return self.Data["Class"][str(index)]

    def saveOption(self):
        with open(self.VideoFolder + "/data.json", "w") as f:
            s = json.dumps(self.Data, indent=4)
            f.write(s)
        with open("./Conf/option.json", "w") as f:
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

    def cvtoImagePos(self, x, y):
        """将视窗坐标转换为图像坐标。"""
        # x -= 5
        # y -= 5
        sw = self.ScaledWidth
        sh = self.ScaledHeight
        fw = self.FrameWidth
        fh = self.FrameHeight
        pw, ph = self.getVideoSize()
        if self.FlagWidth:
            px = int(x * pw / sw)
            py = int(ph / sh * (y - (fh - sh) / 2))
            if py < 0 or py > ph:
                px = py = -1
        else:
            py = int(y * ph / sh)
            px = int(pw / sw * (x - (fw - sw) / 2))
            if px < 0 or px > pw:
                px = py = -1
        return px, py

    def updateWH(self, index):
        pw, ph = self.getVideoSize(index)
        fw = self.Shell.Frame.Image.width()
        fh = self.Shell.Frame.Image.height()
        self.FrameWidth = fw
        self.FrameHeight = fh
        self.FlagWidth = pw / ph > fw / fh
        if self.FlagWidth:
            self.ScaledWidth = fw
            self.ScaledHeight = int(ph * fw / pw)
        else:
            self.ScaledWidth = int(pw * fh / ph)
            self.ScaledHeight = fh
        return

    def cvtoFrameRect(self, x, y, w, h, f=False):
        """将图像框坐标转换为视窗坐标。"""
        vw, vh = self.getVideoSize()
        sw = self.ScaledWidth
        sh = self.ScaledHeight
        if f:
            fx = float(x)
            fy = float(y)
            fw = float(w)
            fh = float(h)
            if self.Data["FlagClip"] and not self.FlagSetMode:
                x = (fx - fw / 2) * self.Data["Clip"][2] + self.Data["Clip"][0]
                y = (fy - fh / 2) * self.Data["Clip"][3] + self.Data["Clip"][1]
                w = fw * self.Data["Clip"][2]
                h = fh * self.Data["Clip"][3]
                x, y, w, h = self.cvtoFrameRect(x, y, w, h)
            else:
                if self.FlagWidth:
                    x = (fx - fw / 2) * sw
                    y = (fy - fh / 2) * sh + (self.FrameHeight - sh) / 2
                else:
                    x = (fx - fw / 2) * sw + (self.FrameWidth - sw) / 2
                    y = (fy - fh / 2) * sh
                w = fw * sw
                h = fh * sh
        else:
            if self.FlagWidth:
                x = x / vw * sw
                y = y / vh * sh + (self.FrameHeight - sh) / 2
            else:
                x = x / vw * sw + (self.FrameWidth - sw) / 2
                y = y / vh * sh
            w = w / vw * sw
            h = h / vh * sh
        return int(x), int(y), int(w), int(h)

    def cvtoImageRect(self, x, y, w, h):
        # x -= 5
        # y -= 5
        vw, vh = self.getVideoSize()

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

    def getColor(self, index):
        random.randint(0, 254)
        h = 255 // len(self.Data["Class"]) * len(self.DictColor) % 255
        if index not in self.DictColor:
            color = f"hsv({h},200,200)"
            self.DictColor[index] = color
        return self.DictColor[index]

    def getClass(self, i):
        return self.Data["Class"][str(i)]

    def getPath(self, frame=-1, img=True):
        if frame == -1:
            frame = self.Video.Index
        i = str(frame).rjust(6, "0")
        if img:
            ret = f"{self.VideoFolder}/images/{i}.jpg"
        else:
            ret = f"{self.VideoFolder}/labels/{i}.txt"
        return ret

    pass


SLC = ShortLabelCore()


def getCore():
    global SLC
    return SLC


def getShell():
    global SLC
    return SLC.Shell

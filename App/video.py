import json
import os
import subprocess as sp
import threading
import time
import _winapi
import msvcrt

import requests

import cv2

from . import getCore

SLC = getCore()


class Tracker(object):
    def __init__(self, **argkw):
        """Need keyword: tid,method,img,roi,start."""
        self.TID = argkw.get("tid")
        self.Start = argkw.get("start")
        self.ROI = argkw.get("roi")
        self.Method = argkw.get("method")
        self.FlagEnable = True
        self.FlagSuccess = False

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
        self.FlagSuccess = True
        return

    def track(self, image):
        if not self.FlagEnable:
            return False, None
        success, roi = self.Tracker.update(image)
        self.FlagSuccess = success
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


class AIControl:
    def __init__(self) -> None:
        self.Process: sp.Popen = None
        self.HandleOut = -1
        self.HandleIn = -1
        self.FlagBusy = False
        return

    def init(self, model, method):
        self.ModelPath = model
        self.Method = method
        try:
            if self.Method == "Yolov5":
                cmd = [
                    "python",
                    "VS.py",
                    "--weights",
                    self.ModelPath,
                ]
                cwd = os.getcwd() + "\\..\\ViServer"
                self.Process = sp.Popen(cmd, shell=True, cwd=cwd)
                # self.HandleIn = msvcrt.get_osfhandle(self.Process.stdin.fileno())
                # self.HandleOut = msvcrt.get_osfhandle(self.Process.stdout.fileno())
        except BaseException as e:
            print(e)
            return False
        return True

    def deinit(self):
        if self.Process is not None:
            self.Process.kill()
        return

    def detect(self, img, recall=None):
        self.Recall = recall
        self.Source = img

        Thread = threading.Thread(target=self.threadDetect)
        Thread.start()
        return

    def writeInDict(self, d):
        self.Process.stdin.write((json.dumps(d) + "\r\n").encode())
        self.Process.stdin.flush()
        return

    def getOutCount(self):
        count, read = _winapi.PeekNamedPipe(self.HandleOut, 0)
        return count

    def readOut(self):
        count, read = _winapi.PeekNamedPipe(self.HandleOut, 0)
        if count > 0:
            data, errcode = _winapi.ReadFile(self.HandleOut, count)
            ret = data.decode()
            # t = self.Process.stdout.read()
        else:
            ret = None
        return ret

    def isIdle(self):
        try:
            res = requests.post(
                "http://127.0.0.1:5005/Command", data={"Command": "isIdle"}
            )
            jret = res.json()
            if jret["Return"] == 0:
                return True
        except BaseException as e:
            print(e)
            return False
        return False

    def threadDetect(self):
        if self.FlagBusy:
            return
        else:
            self.FlagBusy = True

        try:
            res = requests.post(
                "http://127.0.0.1:5005/Command",
                data={"Command": "detect", "Source": self.Source},
            )

            j = res.json()
            if self.Recall is not None:
                self.Recall(j)
        except BaseException as e:
            print(e)

        self.FlagBusy = False

        return

    pass

import os
import threading
import time

import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from PyQt6.QtCore import Qt

from . import getCore, LabelItem, TrackItem, LabelBox, CircleVariable
from . import MainMenu, SideFrame

SLC = getCore()


class ClipHandle(qtw.QLabel):
    def __init__(self, parent, type="Corner"):
        super().__init__(parent)

        self.FlagPress = False
        self.Type = type

        self.setStyleSheet("background-color:#3b0;border:none;")
        self.setMouseTracking(True)
        if self.Type == "Corner":
            self.setFixedSize(10, 10)
        else:
            self.setFixedSize(20, 10)

        self.hide()
        return

    def enterEvent(self, ev: qtg.QMouseEvent):
        self.setStyleSheet("background-color:#5d0;border:none;")
        return

    def leaveEvent(self, ev: qtg.QMouseEvent):
        self.setStyleSheet("background-color:#3b0;border:none;")
        return

    def mouseMoveEvent(self, ev: qtg.QMouseEvent):
        SLS = SLC.Shell
        if self.FlagPress:
            pos = ev.pos()
            x = self.pos().x() - self.Pos.x() + pos.x()
            y = self.pos().y() - self.Pos.y() + pos.y()
            self.move(x, y)

            h1 = SLC.Shell.Frame.HandClip1
            h2 = SLC.Shell.Frame.HandClip2
            hm = SLC.Shell.Frame.HandClipM
            x1 = h1.geometry().x()
            y1 = h1.geometry().y()
            x2 = h2.geometry().x()
            y2 = h2.geometry().y()
            xm = hm.geometry().x()
            ym = hm.geometry().y()
            if self.Type != "Corner":
                h1.move(xm + 10 - abs(x1 - x2) // 2, ym + 10)
                h2.move(xm + 10 + abs(x1 - x2) // 2, ym + 10 + abs(y1 - y2))
            else:
                hm.move((x1 + x2 + 10) // 2 - 10, min(y1, y2) - 10)

            SLC.Shell.Frame.BoxTodo.setGeometry(
                min(x1, x2),
                min(y1, y2),
                abs(x1 - x2) + 10,
                abs(y1 - y2) + 10,
            )
            SLC.Shell.Frame.BoxTodo.show()
        return

    def mousePressEvent(self, ev: qtg.QMouseEvent):
        self.FlagPress = True
        self.Pos = ev.pos()
        return

    def mouseReleaseEvent(self, ev: qtg.QMouseEvent):
        self.FlagPress = False

        SLC.Shell.Frame.BoxTodo.hide()
        h1 = SLC.Shell.Frame.HandClip1
        h2 = SLC.Shell.Frame.HandClip2
        x1 = h1.pos().x()
        y1 = h1.pos().y()
        x2 = h2.pos().x() + 10
        y2 = h2.pos().y() + 10
        w = abs(x1 - x2)
        h = abs(y1 - y2)
        rect = SLC.cvtoImageRect(min(x1, x2), min(y1, y2), w, h)
        if self.Type == "Corner":
            SLC.Data["Clip"] = [*rect]
        else:
            w = int(SLC.Shell.Side.InputWidth.text())
            h = int(SLC.Shell.Side.InputHeight.text())
            SLC.Data["Clip"] = [rect[0], rect[1], w, h]
        SLC.Shell.showImage()
        SLC.Shell.changeBack("Unsaved")
        return

    pass


class ImageFrame(qtw.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("FrameImage")
        self.setStyleSheet("#FrameImage{border:5px solid #000;}")
        self.setToolTipDuration(1000)

        self.StartX = 0
        self.StartY = 0
        self.Image = qtw.QLabel(self)
        self.Image.setMouseTracking(True)
        self.Image.mouseMoveEvent = self.mouseMoveImage
        self.Image.mouseReleaseEvent = self.mouseReleaseImage

        self.BoxTodo = qtw.QLabel(self.Image)
        self.BoxTodo.setMouseTracking(True)
        self.BoxTodo.hide()

        self.HandClip1 = ClipHandle(self.Image)
        self.HandClip2 = ClipHandle(self.Image)
        self.HandClipM = ClipHandle(self.Image, type="Move")

        self.setTodoBox()
        return

    def resizeEvent(self, a0: qtg.QResizeEvent):
        self.Image.setGeometry(5, 5, self.width() - 10, self.height() - 10)
        return super().resizeEvent(a0)

    def mouseMoveImage(self, ev: qtg.QMouseEvent):
        if not SLC.isOpened():
            return

        p = ev.pos()
        x = p.x()
        y = p.y()
        px, py = SLC.cvtoImagePos(x, y)
        SLC.Shell.LabelInfo.setText(f"({px},{py})/(0,0,0)")
        if SLC.Status == "StartPoint":
            index = SLC.Shell.getCrtLabelIndex()
            self.setToolTip(f"{index}: {SLC.getLabel(index)}")
        elif SLC.Status in {"EndPoint", "EndTrack"}:
            self.BoxTodo.setGeometry(
                min(x, self.StartX),
                min(y, self.StartY),
                abs(self.StartX - x),
                abs(self.StartY - y),
            )
        elif SLC.Status == "StartTrack":
            index = SLC.Shell.getCrtLabelIndex()
            self.setToolTip(
                f"{index}: {SLC.getLabel(index)}\nMethod: {SLC.TrackerMethod}"
            )
        return super().mouseMoveEvent(ev)

    def leaveEvent(self, a0: qtc.QEvent):
        SLC.Shell.LabelInfo.setText("(-1,-1)/(0,0,0)")
        return super().leaveEvent(a0)

    def mouseReleaseImage(self, ev: qtg.QMouseEvent):
        if SLC.Status == "StartPoint":
            SLC.Status = "EndPoint"
            self.StartX = ev.pos().x()
            self.StartY = ev.pos().y()
            self.setTodoBox()
            self.BoxTodo.setGeometry(self.StartX, self.StartY, 0, 0)
            self.BoxTodo.show()
        elif SLC.Status == "EndPoint":
            mx = ev.pos().x()
            my = ev.pos().y()
            x = min(mx, self.StartX)
            y = min(my, self.StartY)
            w = abs(mx - self.StartX)
            h = abs(my - self.StartY)
            index = SLC.Shell.getCrtLabelIndex()
            color = SLC.getColor(index)
            SLC.Shell.addBox(x, y, w, h, index, color)
        elif SLC.Status == "StartTrack":
            SLC.Status = "EndTrack"
            self.StartX = ev.pos().x()
            self.StartY = ev.pos().y()
            self.setTodoBox("dashed")
            self.BoxTodo.setGeometry(self.StartX, self.StartY, 0, 0)
            self.BoxTodo.show()
        elif SLC.Status == "EndTrack":
            self.setToolTip(None)
            self.setTodoBox()
            self.BoxTodo.hide()
            x = ev.pos().x()
            y = ev.pos().y()
            index = SLC.Shell.getCrtLabelIndex()
            color = SLC.getColor(index)

            bid = -1
            for box in SLC.Shell.ListTrack:
                if not box.FlagUsed:
                    box.useBox(
                        min(x, self.StartX),
                        min(y, self.StartY),
                        abs(x - self.StartX),
                        abs(y - self.StartY),
                        color,
                        index,
                    )
                    bid = box.BID
                    break

            # rect = [
            #     box.geometry().x(),
            #     box.geometry().y(),
            #     box.geometry().width(),
            #     box.geometry().height(),
            # ]

            rect = SLC.cvtoImageRect(*box.getRect())
            SLC.Shell.Side.addTrackItem(bid, index, rect)
            SLC.Shell.onCancel()
        return

    def setPixmap(self, pix):
        self.Image.setPixmap(pix)
        return

    def setTodoBox(self, style="solid"):
        if style == "solid":
            stl = r"QLabel{border:2px solid red;background-color:rgba(0,0,0,0)}"
        elif style == "dashed":
            stl = r"QLabel{border:2px dashed red;background-color:rgba(0,0,0,0)}"
        self.BoxTodo.setStyleSheet(stl)
        return

    pass


class SLWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__(None)

        self.FlagPlay = False
        self.FlagDeal = False

        self.CircleDisp = CircleVariable(3)

        self.ItemLabel = list()
        self.ItemTracker = dict()
        self.ListBox: list[LabelBox]
        self.ListTrack: list[LabelBox]
        self.Speed = 1
        self.ColorBorder = "#555"

        return

    def closeEvent(self, e):
        SLC.AI.deinit()
        return super().closeEvent(e)

    def switchStatus(self, status):
        if status == "StartPoint":
            self.hideAllBox()
            self.Frame.setCursor(Qt.CursorShape.CrossCursor)
        elif status == "StartTrack":
            self.Frame.setCursor(Qt.CursorShape.CrossCursor)
            self.hideAllBox()
        elif status == "Idle":
            SLC.Status = "Idle"
            self.Frame.BoxTodo.hide()
            self.Frame.setCursor(Qt.CursorShape.ArrowCursor)
            self.onDisp(False)
        SLC.Status = status
        return

    def resizeEvent(self, a0):
        w = self.width()
        h = self.height()

        self.Frame.setMinimumSize(int(0.75 * w) - 15, int(0.8 * h))
        self.Side.setMinimumWidth(int(0.25 * w) - 15)
        self.Widget.resize(self.width(), self.height())
        return super().resizeEvent(a0)

    def init(self):
        self.Widget = qtw.QWidget(self)
        self.Widget.resize(SLC.CW, SLC.CH)

        self.Menu = MainMenu(self.Widget)

        self.VidBar = qtw.QSlider(Qt.Orientation.Horizontal, self.Widget)

        self.InputFrame = qtw.QLineEdit("0", self.Widget)
        self.InputFrame.setMaximumSize(50, 20)
        self.InputFrame.setValidator(qtg.QIntValidator())
        self.LabelFrame = qtw.QLabel("/1", self.Widget)
        self.BtnPlay = qtw.QPushButton("▶", self.Widget)
        self.LabelTime = qtw.QLabel("00:00:00/00:59:59", self.Widget)
        self.LabelFps = qtw.QLabel("25fps", self.Widget)
        self.LabelInfo = qtw.QLabel("(-1,-1)/(0,0,0)", self.Widget)
        self.LabelInfo.setMinimumWidth(100)
        self.TxtNext = qtw.QLabel("下一保存帧：0", self.Widget)
        self.TxtSkip = qtw.QLabel("跳帧：", self.Widget)
        self.TxtSkip.setMaximumWidth(50)
        self.InputSpeed = qtw.QLineEdit("1", self.Widget)
        self.InputSpeed.setValidator(qtg.QIntValidator())
        self.InputSpeed.setMaximumWidth(50)

        self.Frame = ImageFrame(self.Widget)

        self.Side = SideFrame(self.Widget)

        self.ListBox = [LabelBox(self.Frame.Image, i) for i in range(32)]
        self.ListTrack = [LabelBox(self.Frame.Image, i, "Track") for i in range(8)]

        layout_v1 = qtw.QVBoxLayout()
        layout_h21 = qtw.QHBoxLayout()
        layout_h22 = qtw.QHBoxLayout()

        self.Widget.setLayout(layout_v1)
        layout_v1.setContentsMargins(10, 0, 10, 0)
        layout_v1.addWidget(self.Menu)
        layout_v1.addLayout(layout_h21)
        layout_h21.addWidget(self.InputFrame)
        layout_h21.addWidget(self.LabelFrame)
        layout_h21.addWidget(self.BtnPlay)
        layout_h21.addWidget(self.LabelTime)
        layout_h21.addWidget(self.LabelFps)
        layout_h21.addWidget(self.LabelInfo)
        layout_h21.addWidget(self.TxtNext)
        layout_h21.addWidget(self.TxtSkip)
        layout_h21.addWidget(self.InputSpeed)
        layout_h21.setSpacing(10)
        layout_v1.addWidget(self.VidBar)
        layout_v1.addLayout(layout_h22)
        layout_h22.addWidget(self.Frame)
        layout_h22.addWidget(self.Side)

        self.VidBar.sliderMoved.connect(self.onSilderGoto)
        self.BtnPlay.clicked.connect(self.onPlay)
        self.InputSpeed.textChanged.connect(self.onEditSpeed)

        self.resize(SLC.CW, SLC.CH)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setWindowTitle("ShortLabel")
        self.show()
        return

    def onDisp(self, toggle=True):
        if toggle:
            v = self.CircleDisp.next()
        else:
            v = self.CircleDisp.Value

        for box in self.ListBox:
            if box.FlagUsed:
                if v in {0, 1}:
                    box.select(False)
                    box.show()
                else:
                    box.hide()
            else:
                box.hide()
        for box in self.ListTrack:
            if box.FlagUsed and SLC.DictTracker[box.BID].FlagEnable:
                if v in {0, 2}:
                    box.select(False)
                    box.show()
                else:
                    box.hide()
            else:
                box.hide()
        return

    def onEditSpeed(self):
        t = self.InputSpeed.text()
        if t != "":
            s = int(t)
            self.Speed = s
        return

    def showImage(self, vi=-1, skip=False):
        from App import cvtSec

        img = SLC.readImage(vi, skip)

        if not SLC.Data["FlagClip"] or (
            SLC.FlagSetMode and SLC.Video.Index in SLC.ListImage
        ):
            self.setClip()
        else:
            self.setClip(SLC.Data["Clip"])

        # pyqt5转换成自己能放的图片格式
        _image = qtg.QImage(
            img[:],
            img.shape[1],
            img.shape[0],
            img.shape[1] * 3,
            qtg.QImage.Format.Format_RGB888,
        )
        pix = qtg.QPixmap(_image)
        self.Frame.setPixmap(pix)

        if SLC.Video.Index in SLC.ListImage:
            cimg = qtg.QImage(SLC.getPath())
            cpix = qtg.QPixmap(cimg).scaled(
                self.Side.ImgClip.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding
            )
            self.Side.ImgClip.setPixmap(cpix)

        self.InputFrame.setText(str(SLC.Video.Index))
        self.LabelFrame.setText(f"/{SLC.Video.Count}")
        self.LabelFps.setText(f"{SLC.Video.Fps}fps")
        self.LabelTime.setText(cvtSec(SLC.Video.Now) + "/" + cvtSec(SLC.Video.Time))

        self.VidBar.setValue(SLC.Video.Index)

        self.clearBox()

        file = SLC.getPath(img=False)
        if os.path.exists(file) and not self.FlagPlay:
            if SLC.Video.Index in SLC.Data["Verified"]:
                self.changeBack("Verified")
            else:
                self.changeBack("Saved")
            with open(file, "r") as fd:
                lines = fd.readlines()
            for line in lines:
                label, fx, fy, fw, fh = line.split(" ")
                label = int(label)
                c = SLC.getColor(label)
                if c is None:
                    continue

                x, y, w, h = SLC.cvtoFrameRect(fx, fy, fw, fh, True)

                for box in self.ListBox:
                    if not box.FlagUsed:
                        box.useBox(x, y, w, h, c, label)
                        break
        else:
            self.changeBack("None")

        for tid, tracker in SLC.DictTracker.items():
            box: LabelBox = self.ListTrack[tid]
            if tracker.FlagEnable and box.FlagUsed:
                box.useBox(*SLC.cvtoFrameRect(*tracker.ROI))

        self.Side.loadBox()
        return

    def onNext(self):
        if self.FlagDeal:
            return
        self.FlagDeal = True

        if SLC.Option["FlagAutoSave"]:
            if len(self.Side.QListBox.items(None)) > 0:
                self.onSave()

        i = SLC.Video.Index
        if SLC.FlagVerify:
            i = SLC.findNextImage(i)
            if i != -1:
                self.showImage(i, True)
        else:
            i = i + self.Speed
            if i <= SLC.Video.Count - 1:
                self.showImage(i)

        nexti = SLC.findNextImage(i)
        if nexti != -1:
            self.TxtNext.setText(f"下一保存帧：{nexti}")

        self.FlagDeal = False
        return

    def onPrev(self):
        if self.FlagDeal:
            return
        self.FlagDeal = True

        if SLC.Option["FlagAutoSave"]:
            if len(self.Side.QListBox.items(None)) > 0:
                self.onSave()

        i = SLC.Video.Index
        if SLC.FlagVerify:
            i = SLC.findNextImage(i, False)
            if i != -1:
                self.showImage(i, True)
        else:
            i = i - self.Speed
            if i >= 0:
                self.showImage(i)

        nexti = SLC.findNextImage(i, False)
        if nexti != -1:
            self.TxtNext.setText(f"上一保存帧：{nexti}")

        self.FlagDeal = False
        return

    def onSilderGoto(self):
        index = self.VidBar.value()
        if index != SLC.Video.Index:
            self.showImage(index, True)
        return

    def onPlay(self):
        if self.FlagPlay:
            self.FlagPlay = False
            self.BtnPlay.setText("▶")
        else:
            self.FlagPlay = True
            self.BtnPlay.setText("▇")
            thd = threading.Thread(target=self.threadPlay, daemon=True)
            thd.start()
        return

    def onDelete(self):
        if SLC.IdxLabel != -1:
            self.deleteBox(SLC.IdxLabel)
        elif SLC.IdxTrack != -1:
            idx = int(SLC.IdxTrack)

            l = self.Side.QListTracker.count()
            for i in range(l):
                item = self.Side.QListTracker.item(i)
                if id(item) == id(self.ItemTracker[idx].Item):
                    it = self.Side.QListTracker.takeItem(i)
                    del it, item
                    break
            # self.Side.QListTracker.removeItemWidget(self.ItemTracker[idx].Item)
            self.deleteBox(idx, "Tracker")
            del SLC.DictTracker[idx]
        return

    def onCancel(self):
        self.switchStatus("Idle")
        return

    def threadPlay(self):
        while self.FlagPlay:
            if self.FlagDeal:
                return
            time.sleep(1 / SLC.Video.Fps)
            self.onNext()
        return

    def onSave(self):
        lines = list()
        vw, vh = SLC.getVideoSize()
        for box in self.ListBox:
            if not box.FlagUsed:
                continue
            label = box.Index
            x, y, w, h = box.getRect()
            if SLC.Data["FlagClip"] and not SLC.FlagSetMode:
                x, y, w, h = SLC.cvtoImageRect(x, y, w, h)
                fx = (x - SLC.Data["Clip"][0] + w / 2) / SLC.Data["Clip"][2]
                fy = (y - SLC.Data["Clip"][1] + w / 2) / SLC.Data["Clip"][3]
                fw = w / SLC.Data["Clip"][2]
                fh = h / SLC.Data["Clip"][3]
            else:
                if SLC.FlagWidth:
                    fx = (x + w / 2) / SLC.ScaledWidth
                    fy = (
                        y - (SLC.FrameHeight - SLC.ScaledHeight) / 2 + h / 2
                    ) / SLC.ScaledHeight
                else:
                    fx = (
                        x - (SLC.FrameWidth - SLC.ScaledWidth) / 2 + w / 2
                    ) / SLC.ScaledWidth
                    fy = (y + h / 2) / SLC.ScaledHeight
                fw = w / SLC.ScaledWidth
                fh = h / SLC.ScaledHeight
            lines.append(f"{label} {fx} {fy} {fw} {fh}\n")

        img = SLC.saveImage(lines)
        SLC.saveOption()
        self.Side.loadImage()
        self.changeBack("Saved")
        return img

    def getCrtLabelIndex(self):
        crt = self.Side.QListLabel.currentRow()
        item: LabelItem = self.ItemLabel[crt]
        index: int = item.Index
        return index

    def setClip(self, rect=None):
        if rect is None:
            self.Frame.HandClip1.hide()
            self.Frame.HandClip2.hide()
            self.Frame.HandClipM.hide()
        else:
            x1, y1, w, h = SLC.cvtoFrameRect(*rect)
            self.Frame.HandClip1.move(x1, y1)
            self.Frame.HandClip2.move(x1 + w - 10, y1 + h - 10)
            self.Frame.HandClipM.move(x1 + w // 2 - 10, y1 - 10)
            self.Frame.HandClip1.show()
            self.Frame.HandClip2.show()
            self.Frame.HandClipM.show()
            self.Side.InputWidth.setText(str(SLC.Data["Clip"][2]))
            self.Side.InputHeight.setText(str(SLC.Data["Clip"][3]))
        return

    # Box.
    def selectBox(self, bid, box_type="Label"):
        if box_type == "Label":
            SLC.IdxLabel = bid
            SLC.IdxTrack = -1
            for box in self.ListBox:
                box.select(box.BID == bid)
            for box in self.ListTrack:
                box.select(False)
        else:
            SLC.IdxLabel = -1
            SLC.IdxTrack = bid
            for box in self.ListTrack:
                box.select(box.BID == bid)
            for box in self.ListBox:
                box.select(False)
        return

    def addBox(self, x, y, w, h, index, color):
        self.Frame.setToolTip(None)
        self.Frame.BoxTodo.hide()

        if SLC.Video.Index in SLC.Data["Verified"]:
            SLC.Data["Verified"].remove(SLC.Video.Index)

        for box in self.ListBox:
            if not box.FlagUsed:
                box.useBox(x, y, w, h, color, index)
                break

        self.onCancel()
        self.Side.loadBox()
        self.changeBack("Unsaved")
        return

    def clearBox(self):
        for box in self.ListBox:
            box.FlagUsed = False
        self.hideAllBox()
        self.Side.loadBox()
        return

    def hideAllBox(self):
        for box in self.ListBox + self.ListTrack:
            box.hide()
        return

    def deleteBox(self, bid, box_type="Label"):
        if box_type == "Label":
            self.ListBox[bid].FlagUsed = False
            self.ListBox[bid].hide()
            SLC.IdxLabel = -1
            self.Side.loadBox()
            self.changeBack("Unsaved")
        else:
            self.ListTrack[bid].FlagUsed = False
            self.ListTrack[bid].hide()
            SLC.IdxTrack = -1
        return

    def changeBack(self, back="None"):
        if back == "None":
            color = "#555"
        elif back == "Unsaved":
            color = "#dd0"
        elif back == "Saved":
            color = "#2e2"
        elif back == "Verified":
            color = "#6cf"
        elif back == "Removed":
            color = "#f30"
        if color != self.ColorBorder:
            self.ColorBorder = color
            self.Frame.setStyleSheet(f"#FrameImage{{border:5px solid {color};}}")

        return

    pass

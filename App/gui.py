import os
import threading
import time, random

import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from PyQt6.QtCore import Qt

import cv2

from . import getCore, LabelItem, TrackItem, LabelBox

VTLC = getCore()


class ImageFrame(qtw.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("QFrame{background-color:#555;" "border:5px solid #000;}")
        self.setToolTipDuration(1000)

        self.StartX = 0
        self.StartY = 0
        self.ColorBorder = "#555"
        self.Win: TLWindow = self.parent().parent()
        self.Image = qtw.QLabel(self)
        self.Image.setMouseTracking(True)
        self.Image.mouseMoveEvent = self.mouseMoveEvent

        self.BoxTodo = qtw.QLabel(self)
        self.BoxTodo.hide()
        self.setTodoBox()

        self.ListBox = [LabelBox(self, i) for i in range(16)]

        self.ListTrack = [LabelBox(self, i, "Track") for i in range(8)]
        return

    def resizeEvent(self, a0: qtg.QResizeEvent):
        self.Image.setGeometry(0, 0, self.width(), self.height())
        return super().resizeEvent(a0)

    def mouseMoveEvent(self, ev: qtg.QMouseEvent):
        if not VTLC.isOpened():
            return

        p = ev.pos()
        x = p.x()
        y = p.y()
        px, py = VTLC.cvtoFramePos(x, y)
        self.Win.LabelInfo.setText(f"({px},{py})/(0,0,0)")
        if VTLC.Status == "StartPoint":
            label, color = self.Win.getCurrentLabel()
            self.setToolTip(f"{label}: {self.Win.getNameByLabel()}")
        elif VTLC.Status in {"EndPoint", "EndTrack"}:
            self.BoxTodo.setGeometry(
                min(x, self.StartX),
                min(y, self.StartY),
                abs(self.StartX - x),
                abs(self.StartY - y),
            )
        elif VTLC.Status == "StartTrack":
            label, color = self.Win.getCurrentLabel()
            self.setToolTip(
                f"{label}: {self.Win.getNameByLabel()}\nMethod: {self.Win.TrackerMethod}"
            )
        return super().mouseMoveEvent(ev)

    def leaveEvent(self, a0: qtc.QEvent):
        self.Win.LabelInfo.setText("(-1,-1)/(0,0,0)")
        return super().leaveEvent(a0)

    def mouseReleaseEvent(self, ev: qtg.QMouseEvent):
        if VTLC.Status == "StartPoint":
            VTLC.Status = "EndPoint"
            self.StartX = ev.pos().x()
            self.StartY = ev.pos().y()
            self.setTodoBox()
            self.BoxTodo.show()
        elif VTLC.Status == "EndPoint":
            mx = ev.pos().x()
            my = ev.pos().y()
            x = min(mx, self.StartX)
            y = min(my, self.StartY)
            w = abs(mx - self.StartX)
            h = abs(my - self.StartY)
            label, color = self.Win.getCurrentLabel()
            self.addLabelBox(x, y, w, h, label, color)
        elif VTLC.Status == "StartTrack":
            VTLC.Status = "EndTrack"
            self.StartX = ev.pos().x()
            self.StartY = ev.pos().y()
            self.setTodoBox("dashed")
            self.BoxTodo.show()
        elif VTLC.Status == "EndTrack":
            self.setToolTip(None)
            self.setTodoBox()
            self.BoxTodo.hide()
            x = ev.pos().x()
            y = ev.pos().y()
            label, color = self.Win.getCurrentLabel()

            bid = -1
            for box in self.ListTrack:
                if not box.FlagUsed:
                    box.useBox(
                        min(x, self.StartX),
                        min(y, self.StartY),
                        abs(x - self.StartX),
                        abs(y - self.StartY),
                        color,
                        label,
                    )
                    bid = box.BID
                    break

            self.Win.addTrackItem(bid, label, box.getBoxRect(False))
            self.Win.onCancel()
        return

    def clearBox(self):
        for box in self.ListBox:
            box.FlagUsed = False
        self.hideAllBox()
        return

    def hideAllBox(self):
        for box in self.ListBox:
            box.hide()
        return

    def setPixmap(self, pix):
        self.Image.setPixmap(pix)
        return

    def changeBack(self, status="None"):
        if status == "None":
            color = "#555"
        elif status == "Unsaved":
            color = "#dd0"
        elif status == "Saved":
            color = "#2e2"
        elif status == "Verified":
            color = "#6cf"
        if color != self.ColorBorder:
            self.ColorBorder = color
            self.setStyleSheet(
                f"QFrame{{background-color:#222;border:5px solid {color};}}"
            )
        return

    def deleteBox(self, bid, box_type="Label"):
        if box_type == "Label":
            self.ListBox[bid].FlagUsed = False
            self.ListBox[bid].hide()
            VTLC.IdxLabel = -1
            self.changeBack("Unsaved")
        else:
            self.ListTrack[bid].FlagUsed = False
            self.ListTrack[bid].hide()
            VTLC.IdxTrack = -1
        return

    def setTodoBox(self, style="solid"):
        if style == "solid":
            stl = r"QLabel{border:2px solid red;background-color:rgba(0,0,0,0)}"
        elif style == "dashed":
            stl = r"QLabel{border:2px dashed red;background-color:rgba(0,0,0,0)}"
        self.BoxTodo.setStyleSheet(stl)
        return

    def addLabelBox(self, x, y, w, h, l, c):
        self.setToolTip(None)
        self.BoxTodo.hide()

        if VTLC.Video.Index in VTLC.Option["Verified"]:
            VTLC.Option["Verified"].remove(VTLC.Video.Index)

        for box in self.ListBox:
            if not box.FlagUsed:
                box.useBox(x, y, w, h, c, l)
                break
        self.Win.onCancel()
        self.changeBack("Unsaved")
        return

    pass


class TLMenu(qtw.QMenuBar):
    def __init__(self, parent: qtw.QWidget):
        super().__init__(parent)
        self.Win: TLWindow = self.parent().parent()
        self.init()
        return

    def init(self):
        # 文件。
        act_open = qtg.QAction("打开…", self)
        act_open.setShortcut("Ctrl+O")
        act_open.triggered.connect(self.Win.onOpen)

        self.ActDisp = qtg.QAction("切换显示", self)
        self.ActDisp.setShortcut("Tab")
        self.ActDisp.triggered.connect(lambda: self.Win.onDisp(True))

        self.ActCancel = qtg.QAction("取消", self)
        self.ActCancel.setShortcut("Esc")
        self.ActCancel.triggered.connect(self.Win.onCancel)

        act_exit = qtg.QAction("退出", self)
        act_exit.setShortcut("Ctrl+W")
        act_exit.triggered.connect(qtw.QApplication.instance().quit)

        # 编辑。
        self.ActNect = qtg.QAction("下一张", self)
        self.ActNect.setShortcut("D")
        self.ActNect.triggered.connect(self.Win.onNext)

        self.ActPrev = qtg.QAction("上一张", self)
        self.ActPrev.setShortcut("A")
        self.ActPrev.triggered.connect(self.Win.onPrev)

        self.ActLabel = qtg.QAction("标注", self)
        self.ActLabel.setShortcut("E")
        self.ActLabel.triggered.connect(self.Win.onLabel)

        self.ActSave = qtg.QAction("保存", self)
        self.ActSave.setShortcut("S")
        self.ActSave.triggered.connect(self.Win.onSave)

        self.ActVerify = qtg.QAction("校对", self)
        self.ActVerify.setShortcut("V")
        self.ActVerify.triggered.connect(self.onVerify)

        self.ActDel = qtg.QAction("删除", self)
        self.ActDel.setShortcut("X")
        self.ActDel.triggered.connect(self.Win.onDelete)

        self.ActPlay = qtg.QAction("播放/暂停", self)
        self.ActPlay.setShortcut("Space")
        self.ActPlay.triggered.connect(self.Win.onPlay)

        self.ActAuto = qtg.QAction("自动保存", self)
        self.ActAuto.setCheckable(True)
        self.ActAuto.triggered.connect(self.onAutoSave)
        self.ActVerifyMode = qtg.QAction("校对模式", self)
        self.ActVerifyMode.setCheckable(True)
        self.ActVerifyMode.triggered.connect(self.onVerifyMode)

        # 追踪。
        self.ActTrack = qtg.QAction("新建追踪器", self)
        self.ActTrack.setShortcut("T")
        self.ActTrack.triggered.connect(self.onCreateTracker)

        self.ActAcept = qtg.QAction("采纳", self)
        self.ActAcept.setShortcut("Q")
        self.ActAcept.triggered.connect(self.Win.onAcept)

        self.ActAll = qtg.QAction("全部采纳", self)
        self.ActAll.setShortcut("Y")
        self.ActAll.triggered.connect(self.Win.onAceptAll)

        self.ActKCF = qtg.QAction("KCF", self)
        self.ActKCF.setCheckable(True)
        self.ActKCF.setChecked(True)
        self.ActKCF.triggered.connect(lambda: self.onTrackMethod("KCF"))
        self.ActCSRT = qtg.QAction("CSRT", self)
        self.ActCSRT.setCheckable(True)
        self.ActCSRT.triggered.connect(lambda: self.onTrackMethod("CSRT"))
        self.ActMOS = qtg.QAction("MOSSE", self)
        self.ActMOS.setCheckable(True)
        self.ActMOS.triggered.connect(lambda: self.onTrackMethod("MOSSE"))
        self.GroupTrack = qtg.QActionGroup(self)
        self.GroupTrack.addAction(self.ActKCF)
        self.GroupTrack.addAction(self.ActCSRT)
        self.GroupTrack.addAction(self.ActMOS)

        self.MenuFile = self.addMenu("文件(F)")
        self.MenuFile.addAction(act_open)
        self.MenuFile.addAction(self.ActDisp)
        self.MenuFile.addAction(self.ActCancel)
        self.MenuFile.addAction(act_exit)

        self.MenuEdit = self.addMenu("编辑(E)")
        self.MenuEdit.addAction(self.ActNect)
        self.MenuEdit.addAction(self.ActPrev)
        self.MenuEdit.addAction(self.ActLabel)
        self.MenuEdit.addAction(self.ActSave)
        self.MenuEdit.addAction(self.ActDel)
        self.MenuEdit.addAction(self.ActPlay)
        self.MenuEdit.addSeparator()
        self.MenuEdit.addAction(self.ActAuto)
        self.MenuEdit.addAction(self.ActVerify)
        self.MenuEdit.addAction(self.ActVerifyMode)

        self.MenuTrack = self.addMenu("追踪(T)")
        self.MenuTrack.addAction(self.ActTrack)
        self.MenuTrack.addAction(self.ActAcept)
        self.MenuTrack.addAction(self.ActAll)
        self.MenuTrack.addSeparator()
        self.MenuTrack.addAction(self.ActKCF)
        self.MenuTrack.addAction(self.ActCSRT)
        self.MenuTrack.addAction(self.ActMOS)
        self.addMenu("帮助(H)")

        self.setMenuEnablity(False)
        return

    def setMenuEnablity(self, flag=True):
        if flag:
            for act in self.MenuEdit.actions():
                act.setEnabled(True)

            for act in self.MenuTrack.actions():
                act.setEnabled(True)
        else:
            for act in self.MenuEdit.actions():
                act.setDisabled(True)

            for act in self.MenuTrack.actions():
                act.setDisabled(True)

    def onTrackMethod(self, m):
        self.Win.TrackerMethod = m
        return

    def onAutoSave(self):
        VTLC.FlagAutoSave = not VTLC.FlagAutoSave
        return

    def onVerify(self):
        i = VTLC.Video.Index
        if i in VTLC.Option["Verified"]:
            VTLC.Option["Verified"].remove(i)
            self.Win.Frame.changeBack("Saved")
        else:
            VTLC.Option["Verified"].append(i)
            self.Win.Frame.changeBack("Verified")
        if VTLC.FlagAutoSave:
            VTLC.saveOption()
        return

    def onVerifyMode(self):
        VTLC.FlagVerify = not VTLC.FlagVerify
        return

    def onCreateTracker(self):
        if VTLC.Status == "Idle":
            self.Win.Frame.setCursor(Qt.CursorShape.CrossCursor)
            VTLC.Status = "StartTrack"
            self.Win.Frame.hideAllBox()
        return

    pass


class TLWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__(None)
        self.FlagPlay = False
        self.FlagDeal = False
        self.FlagDispLabel = True
        self.FlagDispTrack = True
        self.ItemLabel = list()
        self.ItemTracker = dict()
        self.DictColor = dict()
        self.Speed = 1
        self.TrackerMethod = "KCF"
        return

    def resizeEvent(self, a0):
        w = self.width()
        h = self.height()
        self.Frame.setMinimumSize(int(0.75 * w) - 15, int(0.8 * h))
        self.QListLabel.setMinimumWidth(int(0.25 * w) - 15)

        self.Widget.resize(self.width(), self.height())
        return super().resizeEvent(a0)

    def init(self):
        self.Widget = qtw.QWidget(self)
        self.Widget.resize(VTLC.CW, VTLC.CH)

        self.Menu = TLMenu(self.Widget)

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
        self.InputSpeed = qtw.QLineEdit("1", self.Widget)
        self.InputSpeed.setValidator(qtg.QIntValidator())
        self.InputSpeed.setMaximumWidth(50)

        self.Frame = ImageFrame(self.Widget)

        self.LabelList = qtw.QLabel("标签列表", self.Widget)
        self.BtnAdd = qtw.QPushButton("+", self.Widget)
        self.BtnDel = qtw.QPushButton("-", self.Widget)
        self.LabelCurrent = qtw.QLabel("当前：-1", self.Widget)
        self.QListLabel = qtw.QListWidget(self.Widget)
        self.QListTracker = qtw.QListWidget(self.Widget)

        layout_v1 = qtw.QVBoxLayout()
        layout_h21 = qtw.QHBoxLayout()
        layout_h22 = qtw.QHBoxLayout()
        layout_v3 = qtw.QVBoxLayout()
        layout_h4 = qtw.QHBoxLayout()

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
        layout_h21.addWidget(self.InputSpeed)
        layout_h21.addWidget(qtw.QLabel("x", self.Widget))
        layout_h21.setSpacing(10)
        layout_v1.addWidget(self.VidBar)
        layout_v1.addLayout(layout_h22)
        layout_h22.addWidget(self.Frame)
        layout_h22.addLayout(layout_v3)
        layout_v3.addLayout(layout_h4)
        layout_v3.addWidget(self.QListLabel)
        layout_v3.addWidget(self.QListTracker)
        layout_h4.addWidget(self.LabelList)
        layout_h4.addWidget(self.BtnAdd)
        layout_h4.addWidget(self.BtnDel)
        layout_h4.addWidget(self.LabelCurrent)

        self.VidBar.sliderMoved.connect(self.onSilderGoto)
        self.BtnPlay.clicked.connect(self.onPlay)
        self.BtnAdd.clicked.connect(self.onAddLabel)
        self.BtnDel.clicked.connect(self.onDelLabel)
        self.QListLabel.clicked.connect(self.onClickLabelList)
        self.InputSpeed.textChanged.connect(self.onEditSpeed)

        self.resize(VTLC.CW, VTLC.CH)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setWindowTitle("TrackLabel")
        self.show()
        return

    def onDisp(self, toggle=True):
        if toggle:
            if self.FlagDispLabel and self.FlagDispTrack:
                self.FlagDispTrack = False
            elif self.FlagDispLabel and not self.FlagDispTrack:
                self.FlagDispLabel = False
                self.FlagDispTrack = True
            elif not self.FlagDispLabel and self.FlagDispTrack:
                self.FlagDispLabel = False
                self.FlagDispTrack = False
            elif not self.FlagDispLabel and not self.FlagDispTrack:
                self.FlagDispLabel = True
                self.FlagDispTrack = True

        for box in self.Frame.ListBox:
            if box.FlagUsed:
                if self.FlagDispLabel:
                    box.show()
                else:
                    box.hide()
            else:
                box.hide()
        for box in self.Frame.ListTrack:
            if box.FlagUsed:
                if self.FlagDispTrack:
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

    def onOpen(self):
        fname = qtw.QFileDialog.getOpenFileName(self, "打开视频", os.getcwd())

        if fname[0]:
            res = VTLC.loadVideo(fname[0])
        else:
            res = False
        if res:
            self.VidBar.setMaximum(VTLC.Video.Count)
            self.showImage(VTLC.readImage(-1, True))
            self.Menu.setMenuEnablity()

        return

    def showImage(self, img):
        from App import cvtSec

        # opencv读取的bgr格式图片转换成rgb格式
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # pyqt5转换成自己能放的图片格式
        _image = qtg.QImage(
            img[:],
            img.shape[1],
            img.shape[0],
            img.shape[1] * 3,
            qtg.QImage.Format.Format_RGB888,
        )

        VTLC.updateWH()
        pix = qtg.QPixmap(_image).scaled(VTLC.ScaledWidth, VTLC.ScaledHeight)
        self.Frame.setPixmap(pix)

        self.InputFrame.setText(str(VTLC.Video.Index))
        self.LabelFrame.setText(f"/{VTLC.Video.Count}")
        self.LabelFps.setText(f"{VTLC.Video.Fps}fps")
        self.LabelTime.setText(cvtSec(VTLC.Video.Now) + "/" + cvtSec(VTLC.Video.Time))

        self.VidBar.setValue(VTLC.Video.Index)

        self.Frame.clearBox()

        file = f"{VTLC.VideoFolder}/labels/{VTLC.Video.Index}.txt"
        if os.path.exists(file) and not self.FlagPlay:
            if VTLC.Video.Index in VTLC.Option["Verified"]:
                self.Frame.changeBack("Verified")
            else:
                self.Frame.changeBack("Saved")
            with open(file, "r") as fd:
                lines = fd.readlines()
            for line in lines:
                label, fx, fy, fw, fh = line.split(" ")
                label = int(label)
                c = self.getColorByLabel(label)
                if c is None:
                    continue

                x, y, w, h = VTLC.cvtoFrameRect(fx, fy, fw, fh, True)
                for box in self.Frame.ListBox:
                    if not box.FlagUsed:
                        box.useBox(x, y, w, h, c, label)
                        break
        else:
            self.Frame.changeBack("None")

        for tid, tracker in VTLC.DictTracker.items():
            self.Frame.ListTrack[tid].useBox(*VTLC.cvtoFrameRect(*tracker.ROI))
        return

    def onAcept(self, idx=-1):
        if idx == -1:
            if VTLC.IdxTrack == -1:
                return
            idx = VTLC.IdxTrack
        tracker = self.Frame.ListTrack[idx]
        x = tracker.x() - 3
        y = tracker.y() - 3
        w = tracker.width() + 6
        h = tracker.height() + 6
        self.Frame.addLabelBox(x, y, w, h, tracker.Label, tracker.Color)
        return

    def onAceptAll(self):
        for tracker in self.Frame.ListTrack:
            if tracker.FlagUsed:
                self.onAcept(tracker.BID)
        return

    def onNext(self):
        if self.FlagDeal:
            return
        self.FlagDeal = True

        if VTLC.FlagAutoSave:
            self.onSave()

        i = VTLC.Video.Index
        if VTLC.FlagVerify:
            found = False
            while not found:
                i += 1
                if i > VTLC.Video.Count:
                    break
                found = os.path.exists(f"{VTLC.VideoFolder}/labels/{i}.txt")
            if found:
                self.showImage(VTLC.readImage(i, True))
        else:
            if i != VTLC.Video.Count - 1:
                self.showImage(VTLC.readImage(i + self.Speed))
        self.FlagDeal = False
        return

    def onPrev(self):
        if self.FlagDeal:
            return
        self.FlagDeal = True

        if VTLC.FlagAutoSave:
            self.onSave()

        i = VTLC.Video.Index
        if VTLC.FlagVerify:
            found = False
            while not found:
                i -= 1
                if i < 0:
                    break
                found = os.path.exists(f"{VTLC.VideoFolder}/labels/{i}.txt")
            if found:
                self.showImage(VTLC.readImage(i, True))
        else:
            if i != 0:
                self.showImage(VTLC.readImage(i - self.Speed))
        self.FlagDeal = False
        return

    def onSilderGoto(self):
        index = self.VidBar.value()
        if index != VTLC.Video.Index:
            self.showImage(VTLC.readImage(index, True))
        return

    def onPlay(self):
        if self.FlagPlay:
            self.FlagPlay = False
        else:
            self.FlagPlay = True
            thd = threading.Thread(target=self.threadPlay, daemon=True)
            thd.start()
        return

    def onLabel(self):
        if VTLC.Status == "Idle":
            self.Frame.setCursor(Qt.CursorShape.CrossCursor)
            VTLC.Status = "StartPoint"
            self.Frame.hideAllBox()
        return

    def onDelete(self):
        if VTLC.IdxLabel != -1:
            self.Frame.deleteBox(VTLC.IdxLabel)
        elif VTLC.IdxTrack != -1:
            self.QListTracker.removeItemWidget(self.ItemTracker[VTLC.IdxTrack].Item)
            self.Frame.deleteBox(VTLC.IdxTrack, "Tracker")
        return

    def onCancel(self):
        VTLC.Status = "Idle"
        self.Frame.setCursor(Qt.CursorShape.ArrowCursor)
        self.onDisp(False)
        return

    def onAddLabel(self):
        VTLC.addLabel()
        self.loadLabels(VTLC.Option)
        return

    def onDelLabel(self):
        label, color = self.getCurrentLabel()
        VTLC.delLabel(label)
        self.loadLabels(VTLC.Option)
        return

    def threadPlay(self):
        while self.FlagPlay:
            if self.FlagDeal:
                return
            # time.sleep(1)
            time.sleep(1 / VTLC.Video.Fps)
            self.onNext()
        return

    def loadLabels(self, opt=None):
        self.QListLabel.clear()
        self.ItemLabel.clear()
        self.DictColor.clear()

        if opt is None:
            opt = VTLC.Option
        for i in range(len(opt["ClassLabel"])):
            label = opt["ClassLabel"][i]
            color = self.genRandomColor()
            item = qtw.QListWidgetItem(self.QListLabel)
            widget = LabelItem(
                parent=self.Widget,
                label=label,
                name=opt["ClassName"][i],
                color=color,
                item=item,
            )
            self.DictColor[label] = color
            self.QListLabel.setItemWidget(item, widget)
            self.QListLabel.addItem(item)
            self.ItemLabel.append(widget)
        for box in self.Frame.ListBox:
            if box.FlagUsed:
                color = self.getColorByLabel(box.Label)
                if color is not None:
                    box.setColor(color)
        self.onClickLabelList()
        return

    def getColorByLabel(self, label):
        if label not in self.DictColor:
            return None
        return self.DictColor[label]

    def getNameByLabel(self, label=-1):
        if label == -1:
            label, color = self.getCurrentLabel()
        name = ""
        for item in self.ItemLabel:
            item: LabelItem
            if item.Label == label:
                name = item.LabelName.text()
        return name

    def onClickLabelList(self):
        item: LabelItem = self.ItemLabel[self.QListLabel.currentRow()]
        self.LabelCurrent.setText("当前：" + item.LabelIndex.text())
        return

    def onSave(self):
        img_name = f"{VTLC.VideoFolder}/images/{VTLC.Video.Index}.jpg"
        lbl_name = f"{VTLC.VideoFolder}/labels/{VTLC.Video.Index}.txt"
        cv2.imwrite(img_name, VTLC.Video.Frame)

        lines = list()
        for box in self.Frame.ListBox:
            if not box.FlagUsed:
                continue
            label = box.Label
            fx, fy, fw, fh = box.getBoxRect()
            lines.append(f"{label} {fx} {fy} {fw} {fh}\n")

        with open(lbl_name, "w") as fd:
            fd.writelines(lines)

        VTLC.saveOption()
        self.Frame.changeBack("Saved")
        return

    def genRandomColor(self):
        color = f"hsv({str(random.randint(0,254))},200,200)"
        return color

    def getCurrentLabel(self):
        item: LabelItem = self.ItemLabel[self.QListLabel.currentRow()]
        label: int = item.Label
        color: str = self.getColorByLabel(label)
        return label, color

    def addTrackItem(self, bid, label, roi):
        color = self.getColorByLabel(label)
        item = qtw.QListWidgetItem(self.QListTracker)
        start = VTLC.Video.Index
        widget = TrackItem(
            parent=self.Widget,
            label=label,
            bid=bid,
            name=f"Tracker: {label}",
            color=color,
            method=self.TrackerMethod,
            start=start,
            item=item,
        )
        self.QListTracker.setItemWidget(item, widget)
        self.QListTracker.addItem(item)
        self.ItemTracker[bid] = widget
        VTLC.createTracker(tid=bid, method=self.TrackerMethod, roi=roi)
        return

    def selectBox(self, bid, box_type="Label"):
        if box_type == "Label":
            VTLC.IdxLabel = bid
            VTLC.IdxTrack = -1
            for box in self.Frame.ListBox:
                box.select(box.BID == bid)
            for box in self.Frame.ListTrack:
                box.select(False)
        else:
            VTLC.IdxLabel = -1
            VTLC.IdxTrack = bid
            for box in self.Frame.ListTrack:
                box.select(box.BID == bid)
            for box in self.Frame.ListBox:
                box.select(False)
        return

    pass

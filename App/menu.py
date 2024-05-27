import os

import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg

from . import getCore

SLC = getCore()


class MainMenu(qtw.QMenuBar):
    def __init__(self, parent: qtw.QWidget):
        super().__init__(parent)
        self.init()
        return

    def init(self):
        # 文件。
        act_open = qtg.QAction("打开…", self)
        act_open.setShortcut("Ctrl+O")
        act_open.triggered.connect(self.onOpen)

        self.ActDisp = qtg.QAction("切换显示", self)
        self.ActDisp.setShortcut("Tab")
        self.ActDisp.triggered.connect(lambda: SLC.Shell.onDisp(True))

        self.ActCancel = qtg.QAction("取消", self)
        self.ActCancel.setShortcut("Esc")
        self.ActCancel.triggered.connect(SLC.Shell.onCancel)

        act_exit = qtg.QAction("退出", self)
        act_exit.setShortcut("Ctrl+W")
        act_exit.triggered.connect(qtw.QApplication.instance().quit)

        # 编辑。
        self.ActNect = qtg.QAction("下一张", self)
        self.ActNect.setShortcut("D")
        self.ActNect.triggered.connect(SLC.Shell.onNext)

        self.ActPrev = qtg.QAction("上一张", self)
        self.ActPrev.setShortcut("A")
        self.ActPrev.triggered.connect(SLC.Shell.onPrev)

        self.ActLabel = qtg.QAction("标注", self)
        self.ActLabel.setShortcut("E")
        self.ActLabel.triggered.connect(self.onLabel)

        self.ActSave = qtg.QAction("保存", self)
        self.ActSave.setShortcut("S")
        self.ActSave.triggered.connect(SLC.Shell.onSave)

        self.ActRmv = qtg.QAction("移除", self)
        self.ActRmv.setShortcut("W")
        self.ActRmv.triggered.connect(self.onRemove)

        self.ActVerify = qtg.QAction("校对", self)
        self.ActVerify.setShortcut("V")
        self.ActVerify.triggered.connect(self.onVerify)

        self.ActDel = qtg.QAction("删除", self)
        self.ActDel.setShortcut("X")
        self.ActDel.triggered.connect(SLC.Shell.onDelete)

        self.ActPlay = qtg.QAction("播放/暂停", self)
        self.ActPlay.setShortcut("Space")
        self.ActPlay.triggered.connect(SLC.Shell.onPlay)

        self.ActAuto = qtg.QAction("自动保存", self)
        self.ActAuto.setCheckable(True)
        self.ActAuto.triggered.connect(self.onAutoSave)

        self.ActVerifyMode = qtg.QAction("校对模式", self)
        self.ActVerifyMode.setCheckable(True)
        self.ActVerifyMode.triggered.connect(self.onVerifyMode)

        self.ActRot = qtg.QAction("旋转", self)
        self.ActRot.setShortcut("Ctrl+R")
        self.ActRot.triggered.connect(self.onRotate)

        self.ActClip = qtg.QAction("裁剪", self)
        self.ActClip.setShortcut("C")
        self.ActClip.setCheckable(True)
        self.ActClip.triggered.connect(self.onClip)

        # 追踪。
        self.ActTrack = qtg.QAction("新建追踪器", self)
        self.ActTrack.setShortcut("T")
        self.ActTrack.triggered.connect(self.onCreateTracker)

        self.ActAcept = qtg.QAction("采纳", self)
        self.ActAcept.setShortcut("Q")
        self.ActAcept.triggered.connect(self.onAcept)

        self.ActAll = qtg.QAction("全部采纳", self)
        self.ActAll.setShortcut("Y")
        self.ActAll.triggered.connect(self.onAceptAll)

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
        self.MenuEdit.addAction(self.ActRmv)
        self.MenuEdit.addAction(self.ActDel)
        self.MenuEdit.addAction(self.ActPlay)
        self.MenuEdit.addAction(self.ActRot)
        self.MenuEdit.addAction(self.ActClip)
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

    def onOpen(self):
        fname = qtw.QFileDialog.getOpenFileName(self, "打开视频", os.getcwd())

        res = False
        if fname[0]:
            res = SLC.loadVideo(fname[0])

        if res:
            SLC.Shell.Side.loadLabels()
            SLC.Shell.Side.loadImage()
            SLC.Shell.VidBar.setMaximum(SLC.Video.Count)
            SLC.Shell.showImage(SLC.readImage(-1, True))
            self.setMenuEnablity()
            if SLC.Option["FlagAutoSave"]:
                self.ActAuto.setChecked(True)
            if SLC.Option["FlagVerify"]:
                self.ActVerifyMode.setChecked(True)
            if SLC.Data["FlagClip"]:
                self.ActClip.setChecked(True)
        return

    def onLabel(self):
        if SLC.Status == "Idle":
            SLC.Shell.switchStatus("StartPoint")
        return

    def onAcept(self, idx=-1):
        if idx == -1:
            if SLC.IdxTrack == -1:
                return
            idx = SLC.IdxTrack
        tracker = SLC.Shell.ListTrack[idx]
        x = tracker.x() - 3
        y = tracker.y() - 3
        w = tracker.width() + 6
        h = tracker.height() + 6
        SLC.Shell.addBox(x, y, w, h, tracker.Label, tracker.Color)
        return

    def onAceptAll(self):
        for tracker in SLC.Shell.ListTrack:
            if tracker.FlagUsed:
                self.onAcept(tracker.BID)
        return

    def onTrackMethod(self, m):
        SLC.TrackerMethod = m
        return

    def onAutoSave(self):
        SLC.Option["FlagAutoSave"] = not SLC.Option["FlagAutoSave"]
        return

    def onVerify(self):
        i = SLC.Video.Index
        if i in SLC.Data["Verified"]:
            SLC.Data["Verified"].remove(i)
            SLC.Shell.changeBack("Saved")
        else:
            SLC.Data["Verified"].append(i)
            SLC.Shell.changeBack("Verified")
        if SLC.Option["FlagAutoSave"]:
            SLC.saveOption()
        return

    def onVerifyMode(self):
        SLC.Option["FlagVerify"] = not SLC.Option["FlagVerify"]
        return

    def onCreateTracker(self):
        if SLC.Status == "Idle":
            SLC.Shell.switchStatus("StartTrack")
        return

    def onRemove(self):
        SLC.removeImage()
        SLC.Shell.changeBack("Removed")
        return

    def onRotate(self):
        if SLC.Data["Rotate"] != 3:
            SLC.Data["Rotate"] += 1
        else:
            SLC.Data["Rotate"] = 0
        SLC.Shell.showImage()
        SLC.Shell.changeBack("Unsaved")
        return

    def onClip(self):
        SLC.Data["FlagClip"] = not SLC.Data["FlagClip"]
        SLC.Shell.showImage()
        SLC.Shell.changeBack("Unsaved")
        return

    pass

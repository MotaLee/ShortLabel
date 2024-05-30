import json
import os

import shutil

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
        self.initFile()
        self.initEdit()
        self.initAdv()
        self.initOpt()

        self.addMenu("帮助(H)")

        self.setMenuEnablity(False)
        return

    def initFile(self):
        # 文件。
        act_open = qtg.QAction("打开视频…", self)
        act_open.setShortcut("Ctrl+O")
        act_open.triggered.connect(self.onOpen)

        act_folder = qtg.QAction("打开文件夹…", self)
        act_folder.setShortcut("Ctrl+Alt+O")
        # act_open.triggered.connect(self.onOpen)

        act_imp_label = qtg.QAction("导入标签…", self)
        act_imp_label.triggered.connect(self.onImportLabel)

        self.ActCancel = qtg.QAction("取消", self)
        self.ActCancel.setShortcut("Esc")
        self.ActCancel.triggered.connect(SLC.Shell.onCancel)

        act_exit = qtg.QAction("退出", self)
        act_exit.setShortcut("Ctrl+W")
        act_exit.triggered.connect(qtw.QApplication.instance().quit)

        self.MenuFile = self.addMenu("文件(F)")
        self.MenuFile.addAction(act_open)
        self.MenuFile.addAction(act_folder)
        self.MenuFile.addAction(act_imp_label)
        self.MenuFile.addAction(self.ActCancel)
        self.MenuFile.addAction(act_exit)
        return

    def initOpt(self):
        self.ActDisp = qtg.QAction("切换显示", self)
        self.ActDisp.setShortcut("Tab")
        self.ActDisp.triggered.connect(lambda: SLC.Shell.onDisp(True))

        self.ActAuto = qtg.QAction("自动保存", self)
        self.ActAuto.setCheckable(True)
        self.ActAuto.triggered.connect(self.onAutoSave)

        self.ActVerifyMode = qtg.QAction("校对模式", self)
        self.ActVerifyMode.setCheckable(True)
        self.ActVerifyMode.triggered.connect(self.onVerifyMode)

        self.ActClip = qtg.QAction("裁剪模式", self)
        self.ActClip.setCheckable(True)
        self.ActClip.triggered.connect(self.onClip)

        self.ActSetMode = qtg.QAction("已保存图片优先显示", self)
        self.ActSetMode.setCheckable(True)
        self.ActSetMode.triggered.connect(self.onSetMode)

        self.MenuOpt = self.addMenu("选项(O)")
        self.MenuOpt.addAction(self.ActDisp)
        self.MenuOpt.addAction(self.ActClip)
        self.MenuOpt.addAction(self.ActAuto)
        self.MenuOpt.addAction(self.ActVerifyMode)
        self.MenuOpt.addAction(self.ActSetMode)
        return

    def initEdit(self):
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

        self.ActRot = qtg.QAction("旋转", self)
        self.ActRot.setShortcut("Ctrl+R")
        self.ActRot.triggered.connect(self.onRotate)

        self.MenuEdit = self.addMenu("编辑(E)")
        self.MenuEdit.addAction(self.ActNect)
        self.MenuEdit.addAction(self.ActPrev)
        self.MenuEdit.addAction(self.ActLabel)
        self.MenuEdit.addAction(self.ActSave)
        self.MenuEdit.addAction(self.ActRmv)
        self.MenuEdit.addAction(self.ActDel)
        self.MenuEdit.addAction(self.ActPlay)
        self.MenuEdit.addAction(self.ActRot)
        self.MenuEdit.addAction(self.ActVerify)

        return

    def initAdv(self):
        # 追踪。
        self.ActTrack = qtg.QAction("新建追踪器", self)
        self.ActTrack.setShortcut("T")
        self.ActTrack.triggered.connect(self.onCreateTracker)

        self.ActAcept = qtg.QAction("采纳", self)
        self.ActAcept.setShortcut("Q")
        self.ActAcept.triggered.connect(lambda: self.onAccept())

        self.ActAll = qtg.QAction("全部采纳", self)
        self.ActAll.setShortcut("F")
        self.ActAll.triggered.connect(self.onAceptAll)

        self.ActForbid = qtg.QAction("禁用", self)
        self.ActForbid.setShortcut("G")
        self.ActForbid.triggered.connect(self.onForbid)

        self.ActKCF = qtg.QAction("KCF", self)
        self.ActKCF.setCheckable(True)
        self.ActKCF.triggered.connect(lambda: self.onTrackMethod("KCF"))
        self.ActCSRT = qtg.QAction("CSRT", self)
        self.ActCSRT.setChecked(True)
        self.ActCSRT.setCheckable(True)
        self.ActCSRT.triggered.connect(lambda: self.onTrackMethod("CSRT"))
        self.ActMOS = qtg.QAction("MOSSE", self)
        self.ActMOS.setCheckable(True)
        self.ActMOS.triggered.connect(lambda: self.onTrackMethod("MOSSE"))
        self.GroupTrack = qtg.QActionGroup(self)
        self.GroupTrack.addAction(self.ActKCF)
        self.GroupTrack.addAction(self.ActCSRT)
        self.GroupTrack.addAction(self.ActMOS)

        self.MenuTrack = self.addMenu("高级(T)")
        self.MenuTrack.addAction(self.ActTrack)
        self.MenuTrack.addAction(self.ActAcept)
        self.MenuTrack.addAction(self.ActAll)
        self.MenuTrack.addAction(self.ActForbid)
        self.MenuTrack.addSeparator()
        self.MenuTrack.addAction(self.ActCSRT)
        self.MenuTrack.addAction(self.ActKCF)
        self.MenuTrack.addAction(self.ActMOS)
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
            SLC.Shell.VidBar.setMaximum(SLC.Video.Count - 1)
            SLC.Shell.showImage()
            self.setMenuEnablity()
            if SLC.Option["FlagAutoSave"]:
                self.ActAuto.setChecked(True)
            if SLC.Option["FlagVerify"]:
                self.ActVerifyMode.setChecked(True)
            if SLC.Data["FlagClip"]:
                self.ActClip.setChecked(True)
        return

    def onImportLabel(self):
        fname = qtw.QFileDialog.getOpenFileName(self, "导入标签", os.getcwd(), "*.json")

        if fname[0]:
            with open(fname[0], "r") as f:
                data = json.loads(f.read())
                SLC.Data["Class"] = data["Class"]
            SLC.Shell.Side.loadLabels()
        return

    def onLabel(self):
        if SLC.Status == "Idle":
            SLC.Shell.switchStatus("StartPoint")
        return

    def onAccept(self, idx=-1):
        if idx == -1:
            if SLC.IdxTrack == -1:
                return
            idx = SLC.IdxTrack
        tracker = SLC.Shell.ListTrack[idx]
        x = tracker.x() - 3
        y = tracker.y() - 3
        w = tracker.width() + 6
        h = tracker.height() + 6
        SLC.Shell.addBox(x, y, w, h, tracker.Index, tracker.Color)
        return

    def onAceptAll(self):
        for tracker in SLC.Shell.ListTrack:
            if tracker.FlagUsed and tracker.isVisible():
                self.onAccept(tracker.BID)
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

    def onSetMode(self):
        SLC.FlagSetMode = not SLC.FlagSetMode
        SLC.Shell.showImage()
        return

    def onForbid(self):
        if SLC.IdxTrack == -1:
            disable = False
            for box in SLC.Shell.ListTrack:
                if box.isVisible():
                    disable = True
                    break
            for item in SLC.Shell.ItemTracker.values():
                if disable == item.FlagEnable:
                    item.BtnEna.toggle()
        else:
            SLC.Shell.ItemTracker[SLC.IdxTrack].BtnEna.toggle()
            SLC.IdxTrack = -1
        return

    pass

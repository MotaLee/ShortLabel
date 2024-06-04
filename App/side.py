import os
import threading
import time

import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg

from . import getCore, LabelItem, TrackItem

SLC = getCore()


class SideFrame(qtw.QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.TabLabel = qtw.QWidget(self)
        self.TabAdv = qtw.QWidget(self)
        self.TabAI = qtw.QWidget(self)

        self.addTab(self.TabLabel, "标签")
        self.addTab(self.TabAdv, "高级")
        self.addTab(self.TabAI, "AI")

        self.initLabel()
        self.initAdv()
        self.initAI()

        self.setStyleSheet("QListWidget{border:2px solid #ddd;}")
        return

    def initLabel(self):
        self.LblList = qtw.QLabel("标签列表", self.TabLabel)
        self.BtnAdd = qtw.QPushButton("+", self.TabLabel)
        self.BtnDel = qtw.QPushButton("-", self.TabLabel)
        self.LblCrt = qtw.QLabel("当前：-1", self.TabLabel)
        self.QListLabel = qtw.QListWidget(self.TabLabel)
        self.TxtBox = qtw.QLabel("标注框：", self.TabLabel)
        self.QListBox = qtw.QListWidget(self.TabLabel)
        self.TxtImage = qtw.QLabel("图片文件：", self.TabLabel)
        self.QListImage = qtw.QListWidget(self.TabLabel)

        lol_v1 = qtw.QVBoxLayout()
        lol_h2 = qtw.QHBoxLayout()
        lol_h2.addWidget(self.LblList)
        lol_h2.addWidget(self.BtnAdd)
        lol_h2.addWidget(self.BtnDel)
        lol_h2.addWidget(self.LblCrt)
        lol_v1.addLayout(lol_h2)
        lol_v1.addWidget(self.QListLabel)
        lol_v1.addWidget(self.TxtBox)
        lol_v1.addWidget(self.QListBox)
        lol_v1.addWidget(self.TxtImage)
        lol_v1.addWidget(self.QListImage)
        self.TabLabel.setLayout(lol_v1)

        self.QListLabel.clicked.connect(self.onClickLabelList)
        self.QListImage.clicked.connect(self.onClickImageList)
        self.BtnAdd.clicked.connect(self.onAddLabel)
        self.BtnDel.clicked.connect(self.onDelLabel)
        return

    def initAdv(self):
        self.TxtClip = qtw.QLabel("裁剪大小：", self.TabAdv)
        self.InputWidth = qtw.QLineEdit("1280", self.TabAdv)
        self.InputWidth.setValidator(qtg.QIntValidator())
        self.InputWidth.setMaximumWidth(50)
        self.InputHeight = qtw.QLineEdit("720", self.TabAdv)
        self.InputHeight.setValidator(qtg.QIntValidator())
        self.InputHeight.setMaximumWidth(50)
        self.BtnClip = qtw.QPushButton("确定", self.TabAdv)

        self.ImgClip = qtw.QLabel(self.TabAdv)
        self.ImgClip.setMinimumHeight(200)

        self.TxtTracker = qtw.QLabel("追踪器：", self.TabAdv)
        self.QListTracker = qtw.QListWidget(self.TabAdv)
        self.TxtTemplate = qtw.QLabel("模板：", self.TabAdv)
        self.QListTemplate = qtw.QListWidget(self.TabAdv)

        loa_v1 = qtw.QVBoxLayout()
        loa_h2 = qtw.QHBoxLayout()
        loa_v1.addLayout(loa_h2)
        loa_h2.addWidget(self.TxtClip)
        loa_h2.addWidget(self.InputWidth)
        loa_h2.addWidget(qtw.QLabel("x", self.TabAdv))
        loa_h2.addWidget(self.InputHeight)
        loa_h2.addWidget(self.BtnClip)
        loa_v1.addWidget(self.ImgClip)
        loa_v1.addWidget(self.TxtTracker)
        loa_v1.addWidget(self.QListTracker)
        loa_v1.addWidget(self.TxtTemplate)
        loa_v1.addWidget(self.QListTemplate)
        self.TabAdv.setLayout(loa_v1)

        self.BtnClip.clicked.connect(self.onClip)
        return

    def initAI(self):
        self.TxtMethod = qtw.QLabel("AI方法", self.TabAI)
        self.CmbAI = qtw.QComboBox(self.TabAI)
        self.CmbAI.addItem("Yolov5")
        self.CmbAI.addItem("Yolov8")
        self.CmbAI.addItem("GrondingDINO")
        self.CmbAI.addItem("GrondingSAM")

        self.IptPath = qtw.QLineEdit(self)
        self.IptPath.setText(
            r"C:/Work/OneDrive/Project/ShortLabel/Lib/Yolov5/Pt/best.pt")
        self.BtnExplore = qtw.QPushButton("浏览…", self)
        self.BtnLoad = qtw.QPushButton("载入", self)
        self.TxtAIHint = qtw.QLabel(self)

        loi_1v = qtw.QVBoxLayout()
        loi_2h1 = qtw.QHBoxLayout()
        loi_2h2 = qtw.QHBoxLayout()
        loi_1v.addLayout(loi_2h1)
        loi_2h1.addWidget(self.TxtMethod)
        loi_2h1.addWidget(self.CmbAI)
        loi_1v.addLayout(loi_2h2)
        loi_2h2.addWidget(self.IptPath)
        loi_2h2.addWidget(self.BtnExplore)
        loi_2h2.addWidget(self.BtnLoad)
        loi_1v.addWidget(self.TxtAIHint)
        self.TabAI.setLayout(loi_1v)

        self.BtnExplore.clicked.connect(self.onClickExplore)
        self.BtnLoad.clicked.connect(self.onClickLoad)
        return

    def onClickExplore(self):
        fname = qtw.QFileDialog.getOpenFileName(
            self, "导入模型", os.getcwd(), "*.pt")

        self.IptPath.setText(fname[0])
        return

    def onClickLoad(self):
        self.TxtAIHint.setText("模型加载中……")
        model = self.IptPath.text()
        method = self.CmbAI.currentText()
        SLC.initAI(model, method)
        thd = threading.Thread(target=self.threadLoadAI)
        thd.start()
        return

    def threadLoadAI(self):
        fail = False
        while not fail:
            time.sleep(1)
            status = SLC.getAIStatus()
            if status == "Failed":
                self.TxtAIHint.setText("加载模型失败。")
                break
            elif status == "Idle":
                self.TxtAIHint.setText("加载模型成功。")
                break
        return

    def onClickLabelList(self):
        c = self.QListLabel.currentRow()
        if 0 <= c <= len(SLC.Shell.ItemLabel) - 1:
            item: LabelItem = SLC.Shell.ItemLabel[c]
        else:
            item: LabelItem = SLC.Shell.ItemLabel[-1]
        self.LblCrt.setText("当前：" + item.LabelIndex.text())
        return

    def onClickImageList(self):
        index = int(self.QListImage.currentItem().text())
        SLC.Shell.showImage(index, True)
        return

    def onAddLabel(self):
        SLC.addLabel()
        self.loadLabels()
        return

    def onDelLabel(self):
        index = SLC.Shell.getCrtLabelIndex()
        SLC.delLabel(index)
        self.loadLabels()
        return

    def loadLabels(self, opt=None):
        self.QListLabel.clear()
        SLC.Shell.ItemLabel.clear()

        if opt is None:
            opt = SLC.Data["Class"]
        for index, label in opt.items():
            item = qtw.QListWidgetItem(self.QListLabel)
            widget = LabelItem(
                parent=self,
                index=int(index),
                label=label,
                color=SLC.getColor(int(index)),
                item=item,
            )
            self.QListLabel.setItemWidget(item, widget)
            self.QListLabel.addItem(item)
            SLC.Shell.ItemLabel.append(widget)
        for box in SLC.Shell.ListBox:
            if box.FlagUsed:
                color = SLC.getColor(box.Index)
                if color is not None:
                    box.setColor(color)

        self.onClickLabelList()
        return

    def loadImage(self):
        self.QListImage.clear()
        for image in os.listdir(f"{SLC.VideoFolder}/images"):
            if "jpg" in image:
                item = qtw.QListWidgetItem(
                    image[: image.index(".")], self.QListImage)
                self.QListImage.addItem(item)
        return

    def loadBox(self):
        self.QListBox.clear()
        for box in SLC.Shell.ListBox:
            if box.FlagUsed:

                item = qtw.QListWidgetItem(
                    SLC.getLabel(box.Index), self.QListBox)
                self.QListBox.addItem(item)
        return

    def onClip(self):
        x = SLC.Shell.Frame.HandClip1.geometry().x()
        y = SLC.Shell.Frame.HandClip1.geometry().y()
        rect = SLC.cvtoImageRect(
            x, y, int(self.InputWidth.text()), int(self.InputHeight.text())
        )
        SLC.Data["Clip"] = [*rect]
        SLC.Shell.showImage()
        SLC.Shell.changeBack("Unsaved")
        return

    def addTrackItem(self, bid, index, roi):
        color = SLC.getColor(index)
        item = qtw.QListWidgetItem(self.QListTracker)
        start = SLC.Video.Index
        widget = TrackItem(
            parent=self,
            index=index,
            bid=bid,
            color=color,
            method=SLC.TrackerMethod,
            start=start,
            item=item,
        )
        self.QListTracker.setItemWidget(item, widget)
        self.QListTracker.addItem(item)
        SLC.Shell.ItemTracker[bid] = widget
        SLC.createTracker(tid=bid, method=SLC.TrackerMethod, roi=roi)
        return

    pass

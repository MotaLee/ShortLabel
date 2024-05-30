from PyQt6.QtGui import QMouseEvent
import PyQt6.QtWidgets as qtw
import PyQt6.QtCore as qtc

from . import getCore

SLC = getCore()


class LabelItem(qtw.QWidget):
    def __init__(self, **kw):
        """kw need: parent, label, color."""

        super().__init__(kw.get("parent"))

        self.Index = kw.get("index")
        self.Label = kw.get("label")
        self.Item = kw.get("item")
        self.Color = kw.get("color")

        self.Item.setSizeHint(qtc.QSize(0, 30))

        self.setMinimumSize(120, 50)

        self.LabelIndex = qtw.QLabel(str(self.Index), self)
        self.LabelIndex.setGeometry(0, 0, 20, 20)
        self.LabelName = qtw.QPushButton(self.Label, self)
        self.LabelName.setGeometry(20, 0, 80, 20)
        self.EditLabel = qtw.QLineEdit(self)
        self.EditLabel.setGeometry(20, 0, 80, 20)
        self.EditLabel.hide()
        self.LabelColor = qtw.QLabel(self)
        self.LabelColor.setGeometry(110, 0, 20, 20)

        stl = f"QLabel{{background-color:{self.Color};}}"
        self.LabelColor.setStyleSheet(stl)

        self.LabelName.clicked.connect(self.onEditLabel)
        self.EditLabel.editingFinished.connect(self.onFinish)
        return

    def onEditLabel(self):
        self.EditLabel.setText(self.LabelName.text())
        self.LabelName.hide()
        self.EditLabel.show()
        return

    def onFinish(self):
        v = self.EditLabel.text()
        self.LabelName.setText(v)
        self.EditLabel.hide()
        self.LabelName.show()
        SLC.editLabel(int(self.LabelIndex.text()), v)
        return

    pass


class TrackItem(qtw.QWidget):
    def __init__(self, **kw):
        """kw need:
        - parent,
        - bid,
        - index,
        - label,
        - method,
        - item,
        - start,
        - color."""

        super().__init__(kw.get("parent"))

        self.FlagEnable = True

        if "item" in kw:
            self.Item = kw.get("item")
        self.Item.setSizeHint(qtc.QSize(0, 30))

        self.setMinimumSize(150, 50)

        self.BtnEna = qtw.QCheckBox(self)
        self.BtnEna.setChecked(True)
        self.BtnEna.setGeometry(0, 0, 20, 20)

        self.TxtBid = qtw.QLabel(self)
        self.TxtBid.setGeometry(20, 0, 20, 20)

        self.BtnName = qtw.QPushButton(self)
        self.BtnName.setGeometry(40, 0, 80, 20)
        self.EditName = qtw.QLineEdit(self)
        self.EditName.setGeometry(40, 0, 80, 20)
        self.EditName.hide()

        self.ImgColor = qtw.QLabel(self)
        self.ImgColor.setGeometry(120, 0, 20, 20)

        # self.LabelInfo = qtw.QLabel(f"{self.Index}/{self.Method}", self)
        # self.LabelInfo.setGeometry(140, 0, 80, 20)

        self.setTrackItem(**kw)

        self.BtnEna.checkStateChanged.connect(self.onEnable)
        self.BtnName.clicked.connect(self.onEditName)
        self.EditName.editingFinished.connect(self.onFinish)
        return

    def setTrackItem(self, **kw):
        if "bid" in kw:
            self.BID = int(kw["bid"])
            self.TxtBid.setText(str(self.BID))
        if "index" in kw:
            self.Index = kw.get("index")

        if "method" in kw:
            self.Method = kw.get("method")
        if "color" in kw:
            self.Color = kw.get("color")
            stl = f"background-color:{self.Color};"
            self.ImgColor.setStyleSheet(stl)
        # self.Start = kw.get("start")
        if "name" in kw:
            self.Name = kw.get("name")
        else:
            self.Name = f"T: {SLC.getLabel(self.Index)}"
        self.BtnName.setText(self.Name)

        return

    def onEditName(self):
        self.EditName.setText(self.BtnName.text())
        self.BtnName.hide()
        self.EditName.show()
        return

    def onFinish(self):
        v = self.EditName.text()
        self.BtnName.setText(v)
        self.EditName.hide()
        self.BtnName.show()
        return

    def mouseReleaseEvent(self, a0: QMouseEvent):
        SLS = SLC.Shell
        SLS.selectBox(self.BID, "Tracker")
        return super().mouseReleaseEvent(a0)

    def onEnable(self):
        from .gui import LabelBox

        enable = self.BtnEna.isChecked()
        box: LabelBox = SLC.Shell.ListTrack[self.BID]
        if enable:
            self.FlagEnable = True
            SLC.Shell.selectBox(self.BID, "Track")
            box.show()
            SLC.enableTracker(self.BID, True)
        else:
            self.FlagEnable = False
            box.select(False)
            box.hide()
            SLC.enableTracker(self.BID, False)
        return

    pass

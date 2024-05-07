from PyQt6.QtGui import QMouseEvent
import PyQt6.QtWidgets as qtw
import PyQt6.QtCore as qtc

from . import getCore

TLC = getCore()


class LabelItem(qtw.QWidget):
    def __init__(self, **kw):
        """kw need: parent, label, color."""
        parent = kw.get("parent")
        super().__init__(parent)
        # from VTL import TrackLabel

        self.Label = kw.get("label")
        self.Item = kw.get("item")
        self.Item.setSizeHint(qtc.QSize(0, 30))

        self.setMinimumSize(120, 50)
        # self.VTLC: TrackLabel = kw.get("vtlc")
        self.LabelIndex = qtw.QLabel(str(self.Label), self)
        self.LabelIndex.setGeometry(0, 0, 20, 20)
        self.LabelName = qtw.QPushButton(kw.get("name"), self)
        self.LabelName.setGeometry(20, 0, 80, 20)
        self.EditLabel = qtw.QLineEdit(self)
        self.EditLabel.setGeometry(20, 0, 80, 20)
        self.EditLabel.hide()
        self.LabelColor = qtw.QLabel(self)
        self.LabelColor.setGeometry(110, 0, 20, 20)
        self.Color = kw.get("color")
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
        from . import getCore

        TLC = getCore()
        v = self.EditLabel.text()
        self.LabelName.setText(v)
        self.EditLabel.hide()
        self.LabelName.show()
        TLC.editLabel(int(self.LabelIndex.text()), v)
        return

    pass


class TrackItem(qtw.QWidget):
    def __init__(self, **kw):
        """kw need:
        - parent,
        - bid,
        - method,
        - item,
        - start,
        - label,
        - color."""

        super().__init__(kw.get("parent"))
        from App import TLWindow

        self.Win: TLWindow = self.parent().parent()
        self.BID = kw.get("bid")
        self.Label = kw.get("label")
        self.Method = kw.get("method")
        self.Color = kw.get("color")
        self.Start = kw.get("start")
        self.FlagEnable = True
        self.Item = kw.get("item")
        self.Item.setSizeHint(qtc.QSize(0, 30))

        self.setMinimumSize(150, 50)
        self.BtnEna = qtw.QCheckBox(self)
        self.BtnEna.setChecked(True)
        self.BtnEna.setGeometry(0, 0, 20, 20)
        self.LabelBid = qtw.QLabel(str(self.BID), self)
        self.LabelBid.setGeometry(20, 0, 20, 20)

        self.LabelName = qtw.QPushButton(kw.get("name"), self)
        self.LabelName.setGeometry(40, 0, 80, 20)

        self.EditName = qtw.QLineEdit(self)
        self.EditName.setGeometry(40, 0, 80, 20)
        self.EditName.hide()

        self.LabelColor = qtw.QLabel(self)
        self.LabelColor.setGeometry(120, 0, 20, 20)
        stl = f"QLabel{{background-color:{self.Color};}}"
        self.LabelColor.setStyleSheet(stl)

        self.LabelInfo = qtw.QLabel(f"{self.Label}/{self.Method}/{self.Start}", self)
        self.LabelInfo.setGeometry(140, 0, 80, 20)

        self.BtnEna.checkStateChanged.connect(self.onEnable)
        self.LabelName.clicked.connect(self.onEditName)
        self.EditName.editingFinished.connect(self.onFinish)
        return

    def onEditName(self):
        self.EditName.setText(self.LabelName.text())
        self.LabelName.hide()
        self.EditName.show()
        return

    def onFinish(self):
        v = self.EditName.text()
        self.LabelName.setText(v)
        self.EditName.hide()
        self.LabelName.show()
        return

    def mouseReleaseEvent(self, a0: QMouseEvent):
        self.Win.selectBox(self.BID, "Tracker")
        return super().mouseReleaseEvent(a0)

    def onEnable(self):
        from .gui import LabelBox

        enable = self.BtnEna.isChecked()
        box: LabelBox = self.Win.Frame.ListTrack[self.BID]
        if enable:
            box.select(True)
            box.show()
            TLC.enableTracker(self.BID, True)
        else:
            box.select(False)
            box.hide()
            TLC.enableTracker(self.BID, False)
        return

    pass

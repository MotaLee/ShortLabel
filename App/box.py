import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc

import functools as ft

from . import getCore

SLC = getCore()


class LabelBox(qtw.QLabel):
    def __init__(self, parent, bid, box_type="Label"):
        super().__init__(parent)
        self.BID = bid
        self.Color = ""

        self.FlagSelected = False
        self.FlagDrag = False
        self.FlagUsed = False
        self.FlagPressed = False
        self.FlagIn = False

        self.Pos = None
        self.Index = -1
        self.BoxType = box_type
        self.SX = -1
        self.SY = -1

        self.TxtLabel = qtw.QLabel(self)
        self.TxtLabel.setGeometry(0, 0, 50, 15)

        self.Handle = qtw.QLabel(self)
        self.Handle.mousePressEvent = self.onPressHandle
        self.Handle.mouseReleaseEvent = self.onReleaseHandle
        self.Handle.mouseMoveEvent = self.onDragHandle
        self.Handle.hide()

        self.setContextMenuPolicy(qtc.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onMenu)

        self.hide()
        return

    def useBox(self, x, y, w, h, color=None, index=None):
        if color is None:
            color = self.Color
        if index is None:
            index = self.Index

        self.Index = index
        self.Color = color
        self.setColor(color)
        self.setGeometry(x, y, w, h)
        self.FlagUsed = True
        self.TxtLabel.setText(SLC.getLabel(index))
        self.Handle.setStyleSheet(f"background-color:{color};")
        self.TxtLabel.setStyleSheet(f"background-color:{color};color:#eee;")
        self.setMouseTracking(True)
        self.show()
        return

    def setColor(self, color):
        self.Color = color
        line = "solid" if self.BoxType == "Label" else "dashed"
        self.setStyleSheet(
            r"QLabel{"
            f"border:2px {line} {color};"
            "background-color:rgba(0,0,0,0)"
            "}"
        )
        self.Handle.setStyleSheet(f"background-color:{color};")
        self.TxtLabel.setStyleSheet(f"background-color:{color};")
        return

    def getRect(self):
        rect = [
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width(),
            self.geometry().height(),
        ]
        return rect

    # 本体事件。
    def mousePressEvent(self, ev: qtg.QMouseEvent):
        SLS = SLC.Shell
        self.FlagPressed = True
        self.Pos = ev.pos()
        if self.FlagIn:
            return

        if self.FlagSelected:
            # self.select(False)
            pass
        else:
            self.Pos = ev.pos()
            self.FlagIn = True
            SLS.selectBox(self.BID, self.BoxType)
        return

    def mouseReleaseEvent(self, ev: qtg.QMouseEvent):
        self.FlagPressed = False
        if self.BoxType == "Track":
            rect = SLC.cvtoImageRect(*self.getRect())
            SLC.createTracker(tid=self.BID, method=SLC.TrackerMethod, roi=rect)
        return

    def mouseMoveEvent(self, ev: qtg.QMouseEvent):
        SLS = SLC.Shell
        if self.FlagPressed:
            pos = ev.pos()
            x = self.pos().x() - self.Pos.x() + pos.x()
            y = self.pos().y() - self.Pos.y() + pos.y()
            self.move(x, y)
            if self.BoxType == "Label":
                SLS.changeBack("Unsaved")

        mx = ev.pos().x()
        my = ev.pos().y()
        w = self.width()
        h = self.height()
        if mx > w / 2 and my > h / 2:
            self.Handle.setGeometry(w - 20, h - 20, 20, 20)
            self.Handle.show()
        else:
            self.Handle.hide()
        return

    def leaveEvent(self, a0: qtc.QEvent):
        self.FlagPressed = False
        self.FlagIn = False
        self.FlagDrag = False
        self.Handle.hide()
        return

    # 手柄事件。
    def onPressHandle(self, ev: qtg.QMouseEvent):
        self.FlagDrag = True
        self.SX = ev.pos().x()
        self.SY = ev.pos().y()
        return

    def onReleaseHandle(self, ev):
        self.FlagDrag = False

        if self.BoxType == "Track":
            rect = SLC.cvtoImageRect(*self.getRect())
            SLC.createTracker(tid=self.BID, method=SLC.TrackerMethod, roi=rect)
        return

    def onDragHandle(self, ev: qtg.QMouseEvent):
        SLS = SLC.Shell
        if self.FlagDrag:
            sx = ev.pos().x()
            sy = ev.pos().y()
            x = self.geometry().x()
            y = self.geometry().y()
            w = self.geometry().width() + sx - self.SX
            h = self.geometry().height() + sy - self.SY
            self.Handle.setGeometry(w - 20, h - 20, 20, 20)
            self.setGeometry(x, y, w, h)
            SLS.changeBack("Unsaved")
        return

    def select(self, flag=True):
        self.FlagSelected = flag
        line = "solid" if self.BoxType == "Label" else "dashed"
        t = 3 if flag else 2
        a = 50 if flag else 0
        self.setStyleSheet(
            "QLabel{"
            f"border:{t}px {line} {self.Color};"
            f"background-color:rgba(0,0,0,{a})"
            "}"
        )
        return

    def onMenu(self):
        self.Menu = qtw.QMenu(self)

        for index, label in SLC.Data["Class"].items():
            act = qtg.QAction(f"{index}:{label}", self)
            func = ft.partial(self.setIndex, int(index))
            act.triggered.connect(func)
            self.Menu.addAction(act)

        self.Menu.popup(qtg.QCursor.pos())
        return

    def setIndex(self, index):
        SLS = SLC.Shell
        self.Index = index
        color = SLC.getColor(index)
        self.setColor(color)
        self.select(True)
        self.TxtLabel.setText(SLC.getLabel(self.Index))
        if self.BoxType == "Label":
            SLS.changeBack("Unsaved")
        else:
            SLC.Shell.ItemTracker[self.BID].setTrackItem(
                color=color,
                index=self.Index,
            )

        return

    def hide(self):
        self.FlagSelected = False
        return super().hide()

    pass

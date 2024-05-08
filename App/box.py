import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc

import functools as ft

from . import getCore

VTLC = getCore()


class LabelBox(qtw.QLabel):
    def __init__(self, parent, bid, box_type="Label"):
        super().__init__(parent)
        from . import TLWindow

        self.Win: TLWindow = parent.parent().parent()
        self.BID = bid
        self.Color = ""
        self.FlagSelected = False
        self.FlagDrag = False
        self.FlagUsed = False
        self.FlagPressed = False
        self.FlagIn = False
        self.Pos = None
        self.Label = -1
        self.BoxType = box_type
        self.SX = -1
        self.SY = -1

        self.Handle = qtw.QLabel(self)
        self.Handle.mousePressEvent = self.onPressHandle
        self.Handle.mouseReleaseEvent = self.onReleaseHandle
        self.Handle.mouseMoveEvent = self.onDragHandle
        self.Handle.hide()

        self.setContextMenuPolicy(qtc.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onMenu)

        self.hide()
        return

    def useBox(self, x, y, w, h, color=None, label=None):
        if color is None:
            color = self.Color
        if label is None:
            label = self.Label
        self.Label = label
        self.Color = color
        self.setColor(color)
        self.setGeometry(x, y, w, h)
        self.FlagUsed = True
        self.Handle.setStyleSheet(f"QLabel{{background-color:{color};}}")
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
        self.Handle.setStyleSheet(f"QLabel{{background-color:{color};}}")
        return

    def mousePressEvent(self, ev: qtg.QMouseEvent):
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
            self.Win.selectBox(self.BID, self.BoxType)
        return

    def mouseReleaseEvent(self, ev: qtg.QMouseEvent):
        self.FlagPressed = False
        return

    def mouseMoveEvent(self, ev: qtg.QMouseEvent):
        if self.FlagPressed:
            pos = ev.pos()
            x = self.pos().x() - self.Pos.x() + pos.x()
            y = self.pos().y() - self.Pos.y() + pos.y()
            self.move(x, y)
            if self.BoxType == "Label":
                self.parent().changeBack("Unsaved")

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

    def onPressHandle(self, ev: qtg.QMouseEvent):
        self.FlagDrag = True
        self.SX = ev.pos().x()
        self.SY = ev.pos().y()
        return

    def onReleaseHandle(self, ev):
        self.FlagDrag = False
        return

    def onDragHandle(self, ev: qtg.QMouseEvent):
        if self.FlagDrag:
            sx = ev.pos().x()
            sy = ev.pos().y()
            x = self.geometry().x()
            y = self.geometry().y()
            w = self.geometry().width() + sx - self.SX
            h = self.geometry().height() + sy - self.SY
            self.Handle.setGeometry(w - 20, h - 20, 20, 20)
            self.setGeometry(x, y, w, h)
            self.Win.Frame.changeBack("Unsaved")
        return

    def leaveEvent(self, a0: qtc.QEvent):
        self.FlagPressed = False
        self.FlagIn = False
        self.FlagDrag = False
        self.Handle.hide()
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

    def getBoxRect(self, f=True):
        x = self.pos().x()
        y = self.pos().y()
        w = self.geometry().width()
        h = self.geometry().height()
        if f:
            if VTLC.FlagWidth:
                fx = (x + w / 2) / VTLC.ScaledWidth
                fy = (
                    y - (VTLC.FrameHeight - VTLC.ScaledHeight) / 2 + h / 2
                ) / VTLC.ScaledHeight
            else:
                fx = (
                    x - (VTLC.FrameWidth - VTLC.ScaledWidth) / 2 + w / 2
                ) / VTLC.ScaledWidth
                fy = (y + h / 2) / VTLC.ScaledHeight
            fw = w / VTLC.ScaledWidth
            fh = h / VTLC.ScaledHeight
        else:
            fx = x
            fy = y
            fw = w
            fh = h
        return fx, fy, fw, fh

    def onMenu(self):
        self.Menu = qtw.QMenu(self)

        l = len(VTLC.Option["ClassLabel"])
        for i in range(l):
            label = VTLC.Option["ClassLabel"][i]
            name = VTLC.Option["ClassName"][i]
            act = qtg.QAction(f"{label}:{name}", self)
            func = ft.partial(self.setLabel, label)
            act.triggered.connect(func)
            self.Menu.addAction(act)

        self.Menu.popup(qtg.QCursor.pos())
        return

    def setLabel(self, label):
        self.Label = label
        color = self.Win.getColorByLabel(label)
        self.setColor(color)
        self.select(True)
        self.Win.Frame.changeBack("Unsaved")
        return

    def hide(self):
        self.FlagSelected = False
        return super().hide()

    pass

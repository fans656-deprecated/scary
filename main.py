from animation import Engine
from server import thread as server_thread
from f6.pyside import get_hwnd

from PySide.QtCore import *
from PySide.QtGui import *
import win32api
import win32con

import json
import time

class Widget(QLabel):

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # transparent for input
        # http://stackoverflow.com/questions/987019/qt-top-level-widget-with-keyboard-and-mouse-event-transparency
        hwnd = get_hwnd(self)
        styles = win32api.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               styles | win32con.WS_EX_TRANSPARENT)

        cmds = config.get('commands', [])
        desktop_size = self.desktop_size = QDesktopWidget().size()
        self.engine = engine = Engine(cmds, desktop_size)

        timer = self.timer = QTimer(self)
        timer.timeout.connect(self.step)
        timer.start(config.get('step_interval', 50))

        server_thread.received.connect(self.on_received)
        server_thread.start()

    def step(self):
        self.engine.update()
        if self.engine.dirty:
            self.setPixmap(self.engine.pixmap)
        if self.engine.finished:
            server_thread.terminate()
            exit()

    def on_received(self, b):
        if b.type == 'execute':
            cmd = b.cmd
            if ';' in cmd:
                cmds = cmd.split(';')
                self.engine = self.engine.replace(cmds)
            else:
                self.engine.execute(b.cmd)
        elif b.type == 'load':
            try:
                cmds = config['predefined_commands'][b.name]
            except KeyError:
                cmds = []
            if cmds:
                self.engine = self.engine.replace(cmds)
            else:
                self.engine.execute('alpha 0 forever')
        elif b.type == 'reset':
            cmds = config.get('commands', [])
            self.engine = self.engine.replace(cmds)

with open('config.json') as f:
    config = json.load(f)

app = QApplication([])
w = Widget()
w.showFullScreen()
app.exec_()

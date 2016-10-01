from f6 import bunch

from PySide.QtCore import *
from PySide.QtGui import *
import requests

import json
import time
import threading

#server = 'http://10.105.41.77/'
server = 'http://localhost/'

with open('config.json') as f:
    config = json.load(f)

class RequestThread(QThread):

    def __init__(self):
        super(RequestThread, self).__init__()

    def get(self, b):
        requests.get(*b.args, **b.kwargs)

class Widget(QDialog):

    get_signal = Signal(object)

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        names = config['predefined_commands'].keys()
        names = ['None'] + names

        lts = []
        lt = QHBoxLayout()
        for name in names:
            button = QPushButton(name)
            button.name = name
            button.clicked.connect(self.on_load_img)
            lt.addWidget(button)
        lts.append(lt)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setSingleStep(5)
        slider.setPageStep(5)
        slider.valueChanged.connect(self.change_alpha)
        lt = QHBoxLayout()
        lt.addWidget(QLabel('Alpha'))
        lt.addWidget(slider)
        lts.insert(0, lt)

        lt = QVBoxLayout()
        for llt in lts:
            lt.addLayout(llt)

        self.setLayout(lt)
        self.request_thread = request_thread
        self.get_signal.connect(self.request_thread.get, Qt.QueuedConnection)
        self.request_thread.start()

        self.setWindowTitle('Scary Controller')

    def on_load_img(self):
        button = self.sender()
        self.get(server + 'load', params={
            'name': button.name
        })

    def change_alpha(self, val):
        self.get(server + 'execute', params={
            'cmd': 'alpha {} forever'.format(val)
        })

    def get(self, *args, **kwargs):
        self.get_signal.emit(bunch(args=args, kwargs=kwargs))

request_thread = RequestThread()
request_thread.moveToThread(request_thread)
app = QApplication([])
w = Widget()
w.show()
app.exec_()
request_thread.quit()
request_thread.wait()

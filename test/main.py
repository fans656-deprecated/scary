from server import thread

from PySide.QtCore import *
from PySide.QtGui import *

class Widget(QDialog):

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        thread.start()

app = QApplication([])
w = Widget()
w.show()
app.exec_()

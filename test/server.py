from flask import *
from PySide.QtCore import *
from PySide.QtGui import *

app = Flask(__name__)

class Thread(QThread):

    def run(self):
        app.run()

thread = Thread()

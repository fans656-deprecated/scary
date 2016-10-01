from f6 import bunch

from flask import *
from PySide.QtCore import *
from PySide.QtGui import *

app = Flask(__name__)

@app.route('/execute')
def execute():
    cmd = request.args.get('cmd', None)
    if cmd:
        thread.received.emit(bunch(type='execute', cmd=cmd))
    return 'execute: {}'.format(cmd)

@app.route('/load')
def load():
    name = request.args.get('name', None)
    if name:
        thread.received.emit(bunch(type='load', name=name))
    return 'load: {}'.format(name)

@app.route('/reset')
def reset():
    thread.received.emit(bunch(type='reset'))
    return 'ok, will reset to the default config'

class Thread(QThread):

    received = Signal(object)

    def run(self):
        app.run(host='0.0.0.0', port=80, threaded=True)

thread = Thread()

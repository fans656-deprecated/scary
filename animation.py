from f6 import bunch

from PySide.QtCore import *
from PySide.QtGui import *

import json
import time
import os

class UnknownCommand(Exception): pass
class NextCommand(Exception): pass

class Engine(object):

    def __init__(self, cmds, size=None):
        self.cmds = cmds
        self.cmd = None
        self.i = 0
        self.base_pixmap = None
        self.pixmap = None
        self.size = size
        self.dirty = False
        self.finished = False

        print 'Engine size: {}'.format(self.size)

    def replace(self, cmds):
        engine = Engine(cmds, self.size)
        engine.base_pixmap = self.base_pixmap
        engine.pixmap = self.pixmap
        return engine

    def update(self):
        self.dirty = False
        while True:
            cmd = self.parse()
            try:
                if cmd.type == 'alpha':
                    self.cmd_alpha(cmd)
                elif cmd.type == 'load':
                    self.cmd_load(cmd)
                elif cmd.type == 'repeat':
                    self.repeat_cmd = cmd
                    raise NextCommand()
                elif cmd.type == 'end repeat':
                    cmd = self.repeat_cmd
                    cmd.countdown -= 1
                    if cmd.countdown > 0:
                        self.i = cmd.i
                    raise NextCommand()
                elif cmd.type == 'exit':
                    self.finished = True
            except NextCommand:
                self.cmd = None
                continue
            break

    def execute(self, cmd):
        self.cmd = self._parse(cmd)

    def cmd_alpha(self, cmd):
        elapsed = time.time() - cmd.time
        if elapsed > cmd.duration:
            raise NextCommand()
        if cmd.duration > 0:
            alpha_range = cmd.end - cmd.beg
            ratio = elapsed / cmd.duration
            alpha = cmd.beg + alpha_range * ratio
        else:
            alpha = cmd.beg
        alpha /= 100.0
        if alpha != cmd.saved_alpha:
            cmd.saved_alpha = alpha
            self.draw(alpha)
            self.dirty = True

    def cmd_load(self, cmd):
        fpath = cmd.fpath
        print 'load "{}" {}'.format(
            fpath,
            "exists" if os.path.exists(fpath) else "not exists"
        )
        pixmap = QPixmap(fpath)
        if not pixmap:
            print "but pixmap load failed"
        if self.size:
            pixmap = pixmap.scaled(self.size)
        else:
            if pixmap.width() > pixmap.height():
                pixmap = pixmap.scaledToWidth(640)
            else:
                pixmap = pixmap.scaledToHeight(480)
        self.pixmap = self.base_pixmap = pixmap
        self.dirty = True
        raise NextCommand()

    def draw(self, alpha):
        img = QImage(self.base_pixmap.size(),
                     QImage.Format_ARGB32_Premultiplied)
        if self.base_pixmap:
            p = QPainter()
            p.begin(img)
            p.setOpacity(alpha)
            p.drawPixmap(0, 0, self.base_pixmap)
            p.end()
        self.pixmap = QPixmap.fromImage(img)

    def parse(self):
        while not self.cmd:
            self.cmd = self._parse(self.next_cmd())
        return self.cmd

    def _parse(self, cmd):
        try:
            tokens = cmd.strip().split()
            head = tokens[0]
            if head == 'alpha':
                result = self.parse_alpha_cmd(tokens)
            elif head == 'repeat':
                t = tokens[-1]
                if t == 'forever':
                    countdown = float('inf')
                else:
                    countdown = int(t)
                result = bunch(type='repeat', countdown=countdown, i=self.i)
            elif head == 'end' and tokens[-1] == 'repeat':
                result = bunch(type='end repeat')
            elif head == 'load':
                fpath = ' '.join(tokens[1:])
                result = bunch(type='load', fpath=fpath)
            elif head == 'exit':
                result = bunch(type='exit')
            else:
                return None
        except IndexError:
            return None
        self.parsed = True
        return result

    def parse_alpha_cmd(self, tokens):
        tokens = list(reversed(tokens[1:]))
        try:
            # beg
            beg = int(tokens.pop())
            # end
            if tokens[-1] == 'to':
                tokens.pop()
                end = int(tokens.pop())
            else:
                end = beg
            # duration
            if tokens:
                t = tokens.pop()
                if t == 'forever':
                    duration = float('inf')
                elif t.endswith('s'):
                    duration = float(t[:-1])
            else:
                duration = 0
        except IndexError:
            pass
        return bunch(type='alpha', beg=beg, end=end, duration=duration,
                     saved_alpha=None, time=time.time())

    def next_cmd(self):
        if self.i >= len(self.cmds):
            return ''
        cmd = self.cmds[self.i]
        self.i += 1
        return cmd

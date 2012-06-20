#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from PySide.QtGui import QSlider, QLabel, QWidget

from async_application import AsyncApplication


# NOTE!!!!
#
# This is currently hacked together just to validate the ideas of the
# async message passing, this is certainly not production quality code.


class ClientWidget(object):

    def __init__(self, msg_id):
        self.__msg_id = msg_id
        self.widget = None

    def send(self, msg, ctxt):
        app = AsyncApplication.instance()
        if app is None:
            return
        app.recv_message(self.__msg_id, msg, ctxt)

    def recv(self, msg, ctxt):
        handler_name = 'receive_' + msg
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(ctxt)
        return NotImplemented

    def create(self, parent):
        raise NotImplementedError


class QtSlider(ClientWidget):

    def create(self, parent):
        self.widget = QSlider(parent)
        self.widget.valueChanged.connect(self.on_value_changed)
        self.widget.show()
        self.widget.move(100, 100)

    def on_value_changed(self):
        self.send('update_value', dict(value=self.widget.value()))

    def receive_set_value(self, ctxt):
        self.widget.setValue(ctxt['value'])


class QtLabel(ClientWidget):

    def create(self, parent):
        self.widget = QLabel(parent)
        self.widget.show()
        self.widget.move(20, 20)
        self.widget.resize(50, 20)

    def receive_set_label(self, ctxt):
        self.widget.setText(ctxt['label'])


class QtContainer(ClientWidget):

    def create(self, parent):
        self.widget = QWidget(parent)
        self.widget.show()

    def receive_show(self, ctxt):
        self.widget.show()


CLIENTS = {
    'Slider': QtSlider,
    'Label': QtLabel,
    'Container': QtContainer,
}


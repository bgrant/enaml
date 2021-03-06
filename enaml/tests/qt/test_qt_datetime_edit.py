#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime
from uuid import uuid4

from enaml.qt.qt import QtCore
from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_datetime_edit import QtDatetimeEdit
from enaml.qt.qt_local_pipe import QtLocalPipe

# Workarounds for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdatetime_to_python = QtCore.QDateTime.toPython
except AttributeError: # pragma: no cover
    qdatetime_to_python = QtCore.QDateTime.toPyDateTime

class TestQtDatetimeEdit(object):
    """ Unit tests for the QtDatetimeEdit

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
    
    def setUp(self):
        """ Set up the widget for testing

        """
        self.datetime_edit = QtDatetimeEdit(None, uuid4().hex,
                                            QtLocalPipe(uuid4))
        self.datetime_edit.create()

    def test_set_datetime(self):
        """ Test the QtDatetimeEdit's set_datetime command

        """
        date_time = datetime.datetime(2012,6,22,0,0,0,0)
        self.datetime_edit.recv_message({'action':'set-datetime',
                                         'datetime':str(date_time)})
        widget_date_time = qdatetime_to_python(self.datetime_edit.widget.dateTime())
        assert widget_date_time == date_time

    def test_set_min_datetime(self):
        """ Test the QtDatetimeEdit's set_min_datetime command

        """
        min_date_time = datetime.datetime(1752,9,14, 0, 0, 0, 0)
        self.datetime_edit.recv_message({'action':'set-minimum',
                                         'minimum':str(min_date_time)})
        widget_min_date_time = qdatetime_to_python(
            self.datetime_edit.widget.minimumDateTime())
        assert widget_min_date_time == min_date_time

    def test_set_max_datetime(self):
        """ Test the QtDatetimeEdit's set_max_datetime command

        """
        max_date_time = datetime.datetime(7999, 12, 31, 23, 59, 59, 999000)
        self.datetime_edit.recv_message({'action':'set-maximum',
                                         'maximum':str(max_date_time)})
        widget_max_date_time = qdatetime_to_python(
            self.datetime_edit.widget.maximumDateTime())
        assert widget_max_date_time == max_date_time

    def test_set_datetime_format(self):
        """ Test the QtDatetimeEdit's set_datetime_format command

        """
        date_time_format = 'd M y - hh:mm:ss'
        self.datetime_edit.recv_message({'action':'set-datetime_format',
                                         'datetime_format':date_time_format})
        widget_format = self.datetime_edit.widget.displayFormat()
        assert widget_format == date_time_format

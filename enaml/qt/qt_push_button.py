#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QPushButton
from .qt_abstract_button import QtAbstractButton


class QtPushButton(QtAbstractButton):
    """ A Qt4 implementation of an Enaml PushButton.

    """
    def create(self):
        """ Create the underlying QPushButton widget.

        """
        self.widget = QPushButton(self.parent_widget)

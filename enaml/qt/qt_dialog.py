#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QDialog
from .qt.QtCore import Qt
from qt_window import QtWindow, QtWindowLayout

QT_MODALITY = {
    'application_modal' : Qt.ApplicationModal,
    'window_modal' : Qt.WindowModal,
    'non_modal' : Qt.NonModal
}

class QtDialog(QtWindow):
    """ A Qt implementation of a dialog

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QDialog(self.parent_widget)
        self.widget.setLayout(QtWindowLayout())

    def bind(self):
        """ Connect the events to the correct slots

        """
        super(QtDialog, self).bind()
        self.widget.finished.connect(self.on_closed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_modality(self, ctxt):
        """ Handle a set_modality message

        """
        modality = ctxt.get('modality')
        if modality is not None:
            self.set_modality(modality)

    def receive_accept(self, ctxt):
        """ Handle an accept message

        """
        self.accept()

    def receive_reject(self, ctxt):
        """ Handle a reject message

        """
        self.reject()

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_closed(self, qt_result):
        """ The event handler for the closed event.

        """
        if qt_result == QDialog.Accepted:
            result = 'accepted'
        else:
            result = 'rejected'

        self.send({'action':'closed','result':result})

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ Override the parent's set_visible method so that the dialog launches
        correctly with the specified modality

        """
        if visible:
            self.send({'action':'set_active','value':True})
            self.send({'action':'opened'})
            self.widget.exec_()
        else:
            self.reject()

    def set_modality(self, modality):
        """ Set the modality of the dialog window.

        """
        self.widget.setWindowModality(QT_MODALITY[modality])

    def accept(self):
        """ Accept and close the dialog

        """
        self.widget.accept()

    def reject(self):
        """ Reject and close the dialog

        """
        self.widget.reject()
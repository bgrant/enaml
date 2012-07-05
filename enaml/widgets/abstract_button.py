#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base64 import b64encode

from traits.api import Bool, Unicode, Tuple, Instance

from enaml.core.trait_types import EnamlEvent

from .constraints_widget import ConstraintsWidget
from .icon import Icon


class AbstractButton(ConstraintsWidget):
    """ A base class which provides functionality common for several
    button-like widgets.

    """
    #: The text to use as the button's label.
    text = Unicode

    #: The icon to use for the button.
    icon = Instance(Icon)

    #: The size to use for the icon.
    icon_size = Tuple

    #: Whether or not the button is checkable. The default is False.
    checkable = Bool(False)

    #: Whether a checkable button is currently checked.
    checked = Bool(False)

    #: Fired when the button is pressed then released. The payload will
    #: be the current checked state.
    clicked = EnamlEvent

    #: Fired when a checkable button is toggled. The payload will be
    #: the current checked state.
    toggled = EnamlEvent
    
    #: How strongly a component hugs it's contents' width. Buttons hug
    #: their contents' width weakly by default.
    hug_width = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Returns the creation attributes for an abstract button.

        """
        super_attrs = super(AbstractButton, self).creation_attributes()
        super_attrs['text'] = self.text
        super_attrs['checkable'] = self.checkable
        super_attrs['checked'] = self.checked
        super_attrs['icon_size'] = self.icon_size
        icon = self.icon
        super_attrs['icon'] = b64encode(icon.data()) if icon else None
        return super_attrs

    def bind(self):
        """ Bind the change handlers for an abstract button.

        """
        super(AbstractButton, self).bind()
        self.publish_attributes('text', 'checkable', 'checked', 'icon_size')
        self.on_trait_change(self._send_icon, 'icon')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_event_clicked(self, payload):
        """ Handle the 'event-clicked' action from the UI widget. The 
        payload will contain the current checked state.

        """
        checked = payload['checked']
        self.set_guarded(checked=checked)
        self.clicked(checked)

    def on_message_event_toggled(self, payload):
        """ Handle the 'event-toggled' action from the UI widget. The
        payload will contain the current checked state.

        """
        checked = payload['checked']
        self.set_guarded(checked=checked)
        self.toggled(checked)

    def _send_icon(self):
        """ Send the current icon to the client widget.

        """
        icon = self.icon
        enc_data = b64encode(icon.data()) if icon else None
        self.send_message({'action': 'set-icon', 'icon': enc_data})

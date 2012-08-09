#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx


class wxSingleWidgetSizer(wx.PySizer):
    """ A custom wx Sizer for sizing a single child widget.

    There can only be one widget in this sizer at a time and it should
    be added via the .Add(...) method. Old items will be removed 
    automatically (but not destroyed).

    """
    _default_size = wx.Size(-1, -1)

    _widget = None

    def CalcMax(self):
        """ A method to compute the maximum size allowed by the sizer.

        This is not a native wx sizer method, but is included for 
        convenience.

        """
        widget = self._widget
        if not widget:
            return self._default_size
        return widget.GetMaxSize()

    def Add(self, widget):
        """ Adds the given widget to the sizer, removing the old widget
        if present. The old widget is not destroyed.

        """
        self.Clear(deleteWindows=False)
        self._widget = widget
        if widget is not None:
            res = super(wxSingleWidgetSizer, self).Add(widget)
            self.Layout()
            return res

    def CalcMin(self):
        """ Returns the minimum size for the children this sizer is 
        managing.

        """
        widget = self._widget
        if not widget:
            return self._default_size
        return widget.GetEffectiveMinSize()

    def RecalcSizes(self):
        """ Resizes the child to fit the available space of the window.

        """
        widget = self._widget
        if widget:
            widget.SetSize(self.GetSize())


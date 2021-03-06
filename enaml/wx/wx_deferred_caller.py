#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx


class wxDeferredCaller(object):
    """ A simple object which facilitates running callbacks on the main
    application thread.

    """
    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def DeferredCall(self, callback, *args, **kwargs):
        """ Execute the callback on the main gui thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute on the main thread.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to 
            the callback.

        """
        wx.CallAfter(callback, *args, **kwargs)

    def TimedCall(self, ms, callback, *args, **kwargs):
        """ Execute a callback on timer in the main gui thread.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.
            
        callback : callable
            The callable object to execute at on the timer.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to 
            the callback.

        """
        f = lambda: wx.CallLater(ms, callback, *args, **kwargs)
        wx.CallAfter(f)


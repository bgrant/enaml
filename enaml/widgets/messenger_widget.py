#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict

from traits.api import Instance, ReadOnly, Str

from enaml.async.async_application import AsyncApplication, AsyncApplicationError
from enaml.async.async_messenger import AsyncMessenger
from enaml.async.messenger_mixin import MessengerMixin
from enaml.core.base_component import BaseComponent
from enaml.utils import WeakMethod


class LoopbackContext(object):
    """ A context manager generated by a LoopbackGuard which manages
    acquiring and releasing the lock items.

    """
    def __init__(self, guard, lock_items):
        """ Initialize a LoopbackContext

        Parameters
        ----------
        guard : LoopbackGuard
            The loopback guard instance for which we will acquire the
            lock for the items.

        lock_items : iterable
            An iterable items which will be passed to the 'acquire'
            method on the loopback guard.

        """
        self._guard = guard
        self._lock_items = lock_items

    def __enter__(self):
        """ Acquire the guard lock on the lock items.

        """
        self._guard.acquire(self._lock_items)

    def __exit__(self, exc_type, exc_value, traceback):
        """ Release the guard lock on the lock items.

        """
        self._guard.release(self._lock_items)


class LoopbackGuard(object):
    """ A guard object used by the MessengerWidget to protect against
    loopback conditions while updating attributes on the component.

    Instances of this class are callable and return a guarding 
    context manager for the provided lock items.

    """
    def __init__(self):
        """ Initialize a LoopbackGuard.

        """
        self._locked = defaultdict(int)

    def __call__(self, *items):
        """ Return a context manager which will guard the given items.

        Parameters
        ----------
        *items
            The items for which to acquire the guard from within the
            returned context manager. These items must be hashable.

        Returns
        -------
        result : LoopbackContext
            A context manager which will acquire the guard for the
            provided items.

        """
        return LoopbackContext(self, items)

    def __contains__(self, item):
        """ Returns whether or not the given item is currently guarded.

        Parameters
        ----------
        item : object
            The item to check for guarded state.

        Returns
        -------
        result : bool
            True if the item is currently guarded, False otherwise.

        """
        return item in self._locked

    def acquire(self, lock_items):
        """ Acquire the guard for the given lock items.

        This method is normally called by the LoopbackContext returned
        by calling this instance. User code should not normally call
        this method directly.

        It is safe to call this method multiple times for the same
        item, provided it is paired with an equivalent number of 
        calls to release(...). The guard will be released when 
        the acquired count on the item reaches zeros.

        Parameters
        ----------
        lock_items : iterable
            An iterable of objects for which to acquire the guard. The
            items must be hashable.

        """
        for item in lock_items:
            self._locked[item] += 1

    def release(self, lock_items):
        """ Release the guard for the given lock items.

        This method is normally called by the LoopbackContext returned
        by calling this instance. User code should not normally call
        this method directly.

        It is safe to call this method multiple times for the same
        item, provided it is paired with an equivalent number of 
        calls to acquire(...). The guard will be released when 
        the acquired count on the item reaches zeros.

        Parameters
        ----------
        lock_items : iterable
            An iterable of objects for which to release the guard. The
            items must be hashable.

        """
        for item in lock_items:
            self._locked[item] -= 1
            if self._locked[item] == 0:
                del self._locked[item]


class MessengerWidget(MessengerMixin, BaseComponent):
    """ The base class of all widget classes in Enaml.

    This extends BaseComponent with the ability to send and receive
    commands to and from a target by mixing in the AsyncMessenger
    class. It aslo provides the necessary data members and methods
    required to initialize the client widget.

    """
    #: A loopback guard which can be used to prevent a loopback cycle
    #: of messages when setting attributes from within a handler.
    loopback_guard = Instance(LoopbackGuard, ())

    #: A string used to speficy the type of widget which should be 
    #: created by clients when this widget is published. The default 
    #: type is computed based on the name of the component class. This 
    #: may be overridden by users as needed to define custom behavior.
    widget_type = Str
    def _widget_type_default(self):
        return type(self).__name__
    
    #: The internal storage for the target_id property.
    _target_id = ReadOnly

    #: The internal storage for the async_pipe property.
    _async_pipe = ReadOnly

    def __new__(cls, *args, **kwargs):
        """ Create a new AsyncMessenger instance.

        New instances cannot be created unless an AsyncApplication 
        instance is available.

        Parameters
        ----------
        *args, **kwargs
            Any required position and keyword arguments to pass to the
            superclass.

        """
        app = AsyncApplication.instance()
        if app is None:
            msg = 'An async application instance must be created before '
            msg += 'creating any AsyncMessenger instances.'
            raise AsyncApplicationError(msg)
        instance = super(MessengerWidget, cls).__new__(cls, *args, **kwargs)
        app.register(instance)
        return instance

    #--------------------------------------------------------------------------
    # AsyncMessenger Interface
    #--------------------------------------------------------------------------
    def target_id():
        """ The property get/set pair for the 'target_id' attribute.

        """
        def getter(self):
            return self._target_id
        def setter(self, target_id):
            self._target_id = target_id
        return property(getter, setter)

    target_id = target_id()
    
    def async_pipe():
        """ The property get/set pair for the 'async_pipe' attribute.

        """
        def getter(self):
            return self._async_pipe
        def setter(self, pipe):
            self._async_pipe = pipe
            pipe.set_message_callback(self.target_id, WeakMethod(self.recv_message))
            pipe.set_request_callback(self.target_id, WeakMethod(self.recv_request))
        return property(getter, setter)

    async_pipe = async_pipe()

    def creation_payload(self):
        """ Returns the payload dict for the 'create' action for the
        messenger.

        Returns
        -------
        results : dict
            The creation payload dict for the messenger widget.

        """
        payload = {}
        payload['action'] = 'create'
        payload['type'] = self.widget_type
        payload['parent_id'] = self.parent_id
        payload['attributes'] = self.creation_attributes()
        return payload

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @property
    def parent_id(self):
        """ A read only property which returns the target id of the 
        parent of this messenger.

        Returns
        -------
        result : str or None
            The target id of the parent messenger, or None if the parent
            is not an instance of MessengerWidget.

        """
        parent = self.parent
        if isinstance(parent, MessengerWidget):
            return parent.target_id

    def creation_attributes(self):
        """ Returns a dictionary of attributes to initialize the state
        of the target widget when it is created. 

        This method is called by 'creation_info' when assembling the
        dictionary of initial state for creation of the client.

        This method returns a a new empty dictionary which should be 
        updated in-place by subclasses before being returned to the
        caller.

        Returns
        -------
        results : dict

        """
        return {}

    def bind(self):
        """ A method which should be called when preparing a widget for
        publishing.

        The intent of this method is to allow a widget to hook up its
        trait change notification handlers which will send messages
        to the client. The default implementation of this method is 
        a no-op, but is provided to be super() friendly. It's assumed
        that this method will only be called once by the object which
        manages the process of preparing a widget for publishing.

        """
        pass

    def publish_attributes(self, *attrs):
        """ A convenience method provided for subclasses to use to 
        publish an arbitrary number of attributes to the target widet.

        The action generated for the target message is created by 
        prefixing 'set-' to the name of the changed attribute. This
        method is not intended to meet the needs of *all* attribute
        publishing. Rather it is meant to handle the majority of 
        simple cases. More complex attributes will need to implement
        their own dispatching handlers.

        Parameters
        ----------
        *attrs
            The string names of the attributes to publish to the client.
            These attributes are expected to be simply serializable.
            More complex values should use their own dispatch handlers.

        """
        otc = self.on_trait_change
        handler = self._publish_attr_handler
        for attr in attrs:
            otc(handler, attr)

    def set_guarded(self, **attrs):
        """ A convenience method provided for subclasses to set a
        sequence of attributes from within a loopback guard.

        Parameters
        ----------
        **attrs
            The attributes which should be set on the component from
            within a loopback guard context.

        """
        with self.loopback_guard(*attrs):
            for name, value in attrs.iteritems():
                setattr(self, name, value)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _publish_attr_handler(self, name, new):
        """ A trait change handler which will send an attribute change
        message to a target by prefixe the attr name with 'set-' in 
        order to creation the action name.

        The value of the attribute is expected to be serializable.
        If the loopback guard is held for the given name, then the 
        message will no be sent (avoiding potential loopbacks).

        """
        if name not in self.loopback_guard:
            action = 'set-' + name
            payload = {'action': action, name: new}
            self.send_message(payload)


#: Registers the MessengerWidget as an instance of AsyncMessenger.
#: This is done in lieu of inheritence due to metaclass conflicts 
#: with HasTraits classes.
AsyncMessenger.register(MessengerWidget)

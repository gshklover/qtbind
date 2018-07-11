from PyQt5.Qt import pyqtSignal


class Event(list):
    """
    Signal interface similar to Qt
    """
    def connect(self, func):
        self.append(func)

    def disconnect(self, func):
        self.remove(func)

    def emit(self, *args, **kwargs):
        for func in self:
            func(*args, **kwargs)


class IPropertyChanged:
    """
    This class generates an event when a property is changed
    The event arguments are:
    prop_name - string or None when all properties are changed
    new_val - new property value
    Base interface is used for pure Python objects that do not inherit QObject.
    """
    def __init__(self):
        self._property_changed = Event()

    @property
    def property_changed(self):
        return self._property_changed


class IQObjectPropertyChanged(IPropertyChanged):
    """
    Overrides default implementation with Qt signal (offers thread safety).
    Derived classes must inherit QObject.
    """
    def __init__(self):
        super().__init__()

    property_changed = pyqtSignal(str, object)

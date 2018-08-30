from PyQt5.QtWidgets import QTextEdit

BIND_READ = 1
BIND_WRITE = 2


class SimpleLock:
    """
    Simple context lock.
    Usage example:
        with self._lock:
            ...

        if self._lock:
            continue
    """
    def __init__(self):
        self._locked = 0

    def __enter__(self):
        self._locked += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._locked -= 1
        return False

    def __bool__(self):
        return self._locked > 0


class Binding:
    """
    Binds changes to source property with target widget property.
    """
    def __init__(self,
                 source, source_prop,
                 target, target_prop,
                 flags=(BIND_READ | BIND_WRITE),
                 source_to_target=None, target_to_source=None):
        """
        Create a new binding
        :param source: source object
        :param source_prop: source property name
        :param target: target widget
        :param target_prop: target property name
        :param flags: combination of BIND_READ/BIND_WRITE
        :param source_to_target: a value converter callback source -> target
        :param target_to_source: a value converter callback target -> source
        """
        self._source = None
        self._source_prop = source_prop
        self._target = None
        self._target_prop = target_prop
        self._flags = flags
        self._source_to_target = source_to_target
        self._target_to_source = target_to_source
        self._target_has_prop = True
        self._update_lock = SimpleLock()

        self.source = source
        self.target = target

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, val):
        if self._source == val:
            return

        if self._source is not None:
            self._source.property_changed.disconnect(self._on_source_changed)

        self._source = val

        if self._source is not None:
            self._source.property_changed.connect(self._on_source_changed)

        self._sync()

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, val):
        if self._target == val:
            return

        event_name = self._target_prop + "Changed"

        if self._target is not None and self._flags & BIND_WRITE:
            getattr(self._target, event_name).disconnect(self._on_target_changed)

        self._target = val

        if self._target is not None:
            meta = self._target.metaObject()
            self._target_has_prop = False
            for i in range(meta.propertyCount()):
                prop = meta.property(i)
                if prop.name() == self._target_prop:
                    self._target_has_prop = True
                    break

        if self._target is not None and self._flags & BIND_WRITE:
            getattr(self._target, event_name).connect(self._on_target_changed)

        self._sync()

    def _on_source_changed(self, prop, value):
        """
        Called when source values changes
        """
        if prop is not None and prop != self._source_prop:
            return

        if self._source_to_target is not None:
            value = self._source_to_target(value)

        if self._target is not None:
            self._set_target_value(value)

    def _on_target_changed(self):
        """
        Called when target value changes
        """
        if self._update_lock:
            return

        if self._source is not None:
            value = self._get_target_value()
            if self._target_to_source is not None:
                value = self._target_to_source(value)
            setattr(self._source, self._source_prop, value)

    def _get_source_value(self):
        return getattr(self._source, self._source_prop)

    def _get_target_value(self):
        if isinstance(self._target, QTextEdit) and self._target_prop == 'text':
            return self._target.property('plainText')
        return self._target.property(self._target_prop)

    def _set_target_value(self, val):
        with self._update_lock:
            method = "set" + self._target_prop[0].upper() + self._target_prop[1:]
            # QT way:
            if hasattr(self._target, method):
                getattr(self._target, method)(val)
                return
            # Python way
            prop_desc = getattr(type(self._target), self._target_prop, None)
            if prop_desc is None or not hasattr(prop_desc, 'setter'):
                raise(Exception("Don't know how to assign " + self._target_prop + " on target"))
            setattr(self._target, self._target_prop, val)

    def _sync(self):
        """
        Synchronize source and target values
        """
        if self._source is None or self._target is None:
            return

        if self._flags & BIND_READ:
            self._on_source_changed(self._source_prop, self._get_source_value())
        elif self._flags & BIND_WRITE:
            self._on_target_changed(self._get_target_value())

from PyQt5.QtCore import pyqtProperty
from qtbind.qtbind import Binding, BIND_READ, BIND_WRITE


class View:
    def __init__(self, context=None):
        self._context = None
        self._bindings = []
        self.context = context

    @pyqtProperty(object)
    def context(self):
        return self._context

    @context.setter
    def context(self, val):
        if val == self._context:
            return
        old = self._context
        self._context = val
        self._update_bindings()
        self._on_context_changed(old, val)

    def bind(self, prop_name, wdg, wdg_prop, flags=(BIND_READ | BIND_WRITE), target_signal=None):
        """
        Bind context property to widget property
        :param prop_name: context property
        :param wdg: QWidget
        :param wdg_prop: property name
        """
        binding = Binding(source=self._context, source_prop=prop_name,
                          target=wdg, target_prop=wdg_prop, flags=flags,
                          target_signal=target_signal)
        self._bindings.append(binding)

    def _update_bindings(self):
        for binding in self._bindings:
            binding.source = self._context

    def _on_context_changed(self, old, new):
        """
        Called after context is changed
        :param old: old context value
        :param new: new context value
        """
        pass

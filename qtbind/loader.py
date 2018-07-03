from PyQt5.uic.Loader.loader import DynamicUILoader
from PyQt5.uic.properties import Properties
from PyQt5 import QtCore, QtGui, QtWidgets

from .qtbind import BIND_READ, BIND_WRITE
from .view import View


class CustomProperties(Properties):
    """
    Customize default parser for Properties with extension to handle <binding> constructs.
    """
    def __init__(self, factory):
        super().__init__(factory, QtCore, QtGui, QtWidgets)
        self._bindings = []

    def setProperties(self, widget, elem):
        # Lines are sunken unless the frame shadow is explicitly set.
        set_sunken = (elem.attrib.get('class') == 'Line')

        for prop in elem.findall('property'):
            prop_name = prop.attrib['name']

            if prop_name == 'frameShadow':
                set_sunken = False

            # just record the bindings - will apply later after full tree is constructed
            binding = prop.find('binding')
            if binding is not None:
                self._bindings.append((widget, prop.get('name'), binding))
                continue

            try:
                stdset = bool(int(prop.attrib['stdset']))
            except KeyError:
                stdset = True

            if not stdset:
                self._setViaSetProperty(widget, prop)
            elif hasattr(self, prop_name):
                getattr(self, prop_name)(widget, prop)
            else:
                prop_value = self.convert(prop, widget)
                if prop_value is not None:
                    getattr(widget, 'set%s%s' % (prop_name[0].upper(), prop_name[1:]))(prop_value)

        if set_sunken:
            widget.setFrameShadow(QtWidgets.QFrame.Sunken)

    def apply_bindings(self):
        """
        Apply previously collected bindings
        """
        for widget, prop_name, binding_elem in self._bindings:
            self.apply_binding(widget, prop_name, binding_elem)

    def apply_binding(self, widget, prop_name, binding_elem):
        # find widget parent that implements View
        view = widget

        while view is not None and not isinstance(view, View):
            view = view.parent()

        if view is None:
            print('Error: failed to find view for ' + str(widget) + " and property " + prop_name)
            return

        bind_path = binding_elem.attrib['path']
        bind_mode = binding_elem.get('mode', 'READ_WRITE')
        mode_to_flags = {
            'READ': BIND_READ,
            'WRITE': BIND_WRITE,
            'READ_WRITE': BIND_READ | BIND_WRITE
        }
        flags = mode_to_flags[bind_mode]

        view.bind(bind_path, widget, prop_name, flags)


class CustomUILoader(DynamicUILoader):
    def __init__(self, package):
        super().__init__(package)
        # override default implementation
        self.wprops = CustomProperties(self.factory)

    def loadUi(self, filename, toplevelInst, resource_suffix):
        res = super().loadUi(filename, toplevelInst, resource_suffix)
        self.wprops.apply_bindings()
        return res


def load_ui(uifile, baseinstance, package='', resource_suffix="_rc"):
    """
    Custom .ui file loader that supports <binding> elements for property values.
    :param uifile: .ui file path 
    :param wdg: parent object to construct 
    :param package: 
    """
    return CustomUILoader(package).loadUi(uifile, baseinstance, resource_suffix)

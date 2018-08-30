from PyQt5 import QtWidgets, QtCore, Qt
import os

from example.models.models import Group, Person
from example.viewmodels.groupviewmodel import GroupViewModel
from example.views.groupview import GroupView
from qtbind.loader import load_ui
from qtbind.view import View


class DummyModel(QtCore.QObject):

    property_changed = Qt.pyqtSignal(str, object)

    def __init__(self):
        super().__init__()
        self._comment = ''

    @property
    def name(self):
        return "Example value"

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, val):
        if val != self._comment:
            self._comment = val
            self.property_changed.emit('comment', val)


class MyWidget(QtWidgets.QWidget, View):
    def __init__(self):
        super().__init__()
        self.context = DummyModel()
        load_ui(os.path.join(os.path.dirname(__file__), 'views', 'groupview.ui'), self)


def main():
    app = QtWidgets.QApplication([])

    model = Group(
        Person(name="A", family_name="B"),
        Person(name="C", family_name="D"),
        Person(name="E", family_name="F")
    )

    vm = GroupViewModel(model)

    # explicit construction:
    view = GroupView(context=vm)
    view.show()

    # UI-loaded construction:
    ui_wdg = MyWidget()
    ui_wdg.show()

    app.exec()


main()

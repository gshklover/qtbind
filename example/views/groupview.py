from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QGridLayout, QListView, QStyledItemDelegate

from qtbind.qtbind import BIND_READ
from qtbind.view import View
from .personview import PersonView


class PersonItemDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()


class GroupView(QWidget, View):
    def __init__(self, context=None, **kwargs):
        super().__init__(**kwargs)
        #QWidget.__init__(self, **kwargs)
        #View.__init__(self, context=context)

        self._list = QListView()
        self._list.setItemDelegate(PersonItemDelegate())
        self._details = PersonView()

        self.bind("people", self._list, "model", flags=BIND_READ)
        self.bind("current", self._details, "context", flags=BIND_READ)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self._list, 0, 0)
        layout.addWidget(self._details, 0, 1, 1, 1, QtCore.Qt.AlignTop)

        self.context = context

        self._list.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, new_selection, old_selection):
        sel = new_selection.indexes()
        if len(sel) != 1:
            return
        self.context.set_current(sel[0].row())


from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QLineEdit

from qtbind.view import View


class PersonView(QWidget, View):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Name:"), 0, 0)
        layout.addWidget(QLabel("Fаmily Name:"), 1, 0)

        self._name = QLineEdit()
        self._family_name = QLineEdit()

        self.bind("name", self._name, "text")
        self.bind("family_name", self._family_name, "text")

        layout.addWidget(self._name, 0, 1)
        layout.addWidget(self._family_name, 1, 1)
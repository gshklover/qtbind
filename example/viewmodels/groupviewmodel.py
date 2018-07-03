from PyQt5.QtCore import Qt

from example.models.models import Person
from qtbind.viewmodel import ViewModel, ViewModelProperty, ListViewModel


class PersonViewModel(ViewModel):
    """
    Adds change notification to Person data-model object
    """
    def __init__(self, person):
        super().__init__(model=person)

    name = ViewModelProperty("name")
    family_name = ViewModelProperty("family_name")


class GroupViewModel(ViewModel):
    def __init__(self, group):
        super().__init__(model=group)
        self._current = None
        self._people = ListViewModel(group.people,
                                     init=[PersonViewModel(p) for p in group.people],
                                     data_delegate=self._person_delegate)

    leader = ViewModelProperty("leader")

    @property
    def name(self):
        return "Group Name"

    @property
    def people(self):
        return self._people

    @property
    def current(self):
        return self._current

    def set_current(self, index):
        self._current = self.people[index] if index >= 0 and index <= len(self.people) else None
        self.property_changed.emit('current', self._current)

    def add_new_person(self):
        person = Person()
        personvm = PersonViewModel(person)
        self._peolpe.append(personvm)
        self.model.people.append(person)
        self._current = personvm
        self.property_changed.emit('current', self._current)
        # self.property_changed.emit('people', self._people)  # shouldn't be required

    def _person_delegate(self, person, role):
        if role == Qt.DisplayRole:
            return person.family_name + ", " + person.name
        return None

class Person:
    def __init__(self, name="", family_name=""):
        self._name = name
        self.family_name = family_name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val
        print("Person.name = " + str(val))


class Group:
    def __init__(self, *people):
        self.people = list(people)
        self.leader = None

    def add_person(self, person):
        self.people.append(person)

    def remove_person(self, person):
        self.people.remove(person)

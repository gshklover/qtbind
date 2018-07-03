class Person:
    def __init__(self, name="", family_name=""):
        self.name = name
        self.family_name = family_name


class Group:
    def __init__(self, *people):
        self.people = list(people)
        self.leader = None

    def add_person(self, person):
        self.people.append(person)

    def remove_person(self, person):
        self.people.remove(person)

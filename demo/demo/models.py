from tml.strings import to_string

__autor__ = 'xepa4ep'


class User(object):
    GENDERS = MALE, FEMALE = ('male', 'female')

    name = None
    gender = None

    def __init__(self, name, gender=None):
        self.name = name
        self.gender = gender or User.MALE

    def to_dict(self):
        return {
            'name': self.name,
            'gender': self.gender}

    def __unicode__(self):
        return to_string(self.name)

class Language:
    """ A class with a bunch of class methods to aid with finding a chapter in the desired language.
    """
    def __init__(self, code, scdry=None):
        self._lang_code = code
        self._scdry = scdry

    def __eq__(self, other):
        if other in [self._lang_code, self._scdry]:
            return True
        return False

    @classmethod
    def English(cls):
        return cls('gb')

    @classmethod
    def German(cls):
        return cls('de')

    @classmethod
    def French(cls):
        return cls('fr')

    @classmethod
    def Dutch(cls):
        return cls('nl')

    @classmethod
    def Spanish(cls):
        return cls('es', 'mx')

    @classmethod
    def Mexican(cls):
        return cls('es', 'mx')
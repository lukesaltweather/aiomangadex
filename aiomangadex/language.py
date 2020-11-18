lang_codes = {
    19: "Arabic",
    22: "Bengali",
    14: "Bulgarian",
    37: "Burmese",
    33: "Catalan",
    21: "Chinese (Simp)",
    35: "Chinese (Trad)",
    24: "Czech",
    20: "Danish",
    5: "Dutch",
    1: "English",
    34: "Filipino",
    11: "Finnish",
    10: "French",
    8: "German",
    13: "Greek",
    39: "Hebrew",
    40: "Hindi",
    9: "Hungarian",
    27: "Indonesian",
    6: "Italian",
    2: "Japanese",
    28: "Korean",
    38: "Lithuanian",
    31: "Malay",
    25: "Mongolian",
    42: "Norwegian",
    41: "Other",
    30: "Persian",
    3: "Polish",
    16: "Portuguese (Br)",
    17: "Portuguese (Pt)",
    23: "Romanian",
    7: "Russian" ,
    4: "Serbo-Croatian",
    15: "Spanish (Es)",
    29: "Spanish (LATAM)",
    18: "Swedish",
    32: "Thai",
    26: "Turkish",
    36: "Ukrainian",
    12: "Vietnamese"
}

class Language:
    """ A class with a bunch of class methods to aid with finding a chapter in the desired language.
    """
    def __init__(self, code, scdry=None):
        self._lang_code = code
        self._scdry = scdry

    def __eq__(self, other):
        if other in (self._lang_code, self._scdry):
            return True
        return False

    @classmethod
    def English(cls):
        return cls('gb')

    @classmethod
    def NoLang(cls):
        return cls('')

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
from enum import Enum, EnumMeta, _EnumDict


class IntEnum(int, Enum):
    pass


class UniqueEnum(Enum):
    def __init__(self, *args):
        super(UniqueEnum, self).__init__()
        cls = self.__class__
        if any(self.value == dup.value for dup in cls):
            dup = cls(self.value)
            raise ValueError('No duplicate values allowed in %s: %r and %r' % (self.__class__.__name__, self, dup))


class AutoEnumMeta(EnumMeta):
    _i = 0

    def __new__(metacls, cls, bases, classdict):
        if type(classdict) is dict:
            original_dict = classdict
            classdict = _EnumDict()
            for k, v in original_dict.items():
                classdict[k] = v
        temp = _EnumDict()
        for k, v in classdict.items():
            if k in classdict._member_names:
                if v == ():
                    v = metacls._i
                else:
                    metacls._i = v
                metacls._i += 1
                temp[k] = v
            else:
                temp[k] = classdict[k]
        return EnumMeta.__new__(metacls, cls, bases, temp)


class AutoEnum(IntEnum, UniqueEnum):
    __metaclass__ = AutoEnumMeta


class ColorScheme(AutoEnum):
    COLOR1 = 0
    COLOR2 = ()
    COLOR3 = ()

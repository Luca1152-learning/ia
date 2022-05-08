from enum import Enum


class Euristica(Enum):
    BANALA = 1
    ADMISIBILA1 = 2
    ADMISIBILA2 = 3
    NEADMISIBILA = 4


def euristica_to_str(euristica: Euristica):
    if euristica == Euristica.BANALA:
        return "banala"
    elif euristica == Euristica.ADMISIBILA1:
        return "admisibila1"
    elif euristica == Euristica.ADMISIBILA2:
        return "admisibila2"
    elif euristica == Euristica.NEADMISIBILA:
        return "neadmisibila"

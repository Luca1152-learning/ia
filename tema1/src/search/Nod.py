from typing import List

from tema1.src.game.Harta import Harta


class Nod:
    def __init__(self, harta: List[List[str]], h: int = None):
        self.harta = Harta(harta)

        # Poate primim h-ul direct ca parametru (cum ar fi "inf" pentru nodul de start)
        self.h = self.estimeaza_h() if h is not None else h

    def estimeaza_h(self) -> int:
        # TODO

        return 1

    def __repr__(self) -> str:
        # TODO

        return "Nod"

    def __eq__(self, other) -> bool:
        return self.h == other.h and self.harta.soareci_in_aceeasi_pozitie_ca_alta_harta(other.harta)

from typing import List

from tema1.src.game.Harta import Harta
from tema1.src.search.Euristica import Euristica


class Nod:
    def __init__(self, harta: List[List[str]], k: int = False, e_nod_start: bool = False,
                 euristica: Euristica = Euristica.BANALA):
        """
        Initializeaza un obiect de tip Nod, ce contine informatii despre harta si entitatile de pe aceasta.

        :param harta: o matrice de caractere cu harta nodului
        :param k: numarul k din enunt, numarul de soraeci ce trebuie sa scape
        :param e_nod_start: True daca nodul curent este cel de START, False altfel
        :param euristica: ce euristica sa fie folosita in calculul h-ului, daca este cazul
        """
        self.euristica = euristica
        self.harta = Harta(harta)
        self.k = k

        # Se aplica pentru nodul de
        self.h = self.estimeaza_h(self.euristica) if not e_nod_start else float("inf")

    def estimeaza_h(self, euristica: Euristica) -> int:
        """
        Estimeaza valoarea h a nodului folosind tipul de euristica dat.

        :param euristica: ce tip de euristica sa fie folosita
        :return: un intreg ce reprezinta distanta minima estimata catre un nod scop.
        """
        if euristica == Euristica.BANALA:
            return self.h_euristica_banala()
        elif euristica == Euristica.ADMISIBILA1:
            return self.h_euristica_admisibila1()
        elif euristica == Euristica.ADMISIBILA2:
            return self.h_euristica_admisibila2()
        elif euristica == Euristica.NEADMISIBILA:
            return self.h_euristica_neadmisibila()

        raise Exception("Acest tip de euristica nu este tratat.")

    def h_euristica_banala(self) -> int:
        """
        Estimeaza valoarea h a nodului folosind o euristica banala.

        :return: un intreg ce reprezinta distanta minima estimata catre un nod scop.
        """

        return 1

    def h_euristica_admisibila1(self) -> int:
        """TODO"""

        # suma dist manhattan catre cel mai apropiat finish
        # handle case ajung in acelasi timp la finish => cost 1

        distante = []
        for soarece in self.harta.soareci:
            # Soarecele curent a fost prins / a niesit de pe harta - il ignoram
            if soarece is None:
                continue

            dist_min_iesire = float("inf")
            for iesire in self.harta.iesiri:
                dist_min_iesire = min(dist_min_iesire, soarece.distanta_manhattan(iesire))
            distante.append(dist_min_iesire)
        distante.sort()

        soarecii_apropiati = distante[0:self.k - self.harta.soareci_iesiti]
        soareci_aceeasi_distanta = len(soarecii_apropiati) - len(set(soarecii_apropiati))

        return sum(soarecii_apropiati) - soareci_aceeasi_distanta

    def h_euristica_admisibila2(self) -> int:
        """TODO"""

        distante = []
        for soarece in self.harta.soareci:
            # Soarecele curent a fost prins / a niesit de pe harta - il ignoram
            if soarece is None:
                continue
            distante.append(self.harta.distante_reale_iesiri[soarece.y][soarece.x])
        distante.sort()

        de_mutat = self.k - self.harta.soareci_iesiti
        if de_mutat < len(distante) and distante[de_mutat - 1] == distante[de_mutat]:
            # print("da")
            return 0

        soarecii_apropiati = distante[0:de_mutat]
        soareci_aceeasi_distanta = len(soarecii_apropiati) - len(set(soarecii_apropiati))

        return sum(soarecii_apropiati) - soareci_aceeasi_distanta

    def h_euristica_neadmisibila(self) -> int:
        """TODO"""

        # dist reala de la punct la soareci mai apropiata iesire
        suma_distante = 0
        for soarece in self.harta.soareci:
            # Soarecele curent a fost prins / a niesit de pe harta - il ignoram
            if soarece is None:
                continue

            dist_min_pisica = float("inf")
            if len(self.harta.pisici) == 0:
                dist_min_pisica = 0
            else:
                for pisica in self.harta.pisici:
                    dist_min_pisica = min(dist_min_pisica, soarece.distanta_manhattan(pisica))
            suma_distante += len(self.harta.harta) + len(self.harta.harta[0]) - dist_min_pisica
        return suma_distante

    def __repr__(self) -> str:
        # TODO

        return "Nod"

    def __eq__(self, other) -> bool:
        return self.harta.animale_in_aceeasi_pozitie_ca_alta_harta(other.harta)

import math
import os

from typing import Optional, Tuple

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Nod:
    def __init__(self, canibali_vest, canibali_est, misionari_vest, misionari_est, pozitie_barca=1):
        # Indice:    0        1
        # Valoare: VEST      EST
        self.canibali = [
            canibali_vest,
            canibali_est
        ]
        self.misionari = [
            misionari_vest,
            misionari_est
        ]

        # Trebuie sa stim si unde e barca (la fel, 0=vest, 1=est)
        self.pozitie_barca = pozitie_barca

        # Valoarea h a euristicii
        self.h = self.estimeaza_h()

    def estimeaza_h(self) -> int:
        # Euristica pentru aproximare = (numar de indivizi pe malul din est) / (capacitate barca)
        return math.floor(float(self.canibali[1] + self.misionari[1]) / Problema.LOCURI_BARCA)

    def __eq__(self, other) -> bool:
        return (self.canibali[0] == other.canibali[0] and self.misionari[0] == other.misionari[0] and
                self.canibali[1] == other.canibali[1] and self.misionari[1] == other.misionari[1] and
                self.pozitie_barca == other.pozitie_barca)

    def __repr__(self) -> str:
        return (f"[{self.canibali[0]}C, {self.misionari[0]}M] -{'B' if self.pozitie_barca == 0 else ''}----------" +
                f"-----{'B' if self.pozitie_barca == 1 else ''}- [{self.canibali[1]}C, {self.misionari[1]}M]")


class NodParcurgere:
    def __init__(self, nod: Nod, parinte, g: int):
        self.nod = nod  # Referinta catre nodul propriu-zis
        self.parinte = parinte  # Parintele nodului din parcurgerea curenta
        self.g = g  # Adancimea (suma arcelor de la start la nodul dat)
        self.f = self.g + self.nod.h  # Functia folosita pentru compararea valorilor nodurilor

    def se_creeaza_circuit(self, nod: Nod) -> bool:
        curr = self
        while curr is not None:
            if curr.nod == nod:
                return True
            curr = curr.parinte
        return False

    def expandeaza(self) -> list:
        # # Miscarile posibile din starea curenta sunt sa interschimbam vecinii blocului liber cu acesta

        miscari = []

        for misionari_de_mutat in range(min(Problema.LOCURI_BARCA, self.nod.misionari[self.nod.pozitie_barca]) + 1):
            locuri_libere_barca = Problema.LOCURI_BARCA - misionari_de_mutat
            for canibali_de_mutat in range(min(self.nod.canibali[self.nod.pozitie_barca], locuri_libere_barca) + 1):
                # Ignora cazul in care am trimite barca goala
                if misionari_de_mutat + canibali_de_mutat == 0:
                    continue

                # Verifica daca nu s-ar omori intre ei in barca
                if canibali_de_mutat > misionari_de_mutat and misionari_de_mutat != 0:
                    continue

                # Verifica daca nu s-ar omori intre ei pe mal
                misionari_ramasi = self.nod.misionari[self.nod.pozitie_barca] - misionari_de_mutat
                canibali_ramasi = self.nod.canibali[self.nod.pozitie_barca] - canibali_de_mutat
                if canibali_ramasi > misionari_ramasi and misionari_ramasi != 0:
                    continue

                # Verifica daca nu s-ar omori intre ei dupa ce ar ajunge pe celalalt mal
                pozitie_noua_barca = (self.nod.pozitie_barca + 1) % 2
                misionari_noi = self.nod.misionari[pozitie_noua_barca] + misionari_de_mutat
                canibali_noi = self.nod.canibali[pozitie_noua_barca] + canibali_de_mutat
                if canibali_noi > misionari_noi and misionari_noi != 0:
                    continue

                # Totul e sigur => mutarea e valida => cream un nod si il adaugam in lista
                canibali_vest = canibali_noi if pozitie_noua_barca == 0 else canibali_ramasi
                canibali_est = canibali_noi if pozitie_noua_barca == 1 else canibali_ramasi
                misionari_vest = misionari_noi if pozitie_noua_barca == 0 else misionari_ramasi
                misionari_est = misionari_noi if pozitie_noua_barca == 1 else misionari_ramasi
                nod_nou = Nod(canibali_vest, canibali_est, misionari_vest, misionari_est, pozitie_noua_barca)
                nod_parcurgere_nou = NodParcurgere(nod_nou, self, self.g + 1)  # Costul mutarii este 1
                miscari.append(nod_parcurgere_nou)

        return miscari

    def __repr__(self) -> str:
        return f"NodParcurgere[g={self.g} h={self.nod.h} f={self.f}]"


class Problema:
    # De citit din fisier de input
    NUMAR_CANIBALI_MISIONARI = None  # = numarul de canibali = numarul de misionari
    LOCURI_BARCA = None  # Numarul de locuri in barca

    def citeste(self, filepath: str):
        with open(filepath, "r") as f:
            Problema.NUMAR_CANIBALI_MISIONARI, Problema.LOCURI_BARCA = [int(x) for x in f.read().split()]

    def cauta_nod_parcurgere(self, nod_parcurgere: NodParcurgere, lista: [NodParcurgere]) -> Optional[NodParcurgere]:
        for x in lista:
            if x.nod == nod_parcurgere.nod:
                return x
        return None

    def sortare_open(self, x: NodParcurgere) -> Tuple[int, int]:
        return x.f, -x.g

    def rezolva(self):
        open = []  # Nodurile ce urmeaza sa fie expandate
        closed = []  # Nodurile deja expandate

        # Cream NodParcurgere de start si il adaugam in open
        nod_start = NodParcurgere(
            Nod(0, Problema.NUMAR_CANIBALI_MISIONARI, 0, Problema.NUMAR_CANIBALI_MISIONARI), None, 0
        )
        open.append(nod_start)

        while open:
            # Stergem si stocam ultimul element. Nu primul, deoarece open e sortat in ordinea inversa
            # necesara algoritmului - tocmai pentru a putea face pop() rapid
            nod_curent = open.pop()

            # Am gasit un nod scop (nu mai e niciun misionar/canibal pe malul de vest)
            if nod_curent.nod.misionari[1] + nod_curent.nod.canibali[1] == 0:
                drum = []

                nod_i = nod_curent
                while nod_i:
                    drum.append(nod_i.nod)
                    nod_i = nod_i.parinte

                drum.reverse()
                for nod in drum:
                    print(nod.__repr__())

                return

            # Expandeaza nodul curent
            closed.append(nod_curent)  # Marcheaza-l ca expandat (punandu-l in closed)
            succesori = nod_curent.expandeaza()

            for succesor in succesori:
                nod_nou = succesor

                # Cautam succesor in open
                nod_in_open = self.cauta_nod_parcurgere(succesor, open)
                if nod_in_open is not None:
                    # Am gasit un drum mai bun catre succesor
                    if succesor.f < nod_in_open.f:
                        open.remove(nod_in_open)
                    else:
                        nod_nou = None

                # succesor a fost expandat in trecut
                nod_in_closed = self.cauta_nod_parcurgere(succesor, closed)
                if nod_in_closed:
                    closed.remove(nod_in_closed)
                    nod_nou = succesor

                if nod_nou is not None:
                    open.append(nod_nou)
                    # Sorteaza invers criteriului algoritmului, pentru a putea face pop() rapid
                    open.sort(key=self.sortare_open, reverse=True)


p = Problema()
p.citeste(os.path.join(__location__, "lab3-3.in"))
p.rezolva()

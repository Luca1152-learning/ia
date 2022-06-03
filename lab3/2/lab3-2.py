import copy
import os.path
from typing import Optional, List, Tuple

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class Nod:
    def __init__(self, matrice: List[List[int]], h=None):
        self.matrice = matrice

        # Nu ne mai este data distanta estimata pana la un nod scop, trebuie sa o estimam noi
        if h is not None:
            self.h = h  # Poate primim h-ul direct ca parametru (cum ar fi 0 pentru nodul scop)
        else:
            self.h = self.estimeaza_h()

    @staticmethod
    def matrice_to_dict_pozitii(matrice):
        pozitii = {}
        for i in range(len(matrice)):
            for j in range(len(matrice[i])):
                pozitii[matrice[i][j]] = (i, j)
        return pozitii

    def estimeaza_h(self) -> int:
        # Euristica pentru aproximare = suma distantelor blocurilor din matricea curenta fata
        # de matricea scop

        matrice_curr = self.matrice
        matrice_scop = Problema.SCOP.matrice

        # Transforma matricile in dictionare de tipul numar->(coordonata i, coordonata j)
        pozitii_curr = self.matrice_to_dict_pozitii(matrice_curr)
        pozitii_scop = self.matrice_to_dict_pozitii(matrice_scop)

        h = 0
        for numar, pozitie_curr in pozitii_curr.items():
            (i_curr, j_curr) = pozitie_curr
            (i_scop, j_scop) = pozitii_scop[numar]
            h += abs(i_curr - i_scop) + abs(j_curr - j_scop)

        return h

    @staticmethod
    def sunt_matrici_egale(matrix_a: List[list], matrix_b: List[list]) -> bool:
        for i in range(Problema.N):
            for j in range(Problema.N):
                if matrix_a[i][j] != matrix_b[i][j]:
                    return False
        return True

    def __eq__(self, other) -> bool:
        return self.sunt_matrici_egale(self.matrice, other.matrice)

    def __repr__(self) -> str:
        return "\n".join([" ".join([str(x) if x != 0 else " " for x in rand]) for rand in self.matrice])


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
        # Miscarile posibile din starea curenta sunt sa interschimbam vecinii blocului liber cu acesta

        (i_liber, j_liber) = Nod.matrice_to_dict_pozitii(self.nod.matrice)[0]

        miscari = []
        for deplasament in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            (dep_i, dep_j) = deplasament

            # Deplasamentul nu poate fi aplicat, continua
            if not (0 <= i_liber + dep_i < Problema.N) or not (0 <= j_liber + dep_j < Problema.N):
                continue

            i_nou = i_liber + dep_i
            j_nou = j_liber + dep_j

            copie_matrice = copy.deepcopy(self.nod.matrice)
            copie_matrice[i_nou][j_nou], copie_matrice[i_liber][j_liber] = 0, copie_matrice[i_nou][j_nou]

            nod = Nod(copie_matrice)
            nod_parcurgere = NodParcurgere(nod, self, self.g + 1)
            miscari.append(nod_parcurgere)

        return miscari

    def __repr__(self) -> str:
        return f"f={self.f} g={self.g} h={self.nod.h} - {self.nod.__repr__()}"


class Problema:
    N = 3  # Dimensiunea matricei
    START = None  # Configuratia initiala
    SCOP = None  # Configuratia finala

    def citeste(self, filepath: str):
        with open(filepath, "r") as f:
            # Citeste starea initiala
            numere = [int(x) for x in f.read().split()]
            matrice_start = [numere[:3], numere[3:6], numere[6: 9]]
            Problema.START = Nod(matrice_start, float("inf"))

        matrice_scop = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        Problema.SCOP = Nod(matrice_scop, 0)

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
        nod_start = NodParcurgere(Problema.START, None, 0)
        open.append(nod_start)

        while open:
            # Stergem si stocam ultimul element. Nu primul, deoarece open e sortat in ordinea inversa
            # necesara algoritmului - tocmai pentru a putea face pop() rapid
            nod_curent = open.pop()

            # Am gasit un nod scop
            if nod_curent.nod == Problema.SCOP:
                drum = []

                nod_i = nod_curent
                while nod_i:
                    drum.append(nod_i.nod)
                    nod_i = nod_i.parinte

                drum.reverse()
                for nod in drum:
                    print(nod.__repr__())
                    print()

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
p.citeste(os.path.join(__location__, "lab3-2.in"))
p.rezolva()

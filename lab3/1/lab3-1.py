import copy
from typing import Optional, List, Tuple


class Nod:
    def __init__(self, stive: List[List[int]], h=None):
        # O lista cu cele N stive din problema (ce sunt tot liste)
        self.stive = stive

        # Nu ne mai este data distanta estimata pana la un nod scop, trebuie sa o estimam noi
        if h is not None:
            self.h = h  # Poate primim h-ul direct ca parametru (cum ar fi 0 pentru nodul scop)
        else:
            self.h = self.estimeaza_h()

    def estimeaza_h(self) -> int:
        # Euristica pentru aproximare = cate blocuri sunt deasupra unui bloc gresit
        # (cu cat numarul e mai mare, cu atat ne indepartam de nodul scop, deci e ok)

        h = 0
        for index_stiva in range(Problema.N):
            stiva_curr = self.stive[index_stiva]
            stiva_scop = Problema.SCOP.stive[index_stiva]

            # Cauta indexul primei pozitii unde blocurile difera
            prima_greseala = None
            for i in range(min(len(stiva_curr), len(stiva_scop))):
                if stiva_curr[i] != stiva_scop[i]:
                    prima_greseala = i
                    break

            # Am gasit o diferenta => blocurile de deasupra, inclusiv blocul curent, sunt gresite
            if prima_greseala is not None:
                h += min(len(stiva_scop), len(stiva_curr)) - prima_greseala

            # Daca difera numarul de blocuri (avem mai multe/putine) ne indeparteaza de raspuns
            if len(stiva_curr) != len(stiva_scop):
                h += abs(len(stiva_curr) - len(stiva_scop))

        return h

    @staticmethod
    def sunt_matrici_egale(matrix_a: List[List], matrix_b: List[List]) -> bool:
        if len(matrix_a) != len(matrix_b):
            return False

        for i in range(len(matrix_a)):
            if len(matrix_a[i]) != len(matrix_b[i]):
                return False
            for j in range(len(matrix_a[i])):
                if matrix_a[i][j] != matrix_b[i][j]:
                    return False

        return True

    def __eq__(self, other) -> bool:
        return self.sunt_matrici_egale(self.stive, other.stive)

    def __repr__(self) -> str:
        return "\n".join(["".join(f"{index + 1}: {' '.join(stiva)}") for index, stiva in enumerate(self.stive)])


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
        # Miscarile posibile din starea curenta sunt sa mutam cate un bloc pe fiecare dintre celelalte stive

        miscari = []

        for index_stiva_push in range(Problema.N):
            for index_stiva_pull in range(Problema.N):
                if index_stiva_push != index_stiva_pull and len(self.nod.stive[index_stiva_push]) > 0:
                    copie_stive = copy.deepcopy(self.nod.stive)

                    bloc = copie_stive[index_stiva_push][-1]
                    copie_stive[index_stiva_push].pop()
                    copie_stive[index_stiva_pull].append(bloc)

                    nod = Nod(copie_stive)
                    nod_parcurgere = NodParcurgere(nod, self, self.g + 1)
                    miscari.append(nod_parcurgere)

        return miscari

    def __repr__(self) -> str:
        return f"f={self.f} g={self.g} h={self.nod.h} - {self.nod.__repr__()}"


class Problema:
    N = None  # Numarul de stive, citit din fisier
    START = None  # Configuratia initiala
    SCOP = None  # Configuratia finala

    def citeste(self, filepath: str):
        with open(filepath, "r") as f:
            # Citeste N
            Problema.N = int(f.readline())

            # Citste starea initiala
            f.readline()
            stive_start = []
            for _ in range(Problema.N):
                stiva = f.readline().split()
                stive_start.append(stiva)
            Problema.START = Nod(stive_start, float("inf"))

            # Citeste starea finala
            f.readline()
            stive_scop = []
            for _ in range(Problema.N):
                stiva = f.readline().split()
                stive_scop.append(stiva)
            Problema.SCOP = Nod(stive_scop, 0)

    def cauta_nod_parcurgere(self, nod_parcurgere: NodParcurgere, lista: [NodParcurgere]) -> Optional[NodParcurgere]:
        for x in lista:
            if x.nod == nod_parcurgere.nod:
                return x
        return None

    def sortare_open(self, x: NodParcurgere) -> Tuple[int, int]:
        return (x.f, -x.g)

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
                for index, nod in enumerate(drum):
                    if index != 0:
                        bloc_mutat = stiva_push = stiva_pull = None
                        for i in range(Problema.N):
                            if len(drum[index].stive[i]) < len(drum[index - 1].stive[i]):
                                bloc_mutat = drum[index - 1].stive[i][-1]
                                stiva_push = i
                            elif len(drum[index].stive[i]) > len(drum[index - 1].stive[i]):
                                stiva_pull = i

                        print("")
                        print(f"Mutam blocul [{bloc_mutat}] de pe stiva {stiva_push + 1} pe stiva {stiva_pull + 1}:")

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
p.citeste("lab3-1.in")
p.rezolva()

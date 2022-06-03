import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Nod:
    def __init__(self, info: str, h):
        self.info = info  # Identificatorul nodului
        self.h = h  # Valoarea estimata de la nodul curent la un nod scop

    def __repr__(self):
        return f"{self.info} ({self.h})"


class Muchie:
    def __init__(self, x: Nod, y: Nod, cost):
        self.x = x  # Primul nod al muchiei
        self.y = y  # Al doilea nod al muchiei
        self.cost = cost

    def __repr__(self):
        return f"{self.x.info}->{self.y.info} ({self.cost})"


class NodParcurgere:
    def __init__(self, nod: Nod, parinte, g):
        self.nod = nod  # Referinta catre nodul propriu-zis
        self.parinte = parinte  # Parintele nodului din parcurgerea curenta
        self.g = g  # Adancimea (suma arcelor de la start la nodul dat)
        self.f = self.g + self.nod.h  # Functia folosita pentru compararea valorilor nodurilor

    def se_creeaza_circuit(self, nod: Nod):
        curr = self
        while curr is not None:
            if curr.nod == nod:
                return True
            curr = curr.parinte
        return False

    def expandeaza(self, muchii: [Muchie]):
        adiacente = []
        for muchie in muchii:
            if muchie.x == self.nod and not self.se_creeaza_circuit(muchie.y):
                adiacente.append(NodParcurgere(muchie.y, self, self.g + muchie.cost))
        return adiacente

    def __repr__(self):
        return f"{self.nod.info} (parinte = {self.parinte.nod.info if self.parinte else 'nu'}, f = {self.f}, g = {self.g})"


class Problema:
    def __init__(self):
        self.noduri = {}
        self.muchii = []
        self.start = None
        self.scop = []

    def citeste(self, filepath: str):
        with open(filepath, "r") as f:
            # Noduri
            nodes_count = int(f.readline())
            for _ in range(nodes_count):
                info, h = f.readline().split()
                self.noduri[info] = Nod(info, float(h))

            # Muchii
            edges_count = int(f.readline())
            for _ in range(edges_count):
                x, y, cost = f.readline().split()
                self.muchii.append(Muchie(self.noduri[x], self.noduri[y], int(cost)))

            start_info = f.readline().strip()
            self.start = self.noduri[start_info]

            scop_count = int(f.readline())
            for _ in range(scop_count):
                scop_info = f.readline().strip()
                self.scop.append(self.noduri[scop_info])

    def sortare_open(self, x):
        return (x.f, -x.g)

    def cauta_nod_parcurgere(self, nod_parcurgere: NodParcurgere, lista: [NodParcurgere]):
        for x in lista:
            if x.nod == nod_parcurgere.nod:
                return x
        return None

    def rezolva(self):
        open = []  # Nodurile ce urmeaza sa fie expandate
        closed = []  # Nodurile deja expandate

        # Cream NodParcurgere de start si il adaugam in open
        nod_start = NodParcurgere(self.start, None, 0)
        open.append(nod_start)

        while open:
            # Stergem si stocam ultimul element. Nu primul, deoarece open e sortat in ordinea inversa
            # necesara algoritmului - tocmai pentru a putea face pop() rapid
            nod_curent = open.pop()

            # Am gasit un nod scop
            if nod_curent.nod in self.scop:
                drum = []

                nod_i = nod_curent
                while nod_i:
                    drum.append(nod_i.nod)
                    nod_i = nod_i.parinte

                for nod in reversed(drum):
                    print(nod.info)

                return

            # Expandeaza nodul curent
            closed.append(nod_curent)  # Marcheaza-l ca expandat (punandu-l in closed)
            succesori = nod_curent.expandeaza(self.muchii)

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
p.citeste(os.path.join(__location__, "lab2.in"))
p.rezolva()

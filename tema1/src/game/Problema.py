from tema1.src.search.Nod import Nod
from tema1.src.search.NodParcurgere import NodParcurgere
from tema1.src.utils.EvenimentJoc import EvenimentJoc


class Problema:
    def __init__(self, filepath: str):
        self.start, self.k = self._citeste(filepath)

    def _citeste(self, filepath: str):
        with open(filepath, "r") as f:
            k = int(f.readline())

            map_string = f.read()
            map = [line.split(" ") for line in map_string.split("\n")]
            start = Nod(map, float("inf"))

            return start, k

    def sortare_open(self, x):
        return x.f, -x.g

    def cauta_nod_parcurgere(self, nod_parcurgere: NodParcurgere, lista: [NodParcurgere]):
        for x in lista:
            if x.nod == nod_parcurgere.nod:
                return x
        return None

    def e_nod_scop(self, nod: Nod) -> bool:
        """
        TODO

        :param nod:
        :return:
        """

        return nod.harta.soareci_iesiti == self.k

    def rezolva(self):
        open = []  # Nodurile ce urmeaza sa fie expandate
        closed = []  # Nodurile deja expandate

        # Cream NodParcurgere de start si il adaugam in open
        nod_start = NodParcurgere(self.start, None, 0)
        open.append(nod_start)

        self.numar_soareci_initial = len(nod_start.nod.harta.soareci)

        while open:
            # Stergem si stocam ultimul element. Nu primul, deoarece open e sortat in ordinea inversa
            # necesara algoritmului - tocmai pentru a putea face pop() rapid
            nod_curent = open.pop()

            # Am gasit un nod scop
            if self.e_nod_scop(nod_curent.nod):
                drum = []

                nod_i = nod_curent
                while nod_i:
                    drum.append(nod_i)
                    nod_i = nod_i.parinte

                for index, nod_parcurgere in enumerate(reversed(drum)):
                    harta = nod_parcurgere.nod.harta

                    print(f"{index + 1}) g={nod_parcurgere.g}")
                    print("\n".join([" ".join([cell.ljust(2, " ") for cell in line]) for line in harta.harta]))
                    for eveniment in harta.evenimente:
                        tip = eveniment["tip"]
                        if tip == EvenimentJoc.PISICA_MANCAT_SOARECE:
                            print(f"Pisica p{eveniment['id_pisica']} a mancat soarecele s{eveniment['id_soarece']}.")
                        elif tip == EvenimentJoc.SOARECE_ASCUNS:
                            print(f"Soarecele s{eveniment['id']} s-a ascuns.")
                        elif tip == EvenimentJoc.SOARECE_IESIT_HARTA:
                            print(f"Soarecele s{eveniment['id']} a iesit de pe harta.")
                        elif tip == EvenimentJoc.PISICA_BLOCATA:
                            print(f"Pisica p{eveniment['id']} nu s-a putut misca.")
                        elif tip == EvenimentJoc.SOARECE_BLOCAT:
                            print(f"Soarecele s{eveniment['id']} nu s-a putut misca.")
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

from tema1.src.search.Nod import Nod
from tema1.src.search.NodParcurgere import NodParcurgere
from tema1.src.utils.EvenimentJoc import EvenimentJoc


class Problema:
    def __init__(self, input_filepath: str, output_filepath: str):
        self.start, self.k = self._citeste(input_filepath)
        self.output_file = open(output_filepath, "w")  # Inchis in destructor

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

                    self.output_file.write(f"{index + 1}) g={nod_parcurgere.g}\n")

                    # Respecta formatul hartii din enunt, unde lungimea unei coloane depinde de cel mai lung sir de caractere
                    max_str_lengths_per_column = [0 for _ in range(len(harta.harta[0]))]
                    for j in range(len(harta.harta[0])):
                        for i in range(len(harta.harta)):
                            max_str_lengths_per_column[j] = max(len(harta.harta[i][j]), max_str_lengths_per_column[j])
                    self.output_file.write(
                        "\n".join(
                            [" ".join([cell.ljust(max_str_lengths_per_column[j], " ") for j, cell in enumerate(line)])
                             for line in harta.harta]
                        ) + "\n"
                    )

                    for eveniment in harta.evenimente:
                        tip = eveniment["tip"]
                        if tip == EvenimentJoc.PISICA_MANCAT_SOARECE:
                            self.output_file.write(
                                f"Pisica p{eveniment['id_pisica']} a mancat soarecele s{eveniment['id_soarece']}.\n"
                            )
                        elif tip == EvenimentJoc.SOARECE_ASCUNS:
                            self.output_file.write(f"Soarecele s{eveniment['id']} s-a ascuns.\n")
                        elif tip == EvenimentJoc.SOARECE_IESIT_HARTA:
                            self.output_file.write(f"Soarecele s{eveniment['id']} a iesit de pe harta.\n")
                        elif tip == EvenimentJoc.PISICA_BLOCATA:
                            self.output_file.write(f"Pisica p{eveniment['id']} nu s-a putut misca.\n")
                        elif tip == EvenimentJoc.SOARECE_BLOCAT:
                            self.output_file.write(f"Soarecele s{eveniment['id']} nu s-a putut misca.\n")
                    self.output_file.write("\n")

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

    def __del__(self):
        self.output_file.close()

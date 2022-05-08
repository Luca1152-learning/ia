from timeit import default_timer as timer

from tema1.src.search.Euristica import Euristica, euristica_to_str
from tema1.src.search.Nod import Nod
from tema1.src.search.NodParcurgere import NodParcurgere
from tema1.src.utils.EvenimentJoc import EvenimentJoc


class Problema:
    def __init__(self, input_filepath: str, partial_output_filepath: str, euristica: Euristica, timeout: float,
                 n_sol: int):
        """TODO"""

        self.euristica = euristica
        self.timeout = timeout
        self.start, self.k = self._citeste(input_filepath)
        # Fisier inchis in destructor
        self.partial_output_filepath = partial_output_filepath
        self.output_file = open(f"{partial_output_filepath}{'-1' if n_sol > 1 else ''}.out", "w")

        # Statistici
        self.lungime_drum = 0
        self.cost_drum = 0
        self.durata_algoritm = 0
        self.max_noduri_existente = 0
        self.total_noduri_calculate = 0
        self.n_sol = n_sol
        self.curr_sol = 0

    def _citeste(self, filepath: str):
        """TODO"""

        with open(filepath, "r") as f:
            k = int(f.readline())

            map_string = f.read()
            map = [line.split(" ") for line in map_string.split("\n")]
            start = Nod(map, k, e_nod_start=True, euristica=self.euristica)

            return start, k

    def sortare_open(self, x):
        """TODO"""

        return x.f, -x.g

    def cauta_nod_parcurgere(self, nod_parcurgere: NodParcurgere, lista: [NodParcurgere]):
        """TODO"""

        for x in lista:
            if x.nod == nod_parcurgere.nod:
                return x
        return None

    def e_nod_scop(self, nod: Nod) -> bool:
        """TODO"""

        return nod.harta.soareci_iesiti == self.k

    def are_solutie(self, nod_start: NodParcurgere) -> bool:
        """TODO"""

        harta = nod_start.nod.harta

        soareci_ce_pot_ajunge_la_iesiri = 0
        for soarece in harta.soareci:
            if harta.distante_reale_iesiri[soarece.y][soarece.x] != float("inf"):
                soareci_ce_pot_ajunge_la_iesiri += 1
        return soareci_ce_pot_ajunge_la_iesiri >= self.k

    def rezolva(self):
        """TODO"""

        # Statistici
        algoritm_start = timer()

        # A*
        open_list = []  # Nodurile ce urmeaza sa fie expandate
        closed_list = []  # Nodurile deja expandate
        nod_start = NodParcurgere(self.start, None, 0)
        self.numar_soareci_initial = len(nod_start.nod.harta.soareci)

        # Verificam (relativ naiv) daca se poate ajunge intr-un nod scop, numarand cati soareci pot ajunge la iesiri
        # si comparand cu k
        if not self.are_solutie(nod_start):
            self.lungime_drum = 0
            self.durata_algoritm = timer() - algoritm_start

            print(
                f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}A* optimizat, "
                f"euristica {euristica_to_str(self.euristica)} - lungime {self.lungime_drum}" +
                f" - cost {self.cost_drum} - {self.durata_algoritm:.2f}s - {self.max_noduri_existente} max noduri" +
                f" - {self.total_noduri_calculate} total noduri"
            )
            return

        # Posibil sa avem solutie. Continuam cu A*.

        open_list.append(nod_start)
        self.total_noduri_calculate = 1
        while open_list:
            # Statistici
            self.max_noduri_existente = max(self.max_noduri_existente, len(open_list) + len(closed_list))

            # Stergem si stocam ultimul element. Nu primul, deoarece open e sortat in ordinea inversa
            # necesara algoritmului - tocmai pentru a putea face pop() rapid
            nod_curent = open_list.pop()

            # Am gasit un nod scop
            if self.e_nod_scop(nod_curent.nod):
                drum = []

                nod_i = nod_curent
                while nod_i:
                    drum.append(nod_i)
                    nod_i = nod_i.parinte

                # Statistici
                self.lungime_drum = len(drum) - 1
                algoritm_end = timer()
                self.durata_algoritm = algoritm_end - algoritm_start
                self.cost_drum = nod_curent.g
                print(
                    f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}A* optimizat, "
                    f"euristica {euristica_to_str(self.euristica)} - lungime {self.lungime_drum}" +
                    f" - cost {self.cost_drum} - {self.durata_algoritm:.2f}s - {self.max_noduri_existente} max noduri" +
                    f" - {self.total_noduri_calculate} total noduri"
                )

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

                self.curr_sol += 1
                if self.curr_sol == self.n_sol or self.lungime_drum == 0:
                    return
                else:
                    self.output_file.close()
                    self.output_file = open(f"{self.partial_output_filepath}-{self.curr_sol + 1}.out", "w")
                    continue

            # Asigura-te ca nu s-a depasit timpul limita
            elapsed = timer() - algoritm_start
            if elapsed > self.timeout:
                print(f"{f'[{self.curr_sol}/{self.n_sol}]' if self.n_sol > 1 else ''}A* optimizat, " +
                      f"euristica {euristica_to_str(self.euristica)} - TIMEOUT")
                return

            # Expandeaza nodul curent
            closed_list.append(nod_curent)  # Marcheaza-l ca expandat (punandu-l in closed)
            succesori = nod_curent.expandeaza()
            self.total_noduri_calculate += len(succesori)

            for succesor in succesori:
                nod_nou = succesor

                # Cautam succesor in open
                nod_in_open = self.cauta_nod_parcurgere(succesor, open_list)
                if nod_in_open is not None:
                    # Am gasit un drum mai bun catre succesor
                    if succesor.f < nod_in_open.f:
                        open_list.remove(nod_in_open)
                    else:
                        nod_nou = None

                # succesor a fost expandat in trecut
                nod_in_closed = self.cauta_nod_parcurgere(succesor, closed_list)
                if nod_in_closed:
                    closed_list.remove(nod_in_closed)
                    nod_nou = succesor

                if nod_nou is not None:
                    open_list.append(nod_nou)
                    # Sorteaza invers criteriului algoritmului, pentru a putea face pop() rapid
                    open_list.sort(key=self.sortare_open, reverse=True)

    def __del__(self):
        self.output_file.close()

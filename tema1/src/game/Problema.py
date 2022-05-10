import collections
from timeit import default_timer as timer
from typing import List, Optional, Tuple

from tema1.src.search.Euristica import Euristica, euristica_to_str
from tema1.src.search.Nod import Nod
from tema1.src.search.NodParcurgere import NodParcurgere
from tema1.src.utils.EvenimentJoc import EvenimentJoc


class Problema:
    def __init__(self, input_filepath: str, partial_output_filepath: str, timeout: float,
                 n_sol: int, euristica: Optional[Euristica] = None):
        """
        Initializeaza un obiect de tip Problema.

        :param input_filepath: calea catre fisierul de input
        :param partial_output_filepath: parte din calea catre fisierul de output, a se completa cu numarul solutiei si
        extensia
        :param timeout: in cat timp sa se opreasca executia algoritmului
        :param n_sol: numarul de solutii de generat
        :param euristica: ce euristica sa fie folosita, in caz ca se foloseste un algoritm de tip best first
        """

        # Datele problemei
        self.timeout = timeout
        self.n_sol = n_sol
        self.euristica = euristica

        # Input
        self.start, self.k = self._citeste(input_filepath)

        # Output
        self.partial_output_filepath = partial_output_filepath
        self.output_file = open(f"{partial_output_filepath}{'-1' if n_sol > 1 else ''}.out", "w")

        # Statistici
        self.lungime_drum = 0
        self.cost_drum = 0
        self.durata_algoritm = 0
        self.max_noduri_existente = 0
        self.total_noduri_calculate = 0
        self.curr_sol = 0

    def _citeste(self, filepath: str) -> Tuple[Nod, int]:
        """
        Citeste fisierul de input de la calea data.

        :param filepath: calea fisierului de input
        :return: un tuplu cu Nod-ul de start si valoarea lui k
        """

        with open(filepath, "r") as f:
            k = int(f.readline())

            map_string = f.read()
            map = [line.split(" ") for line in map_string.split("\n")]
            start = Nod(map, k, e_nod_start=True, euristica=self.euristica)

            return start, k

    def sortare_open(self, x: NodParcurgere) -> Tuple[int, int]:
        """
        Criteriul de sortare pentru lista OPEN.

        :param x: Nodul Parcurgere caruia sa ii atribuim o valoare
        :return: un tuplu cu criteriul corespunzator de sortare care sa fie folosit
        """

        return x.f, -x.g

    def cauta_nod_parcurgere(self, nod_parcurgere: NodParcurgere, lista: [NodParcurgere]) -> Optional[NodParcurgere]:
        """
        Verifica existenta unui Nod Parcurgere intr-o lista de Noduri Parcurgere, comparandu-se Nod-urile acestora.

        :param nod_parcurgere: Nodul Parcurgere de gasit
        :param lista: lista de Noduri Parcurgere de cautat
        :return: obiectul de tip NodParcurgere gasit sau None daca nu a fost gasit
        """

        for x in lista:
            if x.nod == nod_parcurgere.nod:
                return x
        return None

    def e_nod_scop(self, nod: Nod) -> bool:
        """
        Verifica daca Nod-ul dat ca parametru este unul de tip scop.

        :param nod: Nod-ul de verificat
        :return: True daca este de tip scop, False altfel
        """

        return nod.harta.soareci_iesiti == self.k

    def are_solutie(self, nod_start: NodParcurgere) -> bool:
        """
        Verifica daca, plecandu-se din nodul de start dat, se poate ajunge la un nod scop.

        :param nod_start: nodul de start care sa fie verificat
        :return: True daca problema poate avea solutie, False altfel
        """

        harta = nod_start.nod.harta

        soareci_ce_pot_ajunge_la_iesiri = 0
        for soarece in harta.soareci:
            if harta.distante_reale_iesiri[soarece.y][soarece.x] != float("inf"):
                soareci_ce_pot_ajunge_la_iesiri += 1
        return soareci_ce_pot_ajunge_la_iesiri >= self.k

    def afiseaza_solutie(self, nod_scop: NodParcurgere, algoritm_start, nume_algoritm: str):
        """
        Scrie output-ul corespunzator drumului la nodul scop gasit.

        :param nod_scop: nodul scop gasit
        :param algoritm_start: un timer cu momentul in care s-a inceput executia algoritmului
        :param nume_algoritm: numele algoritmului folosit, ce va fi scris in consola
        """

        drum = []

        nod_i = nod_scop
        while nod_i:
            drum.append(nod_i)
            nod_i = nod_i.parinte

        # Statistici
        self.lungime_drum = len(drum) - 1
        algoritm_end = timer()
        self.durata_algoritm = algoritm_end - algoritm_start
        self.cost_drum = nod_scop.g
        print(
            f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}{nume_algoritm}" +
            (
                f", euristica {euristica_to_str(self.euristica)}" if self.euristica else "") + f" - lungime {self.lungime_drum}" +
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

    def rezolva_bfs(self):
        """Rezolva Problema data folosind un algoritm de tip BFS."""

        # Statistici
        algoritm_start = timer()

        # BFS
        nod_start = NodParcurgere(self.start, None, 0)
        self.numar_soareci_initial = len(nod_start.nod.harta.soareci)

        # Verificam (relativ naiv) daca se poate ajunge intr-un nod scop, numarand cati soareci pot ajunge la iesiri
        # si comparand cu k
        if not self.are_solutie(nod_start):
            self.lungime_drum = 0
            self.durata_algoritm = timer() - algoritm_start

            print(
                f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}BFS - NICIO SOLUTIE"
            )
            return

        # Posibil sa avem solutie. Continuam cu BFS
        q = collections.deque([nod_start])
        self.total_noduri_calculate = 1

        while q:
            # Statistici
            self.max_noduri_existente = max(self.max_noduri_existente, len(q))

            nod_curent = q.popleft()

            # Am gasit un nod scop
            if self.e_nod_scop(nod_curent.nod):
                self.afiseaza_solutie(nod_curent, algoritm_start, "BFS")

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
                print(f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}BFS - TIMEOUT")
                return

            # Expandeaza nodul curent
            succesori = nod_curent.expandeaza()
            self.total_noduri_calculate += len(succesori)

            for succesor in succesori:
                q.append(succesor)

    def _ruleaza_dfs_recursiv(self, nod_curent: NodParcurgere, algoritm_start, adancime=1):
        """
        Recursia unui algoritm DFS ce rezolva Problema data.

        :param nod_curent: nodul curent din parcurgere
        :param algoritm_start: un timer cu momentul in care s-a inceput executia algoritmului
        :param adancime: adancimea curenta a nodului din parcurgere
        """

        self.max_noduri_existente = max(self.max_noduri_existente, adancime)

        # Am gasit un nod scop
        if self.e_nod_scop(nod_curent.nod) and self.curr_sol < self.n_sol:
            self.afiseaza_solutie(nod_curent, algoritm_start, "DFS")

            self.curr_sol += 1
            if self.curr_sol == self.n_sol or self.lungime_drum == 0:
                return
            else:
                self.output_file.close()
                self.output_file = open(f"{self.partial_output_filepath}-{self.curr_sol + 1}.out", "w")

        # Asigura-te ca nu s-a depasit timpul limita
        elapsed = timer() - algoritm_start
        if elapsed > self.timeout and not self.dfs_timeout:
            print(f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}DFS - TIMEOUT")
            self.dfs_timeout = True
            return

        # Expandeaza nodul curent
        succesori = nod_curent.expandeaza()
        self.total_noduri_calculate += len(succesori)

        if not self.dfs_timeout:
            for succesor in succesori:
                self._ruleaza_dfs_recursiv(succesor, algoritm_start, adancime + 1)

    def rezolva_dfs(self):
        """Rezolva Problema data folosind un algoritm de tip DFS."""

        # Statistici
        algoritm_start = timer()

        # DFS
        nod_start = NodParcurgere(self.start, None, 0)
        self.numar_soareci_initial = len(nod_start.nod.harta.soareci)

        # Verificam (relativ naiv) daca se poate ajunge intr-un nod scop, numarand cati soareci pot ajunge la iesiri
        # si comparand cu k
        if not self.are_solutie(nod_start):
            self.lungime_drum = 0
            self.durata_algoritm = timer() - algoritm_start

            print(
                f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}DFS - NICIO SOLUTIE"
            )
            return

        self.total_noduri_calculate = 1
        self.dfs_timeout = False
        try:
            self._ruleaza_dfs_recursiv(nod_start, algoritm_start)
        except RecursionError:
            print(
                f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}DFS - STACK OVERFLOW"
            )

    def _ruleaza_dfi_recursiv(
            self, nod_curent: NodParcurgere, algoritm_start: NodParcurgere, adancime: int = 1,
            max_adancime=float("inf")
    ):
        """
        Recursia unui algoritm DFI ce rezolva Problema data.

        :param nod_curent: nodul curent din parcurgere
        :param algoritm_start: un timer cu momentul in care s-a inceput executia algoritmului
        :param adancime: adancimea curenta a nodului din parcurgere
        :param max_adancime: adancimea maxima a pasului curent din algoritm
        """

        if adancime > max_adancime or self.curr_sol >= self.n_sol:
            return

        self.max_noduri_existente = max(self.max_noduri_existente, adancime)

        # Am gasit un nod scop
        if self.e_nod_scop(nod_curent.nod) and nod_curent.nod not in self.dfi_noduri_scop_excluse:
            self.dfi_noduri_scop_excluse.append(nod_curent.nod)
            self.afiseaza_solutie(nod_curent, algoritm_start, "DFI")

            self.curr_sol += 1
            if self.curr_sol >= self.n_sol or self.lungime_drum == 0:
                self.dfs_succes = True
                return
            else:
                self.output_file.close()
                self.output_file = open(f"{self.partial_output_filepath}-{self.curr_sol + 1}.out", "w")

        # Asigura-te ca nu s-a depasit timpul limita
        elapsed = timer() - algoritm_start
        if elapsed > self.timeout and not self.dfs_timeout:
            print(f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}DFI - TIMEOUT")
            self.dfs_timeout = True
            return

        # Expandeaza nodul curent
        succesori = nod_curent.expandeaza()
        self.total_noduri_calculate += len(succesori)

        if not self.dfs_timeout:
            for succesor in succesori:
                self._ruleaza_dfi_recursiv(succesor, algoritm_start, adancime + 1, max_adancime=max_adancime)

    def rezolva_dfi(self):
        """Rezolva Problema data folosind un algoritm de tip DFI."""

        # Statistici
        algoritm_start = timer()

        # DFS
        nod_start = NodParcurgere(self.start, None, 0)
        self.numar_soareci_initial = len(nod_start.nod.harta.soareci)

        # Verificam (relativ naiv) daca se poate ajunge intr-un nod scop, numarand cati soareci pot ajunge la iesiri
        # si comparand cu k
        if not self.are_solutie(nod_start):
            self.lungime_drum = 0
            self.durata_algoritm = timer() - algoritm_start

            print(
                f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}DFI - NICIO SOLUTIE"
            )
            return

        self.total_noduri_calculate = 1
        self.dfs_timeout = False
        self.dfs_succes = False
        self.dfi_noduri_scop_excluse = []
        try:
            for i in range(1, 100):
                self._ruleaza_dfi_recursiv(nod_start, algoritm_start, max_adancime=i)
                if self.dfs_timeout or self.dfs_succes:
                    break
        except RecursionError:
            print(
                f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}DFI - STACK OVERFLOW"
            )

    def rezolva_a_star(self):
        """Rezolva Problema data folosind un algoritm de tip A*."""

        # Statistici
        algoritm_start = timer()

        # A*
        q = []
        nod_start = NodParcurgere(self.start, None, 0)
        self.numar_soareci_initial = len(nod_start.nod.harta.soareci)

        # Verificam (relativ naiv) daca se poate ajunge intr-un nod scop, numarand cati soareci pot ajunge la iesiri
        # si comparand cu k
        if not self.are_solutie(nod_start):
            self.lungime_drum = 0
            self.durata_algoritm = timer() - algoritm_start

            print(
                f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}A*, "
                f"euristica {euristica_to_str(self.euristica)} - NICIO SOLUTIE"
            )
            return

        # Posibil sa avem solutie. Continuam cu A*.

        q.append(nod_start)
        self.total_noduri_calculate = 1
        while q:
            # Statistici
            self.max_noduri_existente = max(self.max_noduri_existente, len(q))

            # Stergem si stocam ultimul element. Nu primul, deoarece q e sortat in ordinea inversa
            # necesara algoritmului - tocmai pentru a putea face pop() rapid
            nod_curent = q.pop()

            # Am gasit un nod scop
            if self.e_nod_scop(nod_curent.nod):
                self.afiseaza_solutie(nod_curent, algoritm_start, "A*")

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
                print(f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}A*, " +
                      f"euristica {euristica_to_str(self.euristica)} - TIMEOUT")
                return

            # Expandeaza nodul curent
            succesori = nod_curent.expandeaza()
            self.total_noduri_calculate += len(succesori)

            for succesor in succesori:
                nod_nou = succesor

                # Cautam succesor in q
                nod_in_q = self.cauta_nod_parcurgere(succesor, q)
                if nod_in_q is not None:
                    # Am gasit un drum mai bun catre succesor
                    if succesor.f < nod_in_q.f:
                        q.remove(nod_in_q)
                    else:
                        nod_nou = None

                if nod_nou is not None:
                    q.append(nod_nou)

            # Sorteaza invers criteriului algoritmului, pentru a putea face pop() rapid
            q.sort(key=self.sortare_open, reverse=True)

    def rezolva_a_star_optimizat(self):
        """Rezolva Problema data folosind un algoritm de tip A* optimizat."""

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
                f"euristica {euristica_to_str(self.euristica)} - NICIO SOLUTIE"
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
                self.afiseaza_solutie(nod_curent, algoritm_start, "A* optimizat")

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
                print(f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}A* optimizat, " +
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

    def _ruleaza_ida_star_recursiv(self, q: List[NodParcurgere], bound: int, algoritm_start):
        """
        Recursia unui algoritm IDA* ce rezolva Problema data.

        :param q: lista cu nodurile din parcurgerea curenta
        :param bound: costul maxim al unui nod permis in pasul curent al algoritmului
        :param algoritm_start: un timer cu momentul in care s-a inceput executia algoritmului
        """

        if self.ida_timeout or self.curr_sol >= self.n_sol:
            return

        # Statistici
        self.max_noduri_existente = max(self.max_noduri_existente, len(q))

        # Stergem si stocam ultimul element. Nu primul, deoarece q e sortat in ordinea inversa
        # necesara algoritmului - tocmai pentru a putea face pop() rapid
        nod_curent = q[-1]

        # Am gasit un nod scop
        if self.e_nod_scop(nod_curent.nod) and nod_curent.nod not in self.ida_star_noduri_scop_excluse:
            self.afiseaza_solutie(nod_curent, algoritm_start, "IDA*")
            self.ida_star_noduri_scop_excluse.append(nod_curent.nod)

            self.curr_sol += 1
            if self.curr_sol == self.n_sol or self.lungime_drum == 0:
                return
            else:
                self.output_file.close()
                self.output_file = open(f"{self.partial_output_filepath}-{self.curr_sol + 1}.out", "w")
                return

        f = nod_curent.g + nod_curent.nod.h
        if f > bound:
            self.min_exceeded_threshold = min(self.min_exceeded_threshold, f)
            return

        # Asigura-te ca nu s-a depasit timpul limita
        elapsed = timer() - algoritm_start
        if elapsed > self.timeout:
            print(f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}IDA*, " +
                  f"euristica {euristica_to_str(self.euristica)} - TIMEOUT")
            self.ida_timeout = True
            return

        # Expandeaza nodul curent
        succesori = nod_curent.expandeaza()
        self.total_noduri_calculate += len(succesori)

        for succesor in succesori:
            if self.cauta_nod_parcurgere(succesor, q) is None:
                q.append(succesor)
                self._ruleaza_ida_star_recursiv(q, bound, algoritm_start)
                q.pop()

        # Sorteaza invers criteriului algoritmului, pentru a putea face pop() rapid
        q.sort(key=self.sortare_open, reverse=True)

    def rezolva_ida_star(self):
        """Rezolva Problema data folosind un algoritm de tip IDA*."""

        # Statistici
        algoritm_start = timer()

        # IDA*
        q = []
        nod_start = NodParcurgere(self.start, None, 0)
        self.numar_soareci_initial = len(nod_start.nod.harta.soareci)

        # Verificam (relativ naiv) daca se poate ajunge intr-un nod scop, numarand cati soareci pot ajunge la iesiri
        # si comparand cu k
        if not self.are_solutie(nod_start):
            self.lungime_drum = 0
            self.durata_algoritm = timer() - algoritm_start

            print(
                f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}IDA*, "
                f"euristica {euristica_to_str(self.euristica)} - NICIO SOLUTIE"
            )
            return

        # Posibil sa avem solutie. Continuam cu IDA*.
        q.append(nod_start)
        bound = nod_start.nod.estimeaza_h(nod_start.nod.euristica)
        nod_start.nod.h = bound
        self.total_noduri_calculate = 1
        self.min_exceeded_threshold = float("inf")
        self.ida_timeout = False
        self.ida_star_noduri_scop_excluse = []
        while True:
            try:
                self._ruleaza_ida_star_recursiv(q, bound, algoritm_start)
                if self.curr_sol > 0 and self.lungime_drum == 0:
                    break
            except RecursionError:
                print(
                    f"{f'[{self.curr_sol + 1}/{self.n_sol}] ' if self.n_sol > 1 else ''}IDA*, "
                    f"euristica {euristica_to_str(self.euristica)} - STACK OVERFLOW"
                )
                break
            if self.ida_timeout or self.curr_sol >= self.n_sol:
                break
            bound = self.min_exceeded_threshold
            q = [nod_start]

    def __del__(self):
        self.output_file.close()

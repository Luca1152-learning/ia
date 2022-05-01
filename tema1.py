import copy
from collections import deque
from enum import Enum
from typing import List, Tuple


class Punct2D:
    def __init__(self, x: int, y: int):
        """
        Initializeaza un obiect de tip Punct2D.

        :param x: coordonata X a punctului
        :param y: coordonata Y a punctului
        """

        self.x = x
        self.y = y

    def distanta_squared(self, punct):
        return (self.x - punct.x) ** 2 + (self.y - punct.y) ** 2

    def distanta_coords_squared(self, x: int, y: int):
        return (self.x - x) ** 2 + (self.y - y) ** 2

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


# ----------------------------------------------------------------------------------------------

class EvenimentJoc(Enum):
    PISICA_MANCAT_SOARECE = 1
    SOARECE_ASCUNS = 2
    SOARECE_IESIT_HARTA = 3
    PISICA_BLOCATA = 4
    SOARECE_BLOCAT = 5


# ----------------------------------------------------------------------------------------------

class Harta:
    def __init__(self, harta: List[List[str]]):
        """
        Initializeaza un obiect de tip Harta.

        :param harta: matricea cu caractere, citita ca input
        """

        self.harta = harta
        self.pisici, self.soareci, self.ascunzisuri, self.iesiri = self.gaseste_puncte_speciale()
        self.evenimente = []  # Lista de obiecte de tip EvenimentJoc

    def gaseste_puncte_speciale(self) -> Tuple[List[Punct2D], List[Punct2D], List[Punct2D], List[Punct2D]]:
        """
        Identifica punctele speciale din harta (din matricea cu caractere) - pisicile, soarecii, asunzisurile
        libere si iesirile.

        :return: Un tuplu cu (pisici, soareci, ascunzisuri_libere, iesiri).
        """

        # Stocheaza pisicile + soarecii in dictionare pe masura ce sunt gasiti (fiind sortati ulterior)
        dict_pisici, dict_soareci = {}, {}
        ascunzisuri_libere, iesiri = [], []
        max_indice_soarece = -1
        for y, linie in enumerate(self.harta):
            for x, celula in enumerate(linie):
                if celula == "@":
                    ascunzisuri_libere.append(Punct2D(x, y))
                elif celula == "E":
                    iesiri.append(Punct2D(x, y))
                elif celula.startswith("p"):
                    indice = int(celula[1:])
                    dict_pisici[indice] = Punct2D(x, y)
                elif celula.startswith("s") or celula.startswith("S"):
                    indice = int(celula[1:])
                    dict_soareci[indice] = Punct2D(x, y)
                    max_indice_soarece = max(max_indice_soarece, indice)

        # Transforma dictionarele in liste, dupa ce sunt sortate entitatile dupa indici
        pisici = [value for key, value in sorted(dict_pisici.items())]
        # Totusi, e posibil ca unii soareci (poate de la mijloc) sa fi iesit deja de pe harta. In cazul asta, in lista,
        # pe pozitia lor, va fi None
        soareci = [None for _ in range(max_indice_soarece + 1)]
        for indice_soarece in range(max_indice_soarece + 1):
            if indice_soarece in dict_soareci:
                soareci[indice_soarece] = dict_soareci[indice_soarece]

        return pisici, soareci, ascunzisuri_libere, iesiri

    def muta_soarece(self, index_soarece: int, deplasament: Tuple[int, int], simuleaza: bool = False):
        """
        Muta un soarece pe harta (cu un deplasament considerat deja varificat a fi valid), actualizand harta
        (=matricea de caractere) corect.

        :param index_soarece: al catalea soarece sa fie mutat
        :param deplasament: cum sa isi modifice pozitia
        :param simuleaza: True daca vrem doar sa simulam ce s-ar intampla cu harta (fara sa modificam lista de entitati
        sau sa trimitem evenimentele) - util pentru a verifica daca o secventa de miscari a soarecilor e valida. Implicit
        False.
        """

        if self.soareci[index_soarece] is None:
            raise Exception(f"Soarecele {index_soarece} deja a iesit de pe harta.")

        soarece = self.soareci[index_soarece]

        # Actualizeaza pozitia veche de pe harta
        curr = self.harta[soarece.y][soarece.x]
        if curr.startswith("s"):
            # Soarecele nu e intr-un ascunzis, deci e intr-un loc liber
            self.harta[soarece.y][soarece.x] = "."
        elif curr.startswith("S"):
            # Ascunzisul a fost eliberat
            self.harta[soarece.y][soarece.x] = "@"

        # Aplica deplasament
        soarece.x += deplasament[0]
        soarece.y += deplasament[1]

        # Actualizeaza pozitia noua de pe harta
        nou = self.harta[soarece.y][soarece.x]
        if nou == ".":
            # Am ajuns intr-un loc liber
            self.harta[soarece.y][soarece.x] = f"s{index_soarece}"
        elif nou == "@":
            # Am ajuns intr-un ascunzis
            self.harta[soarece.y][soarece.x] = f"S{index_soarece}"
            if not simuleaza:
                self.evenimente.append({"tip": EvenimentJoc.SOARECE_ASCUNS, "id": index_soarece})
        elif nou == "E" and not simuleaza:
            self.evenimente.append({"tip": EvenimentJoc.SOARECE_IESIT_HARTA, "id": index_soarece})
            self.soareci[index_soarece] = None

        if deplasament == (0, 0) and not simuleaza:
            self.evenimente.append({"tip": EvenimentJoc.SOARECE_BLOCAT, "id": index_soarece})

    def e_celula_pe_harta(self, x: int, y: int):
        """
        Verifica daca coordonatele date se afla pe harta (si nu sunt in exteriorul ei).

        :param x: coordonata X a punctului verificat
        :param y: coordonata Y a punctului verificat
        :return: True daca punctul e pe harta, False altfel
        """

        return (0 <= y < len(self.harta)) and (0 <= x < len(self.harta[y]))

    def e_celula_accesibila_soarece(self, x: int, y: int):
        """
        Verifica daca un soarece se poate muta pe celula de la pozitia data.

        :param x: coordonata X a punctului verificat
        :param y: coordonata Y a punctului verificat
        :return: True daca un soarece se poate muta in punctul dat, False altfel
        """

        if not self.e_celula_pe_harta(x, y):
            return False

        celula = self.harta[y][x]
        return celula == "." or celula == "E" or celula == "@"

    def e_mutare_valida_soarece(self, index_soarece: int, deplasament: Tuple[int, int]) -> bool:
        """
        Verifica daca un soarece poate fi mutat pe harta, aplicandu-se deplasamentul dat. De exemplu,
        nu poti muta un soarece in afara hartii / pe o celula pe care e deja un soarece / pe un obstacol / etc.

        :param index_soarece: al catalea soarece sa fie mutat
        :param deplasament: cum sa isi modifice pozitia
        :return: True daca soarecele poate fi mutat cu deplasamentul dat, False altfel
        """

        if self.soareci[index_soarece] is None:
            raise Exception(f"Soarecele {index_soarece} deja a iesit de pe harta.")

        soarece = self.soareci[index_soarece]
        return self.e_celula_accesibila_soarece(soarece.x + deplasament[0], soarece.y + deplasament[1])

    def sunt_mutari_valide_soarece(self, deplasamente: List[Tuple[int, int]]) -> bool:
        """
        Verifica daca secventa de deplasamente poate fi aplicata pe soarecii cu indicii [0, len(deplasamente)].
        Astfel, dupa fiecare mutare valida, harta e modificata corespunzator si se continua cu urmatoarea mutare.
        La final, harta e resetata la starea initiala (aplicandu-se invers miscarile).

        :param deplasamente: lista cu deplasamentele care sa fie aplicate soarecilor cu indicii [0, len(deplasamente)]
        :return: True daca secventa de deplasamente e valida, False altfel
        """

        # Aplica deplasamentele (tinand cont de cate au fost aplicate)
        ultimul_deplasament_aplicat = -1
        for index_soarece, deplasament in enumerate(deplasamente):
            if not self.e_mutare_valida_soarece(index_soarece, deplasament):
                break

            self.muta_soarece(index_soarece, deplasament)
            ultimul_deplasament_aplicat = index_soarece

        # Restaureaza la loc harta (aplicand invers deplasamentele, de la ultimul aplicat la primul)
        for index_deplasament in reversed(range(0, ultimul_deplasament_aplicat + 1)):
            deplasament = deplasamente[index_deplasament]
            deplasament_negat = [-1 * deplasament[0], -1 * deplasament[1]]

            self.muta_soarece(index_deplasament, deplasament_negat)

        # Daca au fost aplicate toate deplasamentele, atunci toate mutarile au fost valide
        return ultimul_deplasament_aplicat == len(deplasamente) - 1

    def e_celula_accesibila_pisica(self, x: int, y: int):
        """
        Verifica daca o pisica se poate muta pe celula de la pozitia data.

        :param x: coordonata X a punctului verificat
        :param y: coordonata Y a punctului verificat
        :return: True daca o pisica se poate muta in punctul dat, False altfel
        """

        if not self.e_celula_pe_harta(x, y):
            return False

        celula = self.harta[y][x]
        return celula == "." or celula.startswith("s")

    def e_mutare_valida_pisica(self, index_pisica: int, deplasament: Tuple[int, int]) -> bool:
        """
        Verifica daca o pisica poate fi mutata pe harta, aplicandu-se deplasamentul dat. De exemplu,
        nu poti muta o pisica in afara hartii / pe o celula pe care e deja o pisica / pe un obstacol / etc.

        :param index_pisica: a cata pisica sa fie mutata
        :param deplasament: cum sa isi modifice pozitia
        :return: True daca pisica poate fi mutata cu deplasamentul dat, False altfel
        """

        pisica = self.pisici[index_pisica]
        return self.e_celula_accesibila_pisica(pisica.x + deplasament[0], pisica.y + deplasament[1])

    def muta_pisica(self, index_pisica, deplasament: Tuple[int, int]):
        """
        Muta o pisica pe harta (cu un deplasament considerat deja varificat a fi valid), actualizand harta
        (=matricea de caractere) corect.

        :param index_pisica: a cata pisica sa fie mutata
        :param deplasament: cum sa isi modifice pozitia
        """

        pisica = self.pisici[index_pisica]

        # Actualizeaza pozitia veche de pe harta
        # Dupa ce pleaca o pisica, in locul ei vechi sigur ramane spatiu liber
        self.harta[pisica.y][pisica.x] = "."

        # Aplica deplasament
        pisica.x += deplasament[0]
        pisica.y += deplasament[1]

        # Actualizeaza pozitia noua de pe harta
        nou = self.harta[pisica.y][pisica.x]
        if nou.startswith("s"):
            id_soarece = int(nou[1:])
            self.soareci[id_soarece] = None
            self.evenimente.append(
                {"tip": EvenimentJoc.PISICA_MANCAT_SOARECE, "id_pisica": index_pisica, "id_soarece": id_soarece}
            )
        # Oriunde ar ajunge pisica, punem "p[id pisica]"
        self.harta[pisica.y][pisica.x] = f"p{index_pisica}"

    def muta_pisici(self):
        """
        Muta pisicile, una cate una, catre pozitia optima acestora (folosind regulile date in enuntul problemei).
        """

        for index_pisica, pisica in enumerate(self.pisici):
            # Gasim cel mai apropiat soarece de pisica
            index_closest_soarece = -1
            distanta_closest_soarece = float("inf")
            for index_soarece, soarece in enumerate(self.soareci):
                # Soarecele a iesit deja de pe harta
                if soarece is None:
                    continue

                # Daca soarecele e ascuns, ignora-l
                if self.harta[soarece.y][soarece.x].startswith("S"):
                    continue

                distanta = pisica.distanta_squared(self.soareci[index_soarece])
                if distanta < distanta_closest_soarece:
                    index_closest_soarece = index_soarece
                    distanta_closest_soarece = distanta
            closest_soarece = self.soareci[index_closest_soarece] if index_closest_soarece != -1 else None

            # Gasim casuta valida vecina apropiata de cel mai apropiat soarece
            deplasament_best = None
            distanta_best = float("inf")
            deplasamente = [(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1)]
            for deplasament in deplasamente:
                if self.e_mutare_valida_pisica(index_pisica, deplasament):
                    # Nu exista niciun soarece la care se poate ajunge (neexistand soareci / toti fiind ascunsi).
                    # Atunci orice mutare valida e la fel de buna (pisicile ne mai vazand soarecii ascunsi).
                    # Nu putem sa stam pe loc daca exista miscari valide.
                    if closest_soarece is None:
                        deplasament_best = deplasament
                        break

                    distanta = closest_soarece.distanta_coords_squared(
                        pisica.x + deplasament[0], pisica.y + deplasament[1]
                    )
                    if distanta < distanta_best:
                        deplasament_best = deplasament
                        distanta_best = distanta_best
            # Permite pisicii sa stea pe loc daca nu are nicio miscare valida
            if deplasament_best is None:
                self.evenimente.append({"tip": EvenimentJoc.PISICA_BLOCATA, "id": index_pisica})
                deplasament_best = (0, 0)

            # Actualizam harta, mutand fizic pisica
            self.muta_pisica(index_pisica, deplasament_best)


# ----------------------------------------------------------------------------------------------


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

        return "Nods"


# ----------------------------------------------------------------------------------------------

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

    def expandeaza(self) -> List:
        # Genereaza toate combinatiile de deplasamente posibile pentru toti soarecii - folosind un fel de BFS,
        # pentru ca e mai usor de scris + nu e nevoie de recursie
        lista_deplasamente = deque([])
        while True:
            curr = lista_deplasamente.popleft() if len(lista_deplasamente) else []
            # Deplasamentul curent are [nr soareci] elemente => s-au generat toate combinatiile de deplasamente
            if len(curr) == len(self.nod.harta.soareci):
                # Adauga inapoi deplasamentul scos (deque nu are peek sau ceva, doar pop)
                lista_deplasamente.appendleft(curr)
                break

            adaugat_deplasament = False
            for deplasament in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                if self.nod.harta.sunt_mutari_valide_soarece(curr + [deplasament]):
                    lista_deplasamente.append(curr + [deplasament])
                    adaugat_deplasament = True
            # Soarecele de la indicele curent nu a putut fi mutat in nicio directie => sta pe loc.
            if not adaugat_deplasament:
                lista_deplasamente.append(curr + [(0, 0)])

        mutari = []
        for deplasamente in lista_deplasamente:
            nod_nou = copy.deepcopy(self.nod)
            for index, deplasament in enumerate(deplasamente):
                nod_nou.harta.muta_soarece(index, deplasament)
            nod_nou.harta.muta_pisici()

            # TODO self.g+1 posibil sa nu fie corect
            mutari.append(NodParcurgere(nod_nou, self, self.g + 1))

        return mutari

    def __repr__(self):
        return "NodParcurgere"


# ----------------------------------------------------------------------------------------------

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
            # if nod_curent.nod in self.scop:
            #     drum = []
            #
            #     nod_i = nod_curent
            #     while nod_i:
            #         drum.append(nod_i.nod)
            #         nod_i = nod_i.parinte
            #
            #     for nod in reversed(drum):
            #         print(nod.info)
            #
            #     return

            # Expandeaza nodul curent
            closed.append(nod_curent)  # Marcheaza-l ca expandat (punandu-l in closed)
            succesori = nod_curent.expandeaza()

            for succesor in succesori:
                pass
                # nod_nou = succesor
                #
                # # Cautam succesor in open
                # nod_in_open = self.cauta_nod_parcurgere(succesor, open)
                # if nod_in_open is not None:
                #     # Am gasit un drum mai bun catre succesor
                #     if succesor.f < nod_in_open.f:
                #         open.remove(nod_in_open)
                #     else:
                #         nod_nou = None
                #
                # # succesor a fost expandat in trecut
                # nod_in_closed = self.cauta_nod_parcurgere(succesor, closed)
                # if nod_in_closed:
                #     closed.remove(nod_in_closed)
                #     nod_nou = succesor
                #
                # if nod_nou is not None:
                #     open.append(nod_nou)
                #     # Sorteaza invers criteriului algoritmului, pentru a putea face pop() rapid
                #     open.sort(key=self.sortare_open, reverse=True)


# ----------------------------------------------------------------------------------------------

p = Problema("tema1-simplu.in")
p.rezolva()

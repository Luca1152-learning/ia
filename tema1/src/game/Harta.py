import collections
from typing import Tuple, List

from tema1.src.utils.EvenimentJoc import EvenimentJoc
from tema1.src.utils.Punct2D import Punct2D


class Harta:
    def __init__(self, harta: List[List[str]]):
        """
        Initializeaza un obiect de tip Harta.

        :param harta: matricea cu caractere, citita ca input
        """

        self.harta = harta
        self.pisici, self.soareci, self.ascunzisuri, self.iesiri = self.gaseste_puncte_speciale()
        self.soareci_iesiti = 0  # Cati soareci (in total) au iesit de pe harta (ajungand in 'E')
        self.evenimente = []  # Lista de obiecte de tip EvenimentJoc

        # Pentru calcularea costului mutarii
        self.soareci_prinsi = 0  # Cati soareci (in total) au fost prinsi de pisici
        self.soareci_prinsi_pas_curent = 0
        self.soareci_mutati_pas_curent = 0
        self.soarece_iesit_pas_curent = False

        # A doua euristica admisibila se foloseste de distantele reale (=numar corect de pasi) catre iesiri.
        # De asemenea, poate fi folosita pentru a determina daca exista solutii.
        # Matricea de distante va fi calculata o singura data, pentru nodul de start, restul de noduri fiind create folosind
        # copy.deepcopy().
        self.distante_reale_iesiri = self.calculeaza_distante_reale_iesiri()

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

    def calculeaza_distante_reale_iesiri(self) -> List[List[int]]:
        """TODO"""

        distante = [[float("inf") for _ in row] for row in self.harta]
        for iesire in self.iesiri:
            distante[iesire.y][iesire.x] = 0

        q = collections.deque()
        for iesire in self.iesiri:
            q.append((0, iesire.y, iesire.x))

        while q:
            dist, y, x = q.popleft()
            for (d_y, d_x) in [(1, 0), (0, -1), (-1, 0), (0, 1)]:
                dist_nou = dist + 1
                y_nou = y + d_y
                x_nou = x + d_x

                if not self.e_celula_pe_harta(x_nou, y_nou):
                    continue

                celula_noua = self.harta[y_nou][x_nou]
                # Orice celula diferita de zid e (posibil) accesibila de un soarece. Posibil pentru ca in locul respectiv
                # se poate sa fie deja un soarece / o pisica.
                e_celula_posibil_accesibila = celula_noua != "#"
                if e_celula_posibil_accesibila and dist_nou < distante[y_nou][x_nou]:
                    distante[y_nou][x_nou] = dist_nou
                    q.append((dist_nou, y_nou, x_nou))

        return distante

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
            self.soareci_iesiti += 1
            self.soarece_iesit_pas_curent = True

        if deplasament == (0, 0) and not simuleaza:
            self.evenimente.append({"tip": EvenimentJoc.SOARECE_BLOCAT, "id": index_soarece})
        elif deplasament != (0, 0) and not simuleaza:
            self.soareci_mutati_pas_curent += 1

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
        return (deplasament == (0, 0) or
                self.e_celula_accesibila_soarece(soarece.x + deplasament[0], soarece.y + deplasament[1]))

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
            # Soarecele de la indicele curent e prins/iesit => deplasamentul lui generat a fost () => il ignoram
            if deplasament == ():
                continue

            if not self.e_mutare_valida_soarece(index_soarece, deplasament):
                break

            self.muta_soarece(index_soarece, deplasament, simuleaza=True)
            ultimul_deplasament_aplicat = index_soarece

        # Restaureaza la loc harta (aplicand invers deplasamentele, de la ultimul aplicat la primul)
        for index_deplasament in reversed(range(0, ultimul_deplasament_aplicat + 1)):
            deplasament = deplasamente[index_deplasament]

            # Soarecele de la indicele curent e prins/iesit => deplasamentul lui generat a fost () => il ignoram
            if deplasament == ():
                continue

            deplasament_negat = [-1 * deplasament[0], -1 * deplasament[1]]

            self.muta_soarece(index_deplasament, deplasament_negat, simuleaza=True)

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
            self.soareci_prinsi += 1
            self.soareci_prinsi_pas_curent += 1
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
                        distanta_best = distanta
            # Permite pisicii sa stea pe loc daca nu are nicio miscare valida
            if deplasament_best is None:
                self.evenimente.append({"tip": EvenimentJoc.PISICA_BLOCATA, "id": index_pisica})
                deplasament_best = (0, 0)

            # Actualizam harta, mutand fizic pisica
            self.muta_pisica(index_pisica, deplasament_best)

    def animale_in_aceeasi_pozitie_ca_alta_harta(self, harta) -> bool:
        """TODO"""

        # Soareci
        if len(self.soareci) != len(harta.soareci):
            return False
        for index_pisica_self, soarece_self in enumerate(self.soareci):
            soarece_harta = harta.soareci[index_pisica_self]
            if soarece_self != soarece_harta:
                return False

        # Pisici
        if len(self.pisici) != len(harta.pisici):
            return False
        for index_pisica_self, pisica_self in enumerate(self.pisici):
            pisica_harta = harta.pisici[index_pisica_self]
            if pisica_self != pisica_harta:
                return False

        return True

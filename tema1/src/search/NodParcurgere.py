import copy
from collections import deque
from typing import List

from tema1.src.search.Nod import Nod


class NodParcurgere:
    def __init__(self, nod: Nod, parinte, g: int):
        """
        Initializeaza un obiect de tip NodParcurgere (folosit pentru a lega Nod-uri intre ele).

        :param nod: instanta de tip Nod pe care sa o infasoare NodParcurgere
        :param parinte: parintele Nod-ului din parcurgere
        :param g: costul necesar pentru a ajunge la nodul curent in parcurgere
        """

        self.nod = nod  # Referinta catre nodul propriu-zis
        self.parinte = parinte  # Parintele nodului din parcurgerea curenta
        self.g = g  # Adancimea (suma arcelor de la start la nodul dat)
        self.f = self.g + self.nod.h  # Functia folosita pentru compararea valorilor nodurilor

    def se_creeaza_circuit(self, nod: Nod) -> bool:
        """
        Verifica daca mai exista Nod-ul dat in parintii NodParcurgere-ului curent (creandu-se, astfel, un circuit).

        :param nod: Nodul de verificat
        :return: True daca se creeaza circuit, False altfel.
        """

        curr = self
        while curr is not None:
            if curr.nod == nod:
                return True
            curr = curr.parinte
        return False

    def expandeaza(self) -> List:
        """
        Genereaza o lista de Noduri Parcurgere ce sunt succesorii Nodului Parcurgere curent.

        :return: o lista cu toti succesori de tip NodParcurgere ai nodului curent.
        """

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

            id_soarece_de_mutat = len(curr)
            # Soarecele pe care vrem sa il mutam a fost prins de pisici / a iesit de pe harta
            if self.nod.harta.soareci[id_soarece_de_mutat] is None:
                lista_deplasamente.append(curr + [()])
                continue

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
            # Reseteaza campurile noului nod necesare
            nod_nou.harta.evenimente = []
            nod_nou.harta.soareci_prinsi_pas_curent = 0
            nod_nou.harta.soareci_mutati_pas_curent = 0
            nod_nou.harta.soarece_iesit_pas_curent = False
            if nod_nou.euristica is not None:
                nod_nou.h = nod_nou.estimeaza_h(nod_nou.euristica)

            # Muta animalele conform deplasamentelor
            mutat_soareci = False
            for index, deplasament in enumerate(deplasamente):
                # Soarecele pe care vrem sa il mutam a fost prins de pisici / a iesit de pe harta
                if nod_nou.harta.soareci[index] is None:
                    continue

                mutat_soareci = True
                nod_nou.harta.muta_soarece(index, deplasament)

            # Daca nu am mutat niciun soarece (fiind toti morti/iesiti de pe harta), inseamna ca mutarea curenta e nula,
            # deci nu o adaugam la mutari
            if not mutat_soareci:
                continue

            nod_nou.harta.muta_pisici()

            # Calculeaza costul mutarii (= ce trebuie adaugat la precedentul g)
            if nod_nou.harta.soarece_iesit_pas_curent:
                cost = 1
            elif nod_nou.harta.soareci_prinsi_pas_curent > 0:
                soareci = len(nod_nou.harta.soareci) - nod_nou.harta.soareci_iesiti - nod_nou.harta.soareci_prinsi + \
                          nod_nou.harta.soareci_prinsi_pas_curent
                cost = len(nod_nou.harta.pisici) * soareci
            else:
                cost = nod_nou.harta.soareci_mutati_pas_curent
            mutari.append(NodParcurgere(nod_nou, self, self.g + cost))

        return mutari

import copy
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Constante:
    # Cate niveluri are voie algoritmul sa extinda arborele de cautare
    MAX_ADANCIME_ARBORE = 5

    # Informatii despre joc
    DIMENSIUNE_HARTA = 3
    SIMBOLURI_JOC = ["X", "O"]
    JUCATOR_MAX = "O"
    JUCATOR_MIN = "X"
    GOL = " "


class Nod:
    # ^ o configuratie de joc (= un nod din graful jocului)

    def __init__(self, harta=None):
        self.harta = harta or [[Constante.GOL for _ in range(Constante.DIMENSIUNE_HARTA)] for _ in
                               range(Constante.DIMENSIUNE_HARTA)]

    def final(self):
        # Returneaza:
        # (1) Simbolul jucatorului ce a castigat
        # (2) "remiza", daca este remiza
        # (3) False, daca jocul nu s-a terminat

        # Verifica daca a castigat vreun jucator
        for jucator in Constante.SIMBOLURI_JOC:
            # Verifica linii
            for linie in self.harta:
                castigat_linie = True
                for casuta in linie:
                    if casuta != jucator:
                        castigat_linie = False
                        break
                if castigat_linie:
                    return jucator

            # Verifica coloane
            for j in range(Constante.DIMENSIUNE_HARTA):
                castigat_coloana = True
                for i in range(Constante.DIMENSIUNE_HARTA):
                    if self.harta[i][j] != jucator:
                        castigat_coloana = False
                        break
                if castigat_coloana:
                    return jucator

            # Verifica diagonala principala ( \ )
            castigat_diagonala_principala = True
            for i in range(Constante.DIMENSIUNE_HARTA):
                if self.harta[i][i] != jucator:
                    castigat_diagonala_principala = False
                    break
            if castigat_diagonala_principala:
                return jucator

            # Verifica diagonala secundara ( / )
            castigat_diagonala_secundara = True
            for i in range(Constante.DIMENSIUNE_HARTA):
                if self.harta[i][Constante.DIMENSIUNE_HARTA - 1 - i] != jucator:
                    castigat_diagonala_secundara = False
                    break
            if castigat_diagonala_secundara:
                return jucator

        # Verifica daca e remiza
        e_remiza = True
        for linie in self.harta:
            for casuta in linie:
                if casuta == Constante.GOL:
                    e_remiza = False
                    break
        if e_remiza:
            return "remiza"

        # Nu a castigat niciun jucator, nu e nici remiza => returnam False
        return False

    def succesori_nod(self, jucator):
        # Returneaza o lista de obiecte de tip Nod = toate configuratiile valide in care se poate ajunge
        # din 'self' dupa o mutare de-a lui 'jucator'

        succesori = []
        for i, linie in enumerate(self.harta):
            for j, casuta in enumerate(linie):
                # Cautam locurile in care jucatorul curent ar putea juca
                if casuta == Constante.GOL:
                    harta_noua = copy.deepcopy(self.harta)
                    harta_noua[i][j] = jucator
                    succesori.append(Nod(harta_noua))
        return succesori

    def estimeaza_scor(self, adancime):
        # Daca 'self' e configuratie finala de joc, atunci returneaza:
        #   0, daca jocul-a terminat cu „remiza"
        #   un numar foarte mare (> 0), daca a castigat JMAX
        #   un numar foarte mic (< 0), daca a castigat JMIN
        #
        # Ne putem folosi de adancime pentru a considera mai bune configuratiile de joc in care s-a castigat cu mai
        # putine mutari
        #
        # Daca 'self' nu e configuratie finala de joc:
        #   Returneaza (sanse de castig pentru JUCATOR MAX) - (sanse de castig pentru JUCATOR MIN)

        scor = 0

        # Numaram cate X-uri / O-uri sunt puse pe linii/coloane/diagonale de catre JUCATOR_MAX ce pot duce la o victorie
        # (adica nu sunt intrerupte de JUCATOR_MIN)

        # Verifica linii
        for linie in self.harta:
            scor_linie = 0
            for casuta in linie:
                if casuta == Constante.JUCATOR_MAX:
                    scor_linie += 1
                elif casuta == Constante.JUCATOR_MIN:
                    scor_linie = 0
                    break
            scor += scor_linie

        # Verifica coloane
        for j in range(Constante.DIMENSIUNE_HARTA):
            scor_coloana = 0
            for i in range(Constante.DIMENSIUNE_HARTA):
                if self.harta[i][j] == Constante.JUCATOR_MAX:
                    scor_coloana += 1
                elif self.harta[i][j] == Constante.JUCATOR_MIN:
                    scor_coloana = 0
                    break
            scor += scor_coloana

        # Verifica diagonala principala ( \ )
        scor_diagonala_principala = 0
        for i in range(Constante.DIMENSIUNE_HARTA):
            if self.harta[i][i] == Constante.JUCATOR_MAX:
                scor_diagonala_principala += 1
            elif self.harta[i][i] == Constante.JUCATOR_MIN:
                scor_diagonala_principala = 0
                break
        scor += scor_diagonala_principala

        # Verifica diagonala secundara ( / )
        scor_diagonala_secundara = 0
        for i in range(Constante.DIMENSIUNE_HARTA):
            casuta = self.harta[i][Constante.DIMENSIUNE_HARTA - 1 - i]
            if casuta == Constante.JUCATOR_MAX:
                scor_diagonala_secundara += 1
            elif casuta == Constante.JUCATOR_MIN:
                scor_diagonala_secundara = 0
                break
        scor += scor_diagonala_secundara

        # Adancime mai mare = mai buna, fiind mai greu de batut
        scor += adancime

        return scor

    def __str__(self):
        return "\n----------\n".join([" | ".join(linie) for linie in self.harta])


class NodParcurgere:
    # ^ nod din arborele de cautare al algoritmului

    def __init__(self, nod: Nod, jucator_curent, adancime, parinte=None, scor=None):
        self.nod = nod
        self.jucator_curent = jucator_curent
        self.adancime = adancime
        self.parinte = parinte
        self.scor = scor

        # Lista de mutari posibile din nodul parcurgere curent
        self.succesori = []

        # Cea mai buna mutare din lista de mutari pentru jucatorul curent
        self.succesor_ales = None

    def jucator_opus(self):
        # Returneaza simbolul jucatorului opus

        if self.jucator_curent == "X":
            return "O"
        else:
            return "X"

    def succesori_nod_parcurgere(self):
        # Returneaza o lista de obiecte de tip NodParcurgere, reprezentand toti fiii nodului 'self'

        succesori_nod = self.nod.succesori_nod(self.jucator_curent)
        succesori_nod_parcurgere = []
        for succesor_nod in succesori_nod:
            succesori_nod_parcurgere.append(
                NodParcurgere(succesor_nod, self.jucator_opus(), self.adancime + 1, self)
            )
        return succesori_nod_parcurgere

    def __str__(self):
        return f"NodParcurgere(scor={self.scor} adancime={self.adancime})"


class Joc:
    def minimax(self, nod_parcurgere: NodParcurgere):
        # Am ajuns la o frunza a arborelui. Adica:
        #   - Am expandat arborele pana la adancimea maxima permisa
        #   - Sau am ajuns intr-o configuratie finala de joc (unul dintre jucatori a castigat / e remiza)
        if nod_parcurgere.adancime == Constante.MAX_ADANCIME_ARBORE or nod_parcurgere.nod.final():
            # Calculam scorul frunzei (pentru a ne folosi de el recursiv, in calculul scorurilor nodurilor interne)
            nod_parcurgere.scor = nod_parcurgere.nod.estimeaza_scor(nod_parcurgere.adancime)
            return nod_parcurgere

        # Nu am ajuns intr-o frunza => vom expanda nodul
        nod_parcurgere.succesori = nod_parcurgere.succesori_nod_parcurgere()

        # Aplic algoritmul Minimax pe toate mutarile posibile (calculand, astfel, toti subarborii)
        nod_parcurgere_mutari = []
        for nod_parcurgere_mutare in nod_parcurgere.succesori:
            nod_parcurgere_mutari.append(self.minimax(nod_parcurgere_mutare))

        if nod_parcurgere.jucator_curent == Constante.JUCATOR_MAX:
            # Jucatorul MAX (= A.I.-ul) alege nodul parcurgere fiu cu scorul maxim
            nod_parcurgere.succesor_ales = max(nod_parcurgere_mutari, key=lambda x: x.scor)
        else:
            # Jucatorul MIN (omul) alege nodul parcurgere fiu cu scorul minim
            nod_parcurgere.succesor_ales = min(nod_parcurgere_mutari, key=lambda x: x.scor)

        # Scorul nodului parcurgere curent este scorul nodului parcurgere fiu ales
        nod_parcurgere.scor = nod_parcurgere.succesor_ales.scor

        return nod_parcurgere

    def alpha_beta(self, nod_parcurgere: NodParcurgere, alpha=float("-inf"), beta=float("inf")):
        # Am ajuns la o frunza a arborelui. Adica:
        #   - Am expandat arborele pana la adancimea maxima permisa
        #   - Sau am ajuns intr-o configuratie finala de joc (unul dintre jucatori a castigat / e remiza)
        if nod_parcurgere.adancime == 0 or nod_parcurgere.nod.final():
            # Calculam scorul frunzei (pentru a ne folosi de el recursiv, in calculul scorurilor nodurilor interne)
            nod_parcurgere.scor = nod_parcurgere.nod.estimeaza_scor(nod_parcurgere.adancime)
            return nod_parcurgere

        # Conditie de retezare - nu mai continuam cu generarea succesorilor
        if alpha >= beta:
            return nod_parcurgere

        # Nu am ajuns intr-o frunza => vom expanda nodul
        nod_parcurgere.succesori = nod_parcurgere.succesori_nod_parcurgere()

        if nod_parcurgere.jucator_curent == Constante.JUCATOR_MAX:
            # Jucatorul MAX (= A.I.-ul) alege nodul parcurgere fiu cu scorul maxim

            scor_max = float("-inf")
            for succesor in nod_parcurgere.succesori:
                # Calculeaza scorul succesorului curent
                succesor_evaluat = self.alpha_beta(succesor, alpha, beta)

                # Incerc sa imbunatatesc scorul nodului curent
                if succesor_evaluat.scor > scor_max:
                    scor_max = succesor_evaluat.scor
                    nod_parcurgere.succesor_ales = succesor_evaluat

                if succesor_evaluat.scor > alpha:
                    alpha = succesor_evaluat.scor
                    # Verificam daca, dupa evaluarea asta, realizam ca putem face o retezare (oprind evaluarea celorlalti copii)
                    if alpha >= beta:
                        break
        else:
            # Jucatorul MIN (omul) alege nodul parcurgere fiu cu scorul minim

            scor_min = float("inf")
            for succesor in nod_parcurgere.succesori:
                # Calculeaza scorul succesorului curent
                succesor_evaluat = self.alpha_beta(succesor, alpha, beta)

                # Incerc sa imbunatatesc scorul nodului curent
                if succesor_evaluat.scor < scor_min:
                    scor_min = succesor_evaluat.scor
                    nod_parcurgere.succesor_ales = succesor_evaluat

                if succesor_evaluat.scor < beta:
                    alpha = succesor_evaluat.scor
                    # Verificam daca, dupa evaluarea asta, realizam ca putem face o retezare (oprind evaluarea celorlalti copii)
                    if alpha >= beta:
                        break

        # Scorul nodului parcurgere curent este scorul nodului parcurgere fiu ales
        nod_parcurgere.scor = nod_parcurgere.succesor_ales.scor

        return nod_parcurgere

    @staticmethod
    def afiseaza(nod_start: NodParcurgere):
        prev = None
        curr = nod_start
        while True:
            print(curr.nod)
            print()

            prev = curr
            curr = curr.succesor_ales
            if curr is None:
                break
        print("wa")
        print(prev.succesori_nod_parcurgere())


joc = Joc()
nod_curent = NodParcurgere(Nod(), "X", 0)

while True:
    if not nod_curent.nod.final():
        print(f"[Randul lui {nod_curent.jucator_curent}]")
    print(nod_curent.nod)
    if nod_curent.nod.final():
        break

    if nod_curent.jucator_curent == "X":
        while True:
            casuta = int(input(f"Alege o casuta (1-{Constante.DIMENSIUNE_HARTA * Constante.DIMENSIUNE_HARTA}): ")) - 1
            if not 0 <= casuta < Constante.DIMENSIUNE_HARTA * Constante.DIMENSIUNE_HARTA:
                continue

            i, j = int(casuta / Constante.DIMENSIUNE_HARTA), casuta % Constante.DIMENSIUNE_HARTA
            harta_noua = copy.deepcopy(nod_curent.nod.harta)
            if harta_noua[i][j] != Constante.GOL:
                continue
            harta_noua[i][j] = "X"

            nod_curent = NodParcurgere(Nod(harta_noua), "O", 0)
            break
    else:
        calculat = joc.minimax(nod_curent)
        nod_curent = NodParcurgere(Nod(calculat.succesor_ales.nod.harta), "X", 0)

    print()

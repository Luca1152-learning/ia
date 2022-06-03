import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Nod:
    # ^ o configuratie de joc (= un nod din graful jocului)

    def final(self):
        # Returneaza:
        # (1) Simbolul jucatorului ce a castigat
        # (2) "remiza", daca este remiza
        # (3) False, daca jocul nu s-a terminat

        pass

    def mutari_joc(self, jucator):
        # Returneaza o lista de obiecte de tip Joc = toate configuratiile valide in care se poate ajunge
        # din 'self' dupa o mutare de-a lui 'jucator'

        pass

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

        pass

    def __str__(self):
        return "Nod"


class NodParcurgere:
    # ^ nod din arborele de cautare al algoritmului

    def __init__(self, nod: Nod, jucator_curent, adancime, parinte=None, score=None):
        self.nod = nod
        self.jucator_curent = jucator_curent
        self.adancime = adancime
        self.parinte = parinte
        self.scor = score

        # Lista de mutari posibile din starea curenta
        self.succesori = []

        # Cea mai buna mutare din lista de mutari pentru jucatorul curent
        self.succesor_ales = None

    def jucator_opus(self):
        # Returneaza simbolul jucatorului opus

        pass

    def succesori_nod_parcurgere(self):
        # Returneaza o lista de obiecte de tip Stare, reprezentand toti fiii nodului 'self'
        pass

    def __str__(self):
        return "NodParcurgere"


class Joc:
    # Date statice cu informatii despre joc ce nu se modifica (NR_LINII, NR_COLOANE, etc)

    ARBORE_MAX = 5  # Cate niveluri are voie algoritmul sa extinda arborele de cautare
    JUCATOR_MAX = 0
    JUCATOR_MIN = 1

    def __init__(self):
        pass

    def minimax(self, nod_parcurgere: NodParcurgere):
        # Am ajuns la o frunza a arborelui. Adica:
        #   - Am expandat arborele pana la adancimea maxima permisa
        #   - Sau am ajuns intr-o configuratie finala de joc (unul dintre jucatori a castigat / e remiza)
        if nod_parcurgere.adancime == 0 or nod_parcurgere.nod.final():
            # Calculam scorul frunzei (pentru a ne folosi de el recursiv, in calculul scorurilor nodurilor interne)
            nod_parcurgere.scor = nod_parcurgere.nod.estimeaza_scor(nod_parcurgere.adancime)
            return nod_parcurgere

        # Nu am ajuns intr-o frunza => vom expanda nodul
        nod_parcurgere.succesori = nod_parcurgere.succesori_nod_parcurgere()

        # Aplic algoritmul Minimax pe toate mutarile posibile (calculand, astfel, toti subarborii)
        nod_parcurgere_mutari = []
        for nod_parcurgere_mutare in nod_parcurgere.succesori:
            nod_parcurgere_mutari.append(self.minimax(nod_parcurgere_mutare))

        if nod_parcurgere.jucator_curent == Joc.JUCATOR_MAX:
            # Jucatorul MAX (= A.I.-ul) alege starea fiica cu scorul maxim
            nod_parcurgere.succesor_ales = max(nod_parcurgere_mutari, key=lambda x: x.scor)
        else:
            # Jucatorul MIN (omul) alege starea fiica cu scorul minim
            nod_parcurgere.succesor_ales = min(nod_parcurgere_mutari, key=lambda x: x.scor)

        # Scorul nodului parcurgere curent este scorul nodului parcurgere fiu ales
        nod_parcurgere.scor = nod_parcurgere.succesor_ales.scor

        return nod_parcurgere

    def alpha_beta(self, nod_parcurgere: NodParcurgere, alpha: int, beta: int):
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

        if nod_parcurgere.jucator_curent == Joc.JUCATOR_MAX:
            # Jucatorul MAX (= A.I.-ul) alege starea fiica cu scorul maxim

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
            # Jucatorul MIN (omul) alege starea fiica cu scorul minim

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

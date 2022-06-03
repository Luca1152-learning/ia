import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# Un nod din *arborele de cautare* al jocului
class Stare:
    ADANCIME_MAX = 9

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, scor=None):
        self.tabla_joc = tabla_joc  # Un obiect de tip Joc => tabla_joc.matr
        self.j_curent = j_curent  # # Simbolul jucatorului curent

        # Adancimea in arborele de stari (scade cu cate o unitate din „tata” in „fiu”)
        self.adancime = adancime

        # Scorul starii (daca e finala, adica frunza a arborelui) sau scorul celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # Lista de mutari posibile din starea curenta
        self.mutari_posibile = []  # Lista va contine obiecte de tip Stare

        # Cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def jucator_opus(self):
        pass

    def mutari_stare(self):
        pass

    def __str__(self):
        pass


# Configuratie de joc (un nod din *graful* jocului)
class Joc:
    NR_LINII = 3
    NR_COLOANE = 3
    SIMBOLURI_JOC = ["X", "O"]
    JMAX = "X"
    JMIN = "O"
    GOL = " "

    def __init__(self, tabla=None):
        self.matrice = tabla or [[Joc.GOL for _ in Joc.NR_COLOANE] for _ in Joc.NR_LINII]

    def final(self):
        # Verifica daca a castigat vreun jucator
        for jucator in Joc.SIMBOLURI_JOC:
            # Verifica linii
            for line in self.matrice:
                castigat_linie = True
                for line_cell in line:
                    if line_cell != jucator:
                        castigat_linie = False
                        break
                if castigat_linie:
                    return jucator

            # Verifica coloane
            for j in range(Joc.NR_COLOANE):
                for i in range(Joc.NR_LINII):
                    pass

            # Verifica diagonale

        return False

    def mutari_joc(self, jucator):
        pass

    def estimeaza_scor(self, adancime):
        pass

    def __str__(self):
        pass


def min_max(stare):
    pass


def alpha_beta(alpha, beta, stare):
    pass

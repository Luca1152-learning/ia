import os
import random
import time

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def clamp(value, min_value, max_value):
    return min(max(value, min_value), max_value)


class Elev:
    necunoscuti = 0

    def __init__(self, nume=None, sanatate=90, inteligenta=20, oboseala=0, buna_dispozitie=100, lista_activitati=None):
        if nume:
            self.nume = nume
        else:
            Elev.necunoscuti += 1
            self.nume = "Necunoscut_" + str(Elev.necunoscuti)

        self.sanatate = sanatate
        self.inteligenta = inteligenta
        self.oboseala = oboseala
        self.buna_dispozitie = buna_dispozitie
        self.lista_activitati = lista_activitati

        self.activitate_curenta = None
        self.timp_executat_activ = 0

        self.raport = {}

        self.activitate_curenta = random.choice(self.lista_activitati)

    def desfasoara_activitate(self, activitate):
        self.activitate_curenta = activitate
        self.timp_executat_activ = 0

    def trece_ora(self, ora):
        if self.timp_executat_activ >= self.activitate_curenta.durata:
            self.desfasoara_activitate(random.choice(self.lista_activitati))

        activitate = self.activitate_curenta

        multiplicator_oboseala = 1
        if self.oboseala == 100:
            multiplicator_oboseala = 0.5

        self.timp_executat_activ += 1
        self.sanatate = clamp(
            self.sanatate + multiplicator_oboseala * activitate.factor_sanatate / activitate.durata, 0, 100
        )
        self.inteligenta = clamp(
            self.inteligenta + multiplicator_oboseala * activitate.factor_inteligenta / activitate.durata, 0, 100
        )
        self.oboseala = clamp(
            self.oboseala + multiplicator_oboseala * activitate.factor_oboseala / activitate.durata, 0, 100
        )
        self.buna_dispozitie = clamp(
            self.buna_dispozitie + multiplicator_oboseala * activitate.factor_dispozitie / activitate.durata, 0, 100
        )

        if ora >= 22 or ora <= 6:
            self.sanatate = clamp(self.sanatate - 1, 0, 100)

        if activitate not in self.raport:
            self.raport[activitate.nume] = 0
        self.raport[activitate.nume] = self.timp_executat_activ

    def testeaza_final(self):
        return self.inteligenta == 100 or self.sanatate == 0 or self.buna_dispozitie == 0

    def afiseaza_raport(self):
        for key, value in self.raport.items():
            print(f"{key}: {value} ore")

    def stats(self):
        return f"(snt: {self.sanatate}, intel: {self.inteligenta}, obos: {self.oboseala}, dispoz: {self.buna_dispozitie})"

    def __repr__(self):
        return f"{self.nume} {self.stats()}"


class Activitate:
    def __init__(self, nume, factor_sanatate, factor_inteligenta, factor_oboseala, factor_dispozitie, durata):
        self.nume = nume
        self.factor_sanatate = factor_sanatate
        self.factor_inteligenta = factor_inteligenta
        self.factor_oboseala = factor_oboseala
        self.factor_dispozitie = factor_dispozitie
        self.durata = durata

    @staticmethod
    def read_from_file(filename):
        activitati = []
        with open(filename) as f:
            f.readline()  # ignora antetul

            for line in f:
                nume, factor_sanatate, factor_inteligenta, factor_oboseala, factor_dispozitie, durata = line.split()
                activitati.append(Activitate(nume, int(factor_sanatate), int(factor_inteligenta), int(factor_oboseala),
                                             int(factor_dispozitie), int(durata)))
        return activitati


def porneste_simulare():
    ora = 9

    while True:
        # Activitati curente
        print("Activitati curente:")
        for elev in elevi:
            print(f"{elev}: {elev.activitate_curenta.nume}")
        print()

        # Input
        print("comanda = ", end="")
        text = input()

        if text == "gata":
            return
        elif text == "continua":
            for elev in elevi:
                if elev.testeaza_final():
                    if elev.inteligenta == 100:
                        print(f"{elev.nume}: absolvit")
                    else:
                        print(f"{elev.nume}: bolnav")
                elev.afiseaza_raport()
        else:
            nr_ore = int(text)

            while nr_ore != 0:
                print(f"Ora {ora}:00")
                for elev in elevi:
                    if not elev.testeaza_final():
                        elev.trece_ora(ora)

                        if elev.testeaza_final():
                            if elev.inteligenta == 100:
                                print(f"{elev.nume}: absolvit! :D")
                            else:
                                print(f"{elev.nume}: bolnav! :(")

                        # Afisare
                        activitate = elev.activitate_curenta
                        print(
                            f"{elev.nume} {activitate.nume} {elev.timp_executat_activ}/{activitate.durata} {elev.stats()}")
                print()

                ora = ora + 1
                if ora == 25:
                    ora = 1

                nr_ore -= 1
                if nr_ore >= 1:
                    time.sleep(1)
            print()


activitati = Activitate.read_from_file(os.path.join(__location__, "lab1.in"))

# invatat, citit, relaxare, citit, citit
activitati_elev = [activitati[0], activitati[7], activitati[8], activitati[7], activitati[7]]
elev = Elev("Ion", 100, 70, 0, 90, activitati_elev)

elevi = [elev]

porneste_simulare()

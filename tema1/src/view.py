import argparse
import re
from typing import List, Tuple

from tema1.src.game.Harta import Harta


def setup_cli():
    """Initializeaza Command Line Interface-ul, fiind punctul de start al programului."""

    parser = argparse.ArgumentParser(description="Vizualizeaza rezultatul problemei 'Șoareci și pisici'.")
    parser.add_argument("-i", "--input", metavar="PATH",
                        help="calea absoluta catre fisierul de input", required=True)

    args = parser.parse_args()

    with open(args.input) as f:
        pasi = imparte_in_pasi(f.read())

        # Obtine mutarile
        mutari = []
        for index in range(1, len(pasi)):
            mutari.append(parseaza_mutari_animale(pasi[index - 1], pasi[index]))

        # Animeaza mutarile in pygame
        animeaza_mutari(pasi[0][0], mutari)


def imparte_in_pasi(raw_input: str) -> List[Tuple[Harta, List[str]]]:
    """TODO"""

    pasi_raw = raw_input.split("\n\n")
    pasi = []
    for pas_raw in pasi_raw:
        # Ignora prima linie, cu indicele pasului si cu valoarea lui g
        lines = pas_raw.split("\n")[1:]

        # Am ajuns la sfarsitul fisierului
        if lines == []:
            break

        raw_map, evenimente = None, []
        for index, line in enumerate(lines):
            if line.startswith("Soarece") or line.startswith("Pisica"):
                raw_map = lines[:index]
                evenimente = lines[index:]
                break
        # Nu am dat break in for => nu avem evenimente => harta este data de toate liniile
        else:
            raw_map = lines

        # Imparte harta in celule
        raw_map = [line.split() for line in raw_map]

        pasi.append((Harta(raw_map), evenimente))
    return pasi


def parseaza_mutari_animale(
        pas_prev: Tuple[Harta, List[str]], pas_curr: Tuple[Harta, List[str]]
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """TODO"""

    mutari_soareci, mutari_pisici = {}, {}

    # Pasi
    map_prev, _ = pas_prev
    map_curr, evenimente_curr = pas_curr

    # Gaseste deplasamente soareci inca pe harta
    for i in range(min(len(map_prev.soareci), len(map_curr.soareci))):
        if map_prev.soareci[i] and map_curr.soareci[i]:
            depl_x, depl_y = map_curr.soareci[i].x - map_prev.soareci[i].x, map_curr.soareci[i].y - map_prev.soareci[
                i].y
            if not (depl_x == 0 and depl_y == 0):
                mutari_soareci[i] = (depl_x, depl_y)

    # Gaseste deplasamente pisici
    for i in range(len(map_curr.pisici)):
        if map_prev.pisici[i] and map_curr.pisici[i]:
            mutari_pisici[i] = (
                map_curr.pisici[i].x - map_prev.pisici[i].x, map_curr.pisici[i].y - map_prev.pisici[i].y
            )

    for eveniment in evenimente_curr:
        # Gaseste deplasamente soareci prinsi de pisici
        soarece_prins = re.search("Pisica p(\d+) a mancat soarecele s(\d+).", eveniment)
        if soarece_prins:
            id_pisica, id_soarece = int(soarece_prins.group(1)), int(soarece_prins.group(2))
            soarece, pisica = map_prev.soareci[id_soarece], map_curr.pisici[id_pisica]

            # Pisica a prins soarecele, deci soarecele s-a mutat unde e pisica acum
            mutari_soareci[id_soarece] = (pisica.x - soarece.x, pisica.y - soarece.y)

        # Gaseste deplasamente soareci iesiti de pe harta
        soarece_iesit = re.search("Soarecele s(\d+) a iesit de pe harta.", eveniment)
        if soarece_iesit:
            id_soarece = int(soarece_iesit.group(1))
            soarece = map_prev.soareci[id_soarece]

            for deplasament in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = soarece.x + deplasament[0], soarece.y + deplasament[1]
                if map_prev.e_celula_accesibila_soarece(new_x, new_y) and map_prev.harta[new_y][new_x] == "E":
                    mutari_soareci[id_soarece] = deplasament
                    break

    return (mutari_soareci, mutari_pisici)


def animeaza_mutari(harta_initiala: Harta, mutari: Tuple[Tuple[int, int], Tuple[int, int]]):
    """TODO"""

    pass


setup_cli()

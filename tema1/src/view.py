import argparse
import math
import re
from typing import List, Tuple, Dict

import pygame
from pygame import RLEACCEL

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
) -> Tuple[Dict[int, Tuple[int, int]], Dict[int, Tuple[int, int]]]:
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

    return mutari_soareci, mutari_pisici


def animeaza_mutari(harta_initiala: Harta, mutari: List[Tuple[Dict[int, Tuple[int, int]], Dict[int, Tuple[int, int]]]]):
    """TODO"""

    # PyGame window
    pygame.init()
    win = pygame.display.set_mode((48 * len(harta_initiala.harta[0]), 48 * len(harta_initiala.harta)))
    pygame.display.set_caption("Animație a problemei 'șoareci și pisici'")

    # Creeaza sprites
    grup_obstacole, grup_ascunzatori, grup_iesiri = creeaza_sprites_statice(harta_initiala)
    soareci, grup_soareci, pisici, grup_pisici = creeaza_sprites_dinamice(harta_initiala)

    last_movement_index = 0
    last_mouse_movement_index = 0
    mouse_to_move_id = list(mutari[last_movement_index][0].items())[last_mouse_movement_index][0]
    last_cat_movement_index = -1
    cat_to_move_id = 0
    soareci[0].smoothly_move_to(
        soareci[0].rect.x / TILE_SIZE + mutari[last_movement_index][0][mouse_to_move_id][0],
        soareci[0].rect.y / TILE_SIZE + mutari[last_movement_index][0][mouse_to_move_id][1]
    )

    run = True
    while run:
        pygame.time.delay(100)

        # Verifica daca butonul de X a fost apasat
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Planifica noi mutari
        # Muta soarecii
        if not soareci[mouse_to_move_id].is_moving and last_mouse_movement_index < len(
                mutari[last_movement_index][0]) - 1:
            last_mouse_movement_index += 1
            mouse_to_move_id = list(mutari[last_movement_index][0].items())[last_mouse_movement_index][0]
            soareci[mouse_to_move_id].smoothly_move_to(
                soareci[mouse_to_move_id].rect.x / TILE_SIZE + mutari[last_movement_index][0][mouse_to_move_id][0],
                soareci[mouse_to_move_id].rect.y / TILE_SIZE + mutari[last_movement_index][0][mouse_to_move_id][1]
            )
        # Verifica daca ultimul soarece a ajuns intr-un punct de iesire
        if (mouse_to_move_id > -1 and not soareci[mouse_to_move_id].is_moving and
                harta_initiala.harta[int(soareci[mouse_to_move_id].rect.y / TILE_SIZE)][
                    int(soareci[mouse_to_move_id].rect.x / TILE_SIZE)] == "E"):
            soareci[mouse_to_move_id].kill()
        # Muta pisicile, daca s-au mutat toti soarecii
        if (last_mouse_movement_index == len(mutari[last_movement_index][0]) - 1 and
                not soareci[mouse_to_move_id].is_moving and
                last_cat_movement_index < len(mutari[last_movement_index][1]) - 1):
            last_cat_movement_index += 1
            cat_to_move_id = list(mutari[last_movement_index][1].items())[last_cat_movement_index][0]
            pisici[cat_to_move_id].smoothly_move_to(
                pisici[cat_to_move_id].rect.x / TILE_SIZE + mutari[last_movement_index][1][cat_to_move_id][0],
                pisici[cat_to_move_id].rect.y / TILE_SIZE + mutari[last_movement_index][1][cat_to_move_id][1]
            )
        # Verifica daca ultima pisica a prins un soarece
        if cat_to_move_id > -1 and not pisici[cat_to_move_id].is_moving:
            for soarece in soareci:
                if soarece.rect.x == pisici[cat_to_move_id].rect.x and soarece.rect.y == pisici[cat_to_move_id].rect.y:
                    soarece.kill()
        # Trece la urmatorul pas, daca s-au mutat toate pisicile si toti soarecii de la pasul curent:
        if (last_mouse_movement_index == len(mutari[last_movement_index][0]) - 1 and last_cat_movement_index == len(
                mutari[last_movement_index][1]) - 1 and not pisici[
            cat_to_move_id].is_moving and last_movement_index < len(mutari) - 1):
            last_movement_index += 1
            mouse_to_move_id = -1
            last_mouse_movement_index = -1
            cat_to_move_id = -1
            last_cat_movement_index = -1

        # Update
        grup_obstacole.update()
        grup_ascunzatori.update()
        grup_iesiri.update()
        grup_soareci.update()
        grup_pisici.update()

        # Render
        win.fill((77, 146, 98))
        grup_obstacole.draw(win)
        grup_ascunzatori.draw(win)
        grup_iesiri.draw(win)
        grup_soareci.draw(win)
        grup_pisici.draw(win)
        pygame.display.update()


def creeaza_sprites_statice(harta_initiala: Harta):
    """TODO"""

    obstacole, ascunzatori, iesiri = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

    for y, line in enumerate(harta_initiala.harta):
        for x, cell in enumerate(line):
            if cell == "#":
                obstacole.add(Obstacol(x, y))
            elif cell == "@" or cell.startswith("S"):
                ascunzatori.add(Ascunzatoare(x, y))
            elif cell == "E":
                iesiri.add(Iesire(x, y))

    return obstacole, ascunzatori, iesiri


def creeaza_sprites_dinamice(harta_initiala: Harta):
    """TODO"""

    soareci, pisici = [], []
    grup_soareci, grup_pisici = pygame.sprite.Group(), pygame.sprite.Group()

    for soarece in harta_initiala.soareci:
        sprite = Soarece(soarece.x, soarece.y)
        soareci.append(sprite)
        grup_soareci.add(sprite)

    for pisica in harta_initiala.pisici:
        sprite = Pisica(pisica.x, pisica.y)
        pisici.append(sprite)
        grup_pisici.add(sprite)

    return soareci, grup_soareci, pisici, grup_pisici


# Sprites
TILE_SIZE = 48


def sign(x):
    """TODO"""

    return math.copysign(1, x)


class StaticSprite(pygame.sprite.Sprite):
    def __init__(self, img_src: str, map_x: int, map_y: int):
        """TODO"""

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(img_src).convert_alpha()
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = TILE_SIZE * map_x, TILE_SIZE * map_y

    def sprite_pos_to_map_pos(self):
        return self.rect.x / TILE_SIZE, self.rect.y / TILE_SIZE


class Obstacol(StaticSprite):
    def __init__(self, map_x: int, map_y: int):
        """TODO"""

        StaticSprite.__init__(self, "sprites/obstacol.png", map_x, map_y)


class Ascunzatoare(StaticSprite):
    def __init__(self, map_x: int, map_y: int):
        """TODO"""

        StaticSprite.__init__(self, "sprites/ascunzatoare.png", map_x, map_y)


class Iesire(StaticSprite):
    def __init__(self, map_x: int, map_y: int):
        """TODO"""

        StaticSprite.__init__(self, "sprites/iesire.png", map_x, map_y)


class DynamicSprite(StaticSprite):
    def __init__(self, img_src, initial_map_x: int, initial_map_y: int):
        """TODO"""

        StaticSprite.__init__(self, img_src, initial_map_x, initial_map_y)
        self.target_x, self.target_y = None, None
        self.is_moving = False

    def smoothly_move_to(self, map_target_x, map_target_y):
        self.target_x = TILE_SIZE * map_target_x
        self.target_y = TILE_SIZE * map_target_y
        self.is_moving = True

    def update(self):
        if self.target_y is not None and self.target_y is not None:
            if self.rect.x != self.target_x or self.rect.y != self.target_y:
                self.rect.x += 12 * sign(self.target_x - self.rect.x)
                self.rect.y += 12 * sign(self.target_y - self.rect.y)
            else:
                self.target_x = self.target_y = None
                self.is_moving = False


class Soarece(DynamicSprite):
    def __init__(self, initial_map_x: int, initial_map_y: int):
        """TODO"""

        DynamicSprite.__init__(self, "sprites/soarece.png", initial_map_x, initial_map_y)


class Pisica(DynamicSprite):
    def __init__(self, initial_map_x: int, initial_map_y: int):
        """TODO"""

        DynamicSprite.__init__(self, "sprites/pisica.png", initial_map_x, initial_map_y)


setup_cli()

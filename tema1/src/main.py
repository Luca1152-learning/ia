import argparse
import os
from pathlib import Path

from tema1.src.game.Problema import Problema
from tema1.src.search.Euristica import Euristica, euristica_to_str


def input_valid(raw_data: str) -> bool:
    """TODO"""

    lines = raw_data.split("\n")
    valid = True

    # Verifica corectitudinea lui k
    if lines[0].isnumeric():
        k = int(lines[0])
    else:
        k = 0
        print("[!!] Eroare: k trebuie sa fie un numar.")
        valid = False

    map = [line.split(" ") for line in lines[1:]]

    # Verifica lungimile liniilor
    lungime = len(map[0])
    for index, line in enumerate(map[1:]):
        if len(line) != lungime:
            print(f"[!!] Eroare: lungimea liniei {index + 2} este prea {'mare' if len(line) > lungime else 'mica'}")
            valid = False

    # Verifica indicii pisicilor
    pisici = []
    for line in map:
        for cell in line:
            if cell.startswith("p"):
                pisici.append(int(cell[1:]))
    pisici.sort()
    if pisici and pisici[0] != 0:
        pisici = [-1] + pisici
    for index in range(1, len(pisici)):
        pisica = pisici[index]
        if pisica != pisici[index - 1] + 1:
            for index_lipsa in range(pisici[index - 1] + 1, pisica):
                print(f"[!!] Eroare: lipseste pisica {index_lipsa}")
                valid = False

    # Verifica indicii soarecilor
    soareci = []
    for line in map:
        for cell in line:
            if cell.startswith("s") or cell.startswith("S"):
                soareci.append(int(cell[1:]))
    soareci.sort()
    if soareci and soareci[0] != 0:
        soareci = [-1] + soareci
    for index in range(1, len(soareci)):
        soarece = soareci[index]
        if soarece != soareci[index - 1] + 1:
            for index_lipsa in range(soareci[index - 1] + 1, soarece):
                print(f"[!!] Eroare: lipseste soarecele {index_lipsa}")
                valid = False

    # Compara numarul de soareci cu k
    if len(soareci) < k:
        print(f"[!!] Eroare: k este mai mare decat numarul de soareci de pe harta")
        valid = False

    # Asigura-te ca toate caracterele de pe harta sunt valide
    for line in map:
        for cell in line:
            if cell not in [".", "@", "#", "E"] and not ((cell.startswith("s") or cell.startswith("S") or
                                                          cell.startswith("p")) and cell[1:].isnumeric()):
                print(f"[!!] Eroare: simboulul '{cell}' de pe harta este invalid")
                valid = False
    if not valid:
        print()

    return valid


def setup_cli():
    """TODO"""

    parser = argparse.ArgumentParser(description="Rezolva problema 'Șoareci și pisici'.")
    parser.add_argument("-i", "--input", metavar="PATH",
                        help="calea absoluta catre folderul de input", required=True)
    parser.add_argument("-o", "--output", metavar="PATH",
                        help="calea absoluta catre folderul de output", required=True)
    parser.add_argument("-n", metavar="SOLUTIONS", type=int,
                        help="numarul de solutii de calculat", required=True)
    parser.add_argument("-t", "--timeout", metavar="S", type=float,
                        help="timpul de timeout per solutie, in secunde", required=True)

    args = parser.parse_args()

    # TODO check if the paths (input & output) are valid
    for input_file_name in sorted(os.listdir(args.input)):
        # TODO use path.join
        input_file_path = args.input + "/" + input_file_name
        file_name = str(Path(input_file_name).stem)

        print(f"[{file_name}]")
        with open(input_file_path) as f:
            if not input_valid(f.read()):
                continue

        # BFS
        p = Problema(input_file_path, f"{args.output}/{file_name}-bfs", args.timeout, args.n)
        p.rezolva_bfs()

        # DFS
        p = Problema(input_file_path, f"{args.output}/{file_name}-dfs", args.timeout, args.n)
        p.rezolva_dfs()

        # DFI
        p = Problema(input_file_path, f"{args.output}/{file_name}-dfi", args.timeout, args.n)
        p.rezolva_dfi()

        # A*
        for euristica in Euristica:
            p = Problema(
                input_file_path, f"{args.output}/{file_name}-a*-{euristica_to_str(euristica)}", args.timeout,
                args.n, euristica
            )
            p.rezolva_a_star()

        # A* optimizat
        for euristica in Euristica:
            p = Problema(
                input_file_path, f"{args.output}/{file_name}-a*-opt-{euristica_to_str(euristica)}", args.timeout,
                args.n, euristica
            )
            p.rezolva_a_star_optimizat()

        # IDA*
        for euristica in Euristica:
            p = Problema(
                input_file_path, f"{args.output}/{file_name}-ida*-{euristica_to_str(euristica)}", args.timeout,
                args.n, euristica
            )
            p.rezolva_ida_star()

        print()


setup_cli()

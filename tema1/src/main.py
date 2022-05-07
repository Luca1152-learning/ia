import argparse
import os
from pathlib import Path

from tema1.src.game.Problema import Problema
from tema1.src.search.Euristica import Euristica


def euristica_to_str(euristica: Euristica):
    if euristica == Euristica.BANALA:
        return "banala"
    elif euristica == Euristica.ADMISIBILA1:
        return "admisibila1"
    elif euristica == Euristica.ADMISIBILA2:
        return "admisibila2"
    elif euristica == Euristica.NEADMISIBILA:
        return "neadmisibila"


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
    for input_file_name in os.listdir(args.input):
        # TODO use path.join
        input_file_path = args.input + "/" + input_file_name
        file_name = str(Path(input_file_name).stem)

        for euristica in Euristica:
            p = Problema(input_file_path, f"{args.output}/{file_name}-{euristica_to_str(euristica)}.out", euristica)
            p.rezolva()


setup_cli()

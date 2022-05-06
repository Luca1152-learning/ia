import argparse
import os
from pathlib import Path

from tema1.src.game.Problema import Problema


def setup_cli():
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

    for input_file_name in os.listdir(args.input):
        input_file_path = args.input + "/" + input_file_name
        file_name = str(Path(input_file_name).stem)
        p = Problema(input_file_path, args.output + "/" + file_name + "-output.out")
        p.rezolva()


setup_cli()

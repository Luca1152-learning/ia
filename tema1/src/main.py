import os

from tema1.src.game.Problema import Problema

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = Problema(parent_dir + "/input/simplu.in", parent_dir + "/output/simplu-output.out")
p.rezolva()

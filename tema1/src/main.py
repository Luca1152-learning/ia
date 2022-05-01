import os

from tema1.src.game.Problema import Problema

p = Problema(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/input/simplu.in")
p.rezolva()

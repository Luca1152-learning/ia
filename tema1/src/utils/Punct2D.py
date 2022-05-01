class Punct2D:
    def __init__(self, x: int, y: int):
        """
        Initializeaza un obiect de tip Punct2D.

        :param x: coordonata X a punctului
        :param y: coordonata Y a punctului
        """

        self.x = x
        self.y = y

    def distanta_squared(self, punct):
        return (self.x - punct.x) ** 2 + (self.y - punct.y) ** 2

    def distanta_coords_squared(self, x: int, y: int):
        return (self.x - x) ** 2 + (self.y - y) ** 2

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

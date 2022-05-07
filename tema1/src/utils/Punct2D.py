class Punct2D:
    def __init__(self, x: int, y: int):
        """
        Initializeaza un obiect de tip Punct2D.

        :param x: coordonata X a punctului
        :param y: coordonata Y a punctului
        """

        self.x = x
        self.y = y

    def distanta_squared(self, punct) -> float:
        """
        Calculeaza distanta (euclidiana) dintre punctul curent si cel dat ca parametru. Rezultatul va fi distanta
        la patrat. Util pentru comparatii - pentru a nu mai plati si costul unui sqrt.

        :param punct: punctul fata de care sa se calculeze distanta de la punctul curent
        :return: d(self, punct)^2
        """

        return self.distanta_coords_squared(punct.x, punct.y)

    def distanta_coords_squared(self, x: int, y: int):
        """
        Calculeaza distanta (euclidiana) dintre punctul curent si cel dat ca parametru. Rezultatul va fi distanta
        la patrat. Util pentru comparatii - pentru a nu mai plati si costul unui sqrt.

        :param x: coordonata x a punctului fata de care sa se calculeze distanta de la punctul curent
        :param y: coordonata y a punctului fata de care sa se calculeze distanta de la punctul curent
        :return: d((self.x, self.y), (x, y))^2
        """

        return (self.x - x) ** 2 + (self.y - y) ** 2

    def distanta_manhattan(self, punct) -> int:
        """
        Calculeaza distanta Manhattan dintre punctul curent sic el dat ca parametru.

        :param punct: punctul fata de care sa se calculeze distanta de la punctul curent
        :return: d_manhattan(self, punct)
        """

        return abs(self.x - punct.x) + abs(self.y - punct.y)

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

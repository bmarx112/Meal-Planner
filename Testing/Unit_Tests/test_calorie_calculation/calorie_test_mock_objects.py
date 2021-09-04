

class TestPerson:

    def __init__(self,
                 weight: float,
                 height: float,
                 age: float,
                 gender: str = None) -> None:
        self.weight = weight
        self.height = height
        self.age = age
        self.gender = gender
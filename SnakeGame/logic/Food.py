import random


class Food:
    def getPosition(self):
        return self.position

    def relocate(self):
        self.position['x'] = random.randrange(0, 400, 20)
        self.position['y'] = random.randrange(0, 400, 20)

    def __init__(self):
        self.position = {'x': 0, 'y': 0}
        self.relocate()
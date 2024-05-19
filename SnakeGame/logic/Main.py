from SnakeGame.logic import Snake, Food

class Main:
    def __init__(self, state=None):
        if state:
            self.snakeControl = Snake(state['snake'][0])
            self.snakeControl.segments = state['snake']
            self.snakeControl.direction = state['direction']
            self.food = Food()
            self.food.position = state['food']
            self.score = state['score']
        else:
            self.snakeControl = Snake({'x': 200, 'y': 200})
            self.food = Food()
            self.score = 0

    def update(self):
        head = self.snakeControl.move()
###
        if head == self.food.getPosition():
            self.food.relocate()
            self.snakeControl.grow()
            self.score += 10
        else:
            self.snakeControl.popTail()

        if self.hit():
            self.snakeControl = None

    def hit(self):
        head = self.snakeControl.getSegments()[0]
        if head['x'] < 0 or head['x'] >= 400 or head['y'] < 0 or head['y'] >= 400:
            return True
        for segment in self.snakeControl.getSegments()[1:]:
            if head == segment:
                return True
        return False

    def gameOver(self):
        return self.snakeControl is None

    def changeDirection(self, direction):
        self.snakeControl.changeDirection(direction)

    def getState(self):
        return {
            'snake': self.snakeControl.getSegments(),
            'food': self.food.getPosition(),
            'score': self.score,
            'direction': self.snakeControl.direction
        }

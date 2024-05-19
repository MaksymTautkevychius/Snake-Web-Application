class Snake:
    def __init__(self, position):
        self.segments = [position]
        self.direction = 'LEFT'

    def move(self):
        head = dict(self.segments[0])
        if self.direction == 'LEFT':
            head['x'] -= 20
        elif self.direction == 'DOWN':
            head['y'] += 20
        elif self.direction == 'UP':
             head['y'] -= 20
        elif self.direction == 'RIGHT':
            head['x'] += 20
        self.segments.insert(0, head)
        return head

    def grow(self):
        self.segments.append(self.segments[-1])

    def popTail(self):
        self.segments.pop()

    def getSegments(self):
        return self.segments

    def changeDirection(self, direction):
        if direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            if (direction == 'UP' and self.direction != 'DOWN') or \
               (direction == 'DOWN' and self.direction != 'UP') or \
               (direction == 'LEFT' and self.direction != 'RIGHT') or \
               (direction == 'RIGHT' and self.direction != 'LEFT'):
                self.direction = direction
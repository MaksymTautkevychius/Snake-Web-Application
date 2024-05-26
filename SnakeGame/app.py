from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import random

app = Flask(__name__)

client = MongoClient('mongodb+srv://s26871:6v442fClsJtgXt3t@snakecluster.httdehw.mongodb.net/?retryWrites=true&w=majority&appName=SnakeCluster')
db = client['SnakeDB']
score_collection = db['scores4']

class Food:
    def __init__(self, map_size):
        self.map_size = map_size
        self.relocate()

    def relocate(self):
        self.position = {
            'x': random.randint(0, self.map_size - 1),
            'y': random.randint(0, self.map_size - 1)
        }

    def get_position(self):
        return self.position

class Snake:
    def __init__(self, initial_position):
        self.segments = [initial_position]
        self.direction = 'LEFT'

    def move(self):
        head = self.segments[0].copy()
        if self.direction == 'LEFT':
            head['x'] -= 1
        elif self.direction == 'RIGHT':
            head['x'] += 1
        elif self.direction == 'UP':
            head['y'] -= 1
        elif self.direction == 'DOWN':
            head['y'] += 1
        self.segments.insert(0, head)
        return head

    def grow(self):
        self.segments.append(self.segments[-1])

    def pop_tail(self):
        self.segments.pop()

    def get_segments(self):
        return self.segments

    def change_direction(self, direction):
        if direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            if (direction == 'UP' and self.direction != 'DOWN') or \
               (direction == 'DOWN' and self.direction != 'UP') or \
               (direction == 'LEFT' and self.direction != 'RIGHT') or \
               (direction == 'RIGHT' and self.direction != 'LEFT'):
                self.direction = direction

class SnakeGame:
    def __init__(self, map_size, state=None):
        self.map_size = map_size
        if state:
            self.snake = Snake(state['snake'][0])
            self.snake.segments = state['snake']
            self.snake.direction = state['direction']
            self.food = Food(self.map_size)
            self.food.position = state['food']
            self.score = state['score']
        else:
            initial_position = {'x': map_size // 2, 'y': map_size // 2}
            self.snake = Snake(initial_position)
            self.food = Food(self.map_size)
            self.score = 0

    def update(self):
        head = self.snake.move()

        if head == self.food.get_position():
            self.food.relocate()
            while self.food.get_position() in self.snake.get_segments():
                self.food.relocate()
            self.snake.grow()
            self.score += 1
        else:
            self.snake.pop_tail()

        if self.WallHit() or self.SnakeHit():
            self.snake = None

    def WallHit(self):
        head = self.snake.get_segments()[0]
        return head['x'] < 0 or head['x'] >= self.map_size or head['y'] < 0 or head['y'] >= self.map_size

    def SnakeHit(self):
        head = self.snake.get_segments()[0]
        return head in self.snake.get_segments()[1:]

    def TheEnd(self):
        return self.snake is None

    def ChangeDir(self, direction):
        self.snake.change_direction(direction)

    def CheckTheState(self):
        return {
            'snake': self.snake.get_segments(),
            'food': self.food.get_position(),
            'score': self.score,
            'direction': self.snake.direction
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game_state', methods=['POST'])
def GetState():
    data = request.get_json()
    action = data.get('action')
    if action == 'start':
        map_size = data.get('map_size')
        game = SnakeGame(map_size)
        return jsonify(game.CheckTheState()), 200
    elif action == 'move':
        game_state = data.get('game_state')
        direction = data.get('direction')
        game = SnakeGame(game_state['map_size'], state=game_state)
        game.ChangeDir(direction)
        game.update()
        if game.TheEnd():
            return jsonify({'game_over': True, 'score': game.score}), 200
        else:
            return jsonify(game.CheckTheState()), 200

@app.route('/SaveScore', methods=['POST'])
def Saves():
    data = request.get_json()
    name = data.get('name')
    MapSize = data.get('MapSize')
    score = data.get('score')
    if name and score is not None:
        score_collection.insert_one({'name': name, 'mapSize': MapSize, 'score': score})
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 400

if __name__ == '__main__':
    app.run(debug=True)
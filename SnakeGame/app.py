from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from logic.Snake import Snake
from logic.Food import Food

app = Flask(__name__)

client = MongoClient('mongodb+srv://s26871:6v442fClsJtgXt3t@snakecluster.httdehw.mongodb.net/?retryWrites=true&w=majority&appName=SnakeCluster')
db = client['SnakeDB']
score_collection = db['scores2']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game_state', methods=['POST'])
def GameGil():
    data = request.get_json()
    action = data.get('action')
    if action == 'start':
        game = SnakeGame()
        return jsonify(game.get_state()), 200
    elif action == 'move':
        game_state = data.get('game_state')
        direction = data.get('direction')
        game = SnakeGame(state=game_state)
        game.change_direction(direction)
        game.update()
        if game.GameOver():
            return jsonify({'game_over': True, 'score': game.score}), 200
        else:
            return jsonify(game.get_state()), 200

@app.route('/SaveScore', methods=['POST'])
def save_score():
    data = request.get_json()
    name = data.get('name')
    score = data.get('score')
    if name and score is not None:
        score_collection.insert_one({'name': name, 'score': score})
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 400

class SnakeGame:
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

        if head == self.food.get_position():
            self.food.relocate()
            self.snakeControl.grow()
            self.score += 10
        else:
            self.snakeControl.pop_tail()

        if self.hit():
            self.snakeControl = None

    def hit(self):
        head = self.snakeControl.get_segments()[0]
        if head['x'] < 0 or head['x'] >= 400 or head['y'] < 0 or head['y'] >= 400:
            return True
        for segment in self.snakeControl.get_segments()[1:]:
            if head == segment:
                return True
        return False

    def is_game_over(self):
        return self.snakeControl is None

    def change_direction(self, direction):
        self.snakeControl.change_direction(direction)

    def get_state(self):
        return {
            'snake': self.snakeControl.get_segments(),
            'food': self.food.get_position(),
            'score': self.score,
            'direction': self.snakeControl.direction
        }

if __name__ == '__main__':
    app.run(debug=True)

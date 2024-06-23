from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import random

app = Flask(__name__)

client = MongoClient(
    'mongodb+srv://s26871:6v442fClsJtgXt3t@snakecluster.httdehw.mongodb.net/?retryWrites=true&w=majority&appName=SnakeCluster')
db = client['SnakeDB']
collection = db['testProject']

# Constants
GRID_SIZE = 32
CELL_SIZE = 10

# Game state
State = {
    "player_pos": GRID_SIZE // 2,
    "aliens": [],
    "bullets": [],
    "total_destroyed": 0,
    "game_over": False
}


def CreateMob():
    return {
        "x": random.randint(0, GRID_SIZE - 1),
        "y": GRID_SIZE - 1
    }


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/start_game', methods=['POST'])
def Start():
    global State
    State = {
        "player_pos": GRID_SIZE // 2,
        "aliens": [CreateMob() for _ in range(5)],
        "bullets": [],
        "total_destroyed": State["total_destroyed"],
        "game_over": False
    }
    return jsonify(State)


@app.route('/move_player', methods=['POST'])
def MoveLeftRight():
    global State
    direction = request.json.get('direction')
    if direction == 'left' and State["player_pos"] > 0:
        State["player_pos"] -= 1
    elif direction == 'right' and State["player_pos"] < GRID_SIZE - 1:
        State["player_pos"] += 1

    State["bullets"].append({"x": State["player_pos"], "y": 0})

    return jsonify(State)


@app.route('/update_game', methods=['POST'])
def UpdateGame():
    global State
    if not State["game_over"]:
        new_aliens = []
        for alien in State["aliens"]:
            alien_hit = False
            for bullet in State["bullets"]:
                if bullet["x"] == alien["x"] and bullet["y"] == alien["y"]:
                    collection.insert_one({'count': 1})
                    State["total_destroyed"] += 1
                    alien_hit = True
                    break

            if not alien_hit:
                if alien["y"] > 0:
                    alien["y"] -= 1
                    new_aliens.append(alien)
                else:
                    collection.insert_one({'count': 1})
                    State["total_destroyed"] += 1
                    State["game_over"] = True

        while len(new_aliens) < len(State["aliens"]):
            new_aliens.append(CreateMob())

        State["aliens"] = new_aliens

        State["bullets"] = [{"x": bullet["x"], "y": bullet["y"] + 1} for bullet in State["bullets"]]
        State["bullets"] = [bullet for bullet in State["bullets"] if bullet["y"] < GRID_SIZE]

        if State["game_over"]:
            SaveScore(State["total_destroyed"])

    return jsonify(State)


@app.route('/get_total_destroyed', methods=['GET'])
def SendTotal():
    total_destroyed = sum([doc['count'] for doc in collection.find()])
    return jsonify({'total_destroyed': total_destroyed})


def SaveScore(score):
    collection.insert_one({'total_destroyed': score})


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

# --- Initial game state ---
def create_initial_state():
    return {
        "players": [
            {"name": "Knight", "score": 0, "position": 0, "icon": "♞", "color": "#c00"},
            {"name": "Archer", "score": 0, "position": 0, "icon": "🏹", "color": "#0c0"},
            {"name": "Mage", "score": 0, "position": 0, "icon": "🪄", "color": "#00c"}
        ],
        "current_turn_index": 0,
        "board_size": 20,
        "messages": ["⚔️ Welcome to Medieval Mayhem! Roll the dice to begin your quest!"],
        "winner": None
    }

# --- Game state ---
game_state = create_initial_state()

# --- Game functions ---
def drawBoard():
    return [{"index": i, "type": "normal"} for i in range(game_state["board_size"])]

def rollDice():
    return random.randint(1, 6)

def movePlayer(player, steps):
    player["position"] += steps
    
    # Check if player reached the end
    if player["position"] >= game_state["board_size"] - 1:
        player["position"] = game_state["board_size"] - 1
        game_state["messages"].append(f"🏰 {player['name']} has reached the Castle Gate!")
        game_state["winner"] = player
        return True
    
    handleTileEvent(player)
    return False

def handleTileEvent(player):
    pos = player["position"]
    # Simple events for demo
    if pos % 5 == 0 and pos != 0:
        player["score"] += 5
        game_state["messages"].append(f"💰 {player['name']} found a Treasure Chest! +5 points")
    elif pos % 7 == 0 and pos != 0:
        player["score"] -= 3
        game_state["messages"].append(f"🗡️ {player['name']} fell into a Trap! -3 points")
    else:
        game_state["messages"].append(f"👣 {player['name']} advances through the realm...")

def nextTurn():
    game_state["current_turn_index"] = (game_state["current_turn_index"] + 1) % len(game_state["players"])

def getGameState():
    return {
        "players": game_state["players"],
        "current_player": game_state["players"][game_state["current_turn_index"]]["name"],
        "board": drawBoard(),
        "messages": game_state["messages"][-10:],  # last 10 messages
        "winner": game_state["winner"]
    }

# --- Flask routes ---
@app.route("/")
def index():
    return render_template("index.html", board_size=game_state["board_size"])

@app.route("/state")
def state():
    return jsonify(getGameState())

@app.route("/roll", methods=['POST'])
def roll():
    # Don't allow rolling if there's a winner
    if game_state["winner"]:
        return jsonify({"roll": 0, "error": "Game is over"})
    
    player = game_state["players"][game_state["current_turn_index"]]
    dice = rollDice()
    
    game_won = movePlayer(player, dice)
    
    if not game_won:
        nextTurn()
    
    return jsonify({"roll": dice})

@app.route("/reset", methods=['POST'])
def reset():
    global game_state
    game_state = create_initial_state()
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
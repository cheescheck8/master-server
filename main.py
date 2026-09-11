from flask import Flask, request, jsonify
import time

app = Flask(name)
rooms = {}
ROOM_TIMEOUT = 15

@app.route('/create_room', methods=['POST'])
def create_room():
    data = request.json
    host_ip = request.remote_addr
    room_id = f"{host_ip}:{data.get('port', 4242)}"
    
    rooms[room_id] = {
        "id": room_id,
        "name": data.get("name", "Unnamed Room"),
        "ip": host_ip,
        "port": data.get("port", 4242),
        "has_password": data.get("has_password", False),
        "max_players": data.get("max_players", 8),
        "current_players": 1,
        "round_time": data.get("round_time", 300),
        "map": data.get("map", "Default"),
        "time_of_day": data.get("time_of_day", "Day"),
        "last_ping": time.time()
    }
    return jsonify({"status": "success", "room_id": room_id})

@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    current_time = time.time()
    active_rooms = []
    expired = []
    for r_id, room in rooms.items():
        if current_time - room["last_ping"] > ROOM_TIMEOUT:
            expired.append(r_id)
        else:
            active_rooms.append(room)
    for r_id in expired:
        del rooms[r_id]
    return jsonify(active_rooms)

@app.route('/ping_room', methods=['POST'])
def ping_room():
    data = request.json
    r_id = data.get("room_id")
    if r_id in rooms:
        rooms[r_id]["last_ping"] = time.time()
        rooms[r_id]["current_players"] = data.get("current_players", 1)
        return jsonify({"status": "ok"})
    return jsonify({"status": "not_found"}), 404

if name == 'main':
    app.run(host='0.0.0.0', port=5000)

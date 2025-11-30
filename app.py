from flask import Flask, render_template, jsonify, request, send_from_directory
import database
import os

app = Flask(__name__)

# Ensure DB is initialized on start
if not os.path.exists(database.DB_PATH):
    database.init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/games', methods=['GET'])
def get_games():
    conn = database.get_db_connection()
    games = conn.execute('SELECT * FROM games').fetchall()
    conn.close()
    return jsonify([dict(g) for g in games])

@app.route('/api/games', methods=['POST'])
def add_game():
    data = request.json
    name = data.get('name')
    map_path = data.get('map_path')
    
    if not name or not map_path:
        return jsonify({'error': 'Name and map_path required'}), 400
        
    conn = database.get_db_connection()
    cursor = conn.execute('INSERT INTO games (name, map_path) VALUES (?, ?)', (name, map_path))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'name': name, 'map_path': map_path})


@app.route('/api/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    conn = database.get_db_connection()
    # Ensure game exists
    game = conn.execute('SELECT * FROM games WHERE id = ?', (game_id,)).fetchone()
    if not game:
        conn.close()
        return jsonify({'error': 'Game not found'}), 404

    # Delete markers for the game
    conn.execute('DELETE FROM markers WHERE game_id = ?', (game_id,))
    # Delete the game itself
    conn.execute('DELETE FROM games WHERE id = ?', (game_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/markers/<game_id>', methods=['GET'])
def get_markers(game_id):
    conn = database.get_db_connection()
    markers = conn.execute('SELECT * FROM markers WHERE game_id = ?', (game_id,)).fetchall()
    conn.close()
    return jsonify([dict(m) for m in markers])

import time

def save_image(file):
    if not file:
        return ''
    filename = f"{int(time.time())}_{file.filename}"
    filepath = os.path.join('static', 'uploads', filename)
    file.save(filepath)
    return f"/static/uploads/{filename}"

@app.route('/api/markers', methods=['POST'])
def add_marker():
    # Handle FormData
    data = request.form
    image_file = request.files.get('image_file')
    image_path = save_image(image_file)
    
    conn = database.get_db_connection()
    cursor = conn.execute('''
        INSERT INTO markers (game_id, lat, lng, title, note, type, game_coords, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['game_id'], 
        data['lat'], 
        data['lng'], 
        data.get('title', ''), 
        data.get('note', ''), 
        data.get('type', 'default'),
        data.get('game_coords', ''),
        image_path
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'status': 'success'})

@app.route('/api/markers/<int:marker_id>', methods=['PUT'])
def update_marker(marker_id):
    data = request.form
    image_file = request.files.get('image_file')
    
    conn = database.get_db_connection()
    
    if image_file:
        image_path = save_image(image_file)
        conn.execute('''
            UPDATE markers 
            SET title = ?, note = ?, type = ?, game_coords = ?, image_path = ?
            WHERE id = ?
        ''', (
            data.get('title', ''), 
            data.get('note', ''), 
            data.get('type', 'default'),
            data.get('game_coords', ''),
            image_path,
            marker_id
        ))
    else:
        conn.execute('''
            UPDATE markers 
            SET title = ?, note = ?, type = ?, game_coords = ?
            WHERE id = ?
        ''', (
            data.get('title', ''), 
            data.get('note', ''), 
            data.get('type', 'default'),
            data.get('game_coords', ''),
            marker_id
        ))
        
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/markers/<int:marker_id>', methods=['DELETE'])
def delete_marker(marker_id):
    conn = database.get_db_connection()
    conn.execute('DELETE FROM markers WHERE id = ?', (marker_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# Route to serve map images from the 'maps' directory
@app.route('/maps/<path:filename>')
def serve_map(filename):
    return send_from_directory('maps', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

import app
from flask import request, jsonify
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'teacher').strip().lower()
    email = data.get('email', '').strip() or None
    full_name = data.get('full_name', '').strip() or None

    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    if role not in app.VALID_ROLES:
        return jsonify({'error': f'role must be one of {app.VALID_ROLES}'}), 400

    app.c = app.cur()
    if role == 'admin':
        app.c.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'admin'")
        if app.c.fetchone()['count'] > 0:
            return jsonify({'error': 'Admin account already exists'}), 403

    password_hash = generate_password_hash(password)
    try:
        app.c.execute(
            "INSERT INTO users (username, password_hash, role, email, full_name) VALUES (%s, %s, %s, %s, %s)",
            (username, password_hash, role, email, full_name),
        )
        app.mysql.connection.commit()
    except Exception:
        return jsonify({'error': 'Username or email already exists'}), 409

    return jsonify({'message': 'User registered', 'role': role}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    app.c = app.cur()
    app.c.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = app.c.fetchone()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    try:
        valid_password = check_password_hash(user.get('password_hash', ''), password)
    except ValueError:
        valid_password = False

    if not valid_password:
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity=user['username'])
    return jsonify({'access_token': token, 'token_type': 'bearer', 'role': user['role']}), 200


@app.route('/auth/me', methods=['GET'])
@jwt_required()
def profile():
    user = app.get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user), 200
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
import MySQLdb.cursors


def cur():
    from app import mysql
    return mysql.connection.cursor(MySQLdb.cursors.DictCursor)


def grade_for(marks):
    if marks >= 90:
        return 'A+'
    if marks >= 80:
        return 'A'
    if marks >= 70:
        return 'B+'
    if marks >= 60:
        return 'B'
    if marks >= 50:
        return 'C'
    if marks >= 40:
        return 'D'
    return 'F'


def grade_points_for(marks):
    if marks >= 90:
        return 4.0
    if marks >= 80:
        return 4.0
    if marks >= 70:
        return 3.5
    if marks >= 60:
        return 3.0
    if marks >= 50:
        return 2.0
    if marks >= 40:
        return 1.0
    return 0.0


def gpa_for(records):
    total_points = 0.0
    total_credits = 0.0
    for row in records:
        try:
            marks = float(row.get('marks', 0) or 0)
        except (TypeError, ValueError):
            continue
        credits = float(row.get('credits', 0) or 0)
        points = grade_points_for(marks)
        if credits > 0:
            total_points += points * credits
            total_credits += credits
        else:
            total_points += points
            total_credits += 1
    return round(total_points / total_credits, 2) if total_credits else 0.0


def get_user_by_username(username):
    c = cur()
    c.execute('SELECT id, username, role, email, full_name FROM users WHERE username = %s', (username,))
    return c.fetchone()


def get_current_user():
    identity = get_jwt_identity()
    if not identity:
        return None
    return get_user_by_username(identity)


def requires_role(*roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user or user['role'] not in roles:
                return jsonify({'error': 'Permission denied'}), 403
            return fn(*args, **kwargs)

        return decorated

    return wrapper

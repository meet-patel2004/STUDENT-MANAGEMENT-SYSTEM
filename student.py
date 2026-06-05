import app
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import math


def parse_date(value):
    if isinstance(value, str):
        for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%a, %d %b %Y %H:%M:%S GMT'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    elif hasattr(value, 'year') and hasattr(value, 'month') and hasattr(value, 'day'):
        return value
    return None


@app.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    page = max(1, int(request.args.get('page', 1)))
    limit = int(request.args.get('limit', app.PAGE_SIZE))
    course = request.args.get('course', '').strip()
    name = request.args.get('name', '').strip()
    department = request.args.get('department', '').strip()
    offset = (page - 1) * limit

    where, params = [], []
    if course:
        where.append('course LIKE %s')
        params.append(f'%{course}%')
    if name:
        where.append('name LIKE %s')
        params.append(f'%{name}%')
    if department:
        where.append('department LIKE %s')
        params.append(f'%{department}%')

    where_sql = 'WHERE ' + ' AND '.join(where) if where else ''

    app.c = app.cur()
    app.c.execute(f'SELECT COUNT(*) AS total FROM students {where_sql}', params)
    total = app.c.fetchone()['total']

    app.c.execute(
        f'SELECT * FROM students {where_sql} ORDER BY id LIMIT %s OFFSET %s',
        params + [limit, offset],
    )
    students = app.c.fetchall()

    return jsonify(
        {
            'students': students,
            'page': page,
            'limit': limit,
            'total': total,
            'total_pages': math.ceil(total / limit) if limit else 0,
        }
    ), 200


@app.route('/students/<int:sid>', methods=['GET'])
@jwt_required()
def get_student(sid):
    app.c = app.cur()
    app.c.execute('SELECT * FROM students WHERE id = %s', (sid,))
    student = app.c.fetchone()
    if not student:
        return jsonify({'error': 'Student ID invalid'}), 404
    return jsonify(student), 200


@app.route('/students', methods=['POST'])
@app.requires_role('admin', 'teacher')
def add_student():
    data = request.get_json() or {}
    required = ['name', 'email', 'course', 'age', 'department', 'admission_date']
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({'error': f'Missing fields: {missing}'}), 400

    try:
        age = int(data['age'])
    except (TypeError, ValueError):
        return jsonify({'error': 'age must be an integer'}), 400

    admission_date = parse_date(data['admission_date'])
    if not admission_date:
        return jsonify({'error': 'admission_date must be a valid date in YYYY-MM-DD or RFC 1123 format'}), 400

    student = {
        'name': data['name'].strip(),
        'email': data['email'].strip(),
        'course': data['course'].strip(),
        'age': age,
        'phone': data.get('phone', '').strip() or None,
        'address': data.get('address', '').strip() or None,
        'guardian_name': data.get('guardian_name', '').strip() or None,
        'guardian_contact': data.get('guardian_contact', '').strip() or None,
        'department': data['department'].strip(),
        'admission_date': admission_date,
        'class_section': data.get('class_section', '').strip() or None,
    }

    app.c = app.cur()
    try:
        app.c.execute(
            '''INSERT INTO students
                   (name, email, course, age, phone, address, guardian_name, guardian_contact, department, admission_date, class_section)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (
                student['name'],
                student['email'],
                student['course'],
                student['age'],
                student['phone'],
                student['address'],
                student['guardian_name'],
                student['guardian_contact'],
                student['department'],
                student['admission_date'],
                student['class_section'],
            ),
        )
        app.mysql.connection.commit()
    except Exception as exc:
        if 'Duplicate entry' in str(exc) and 'email' in str(exc):
            return jsonify({'error': 'Email already exists'}), 409
        return jsonify({'error': 'Invalid student data'}), 400

    return jsonify({'message': 'Student profile added', 'id': app.c.lastrowid}), 201


@app.route('/students/<int:sid>', methods=['PUT'])
@app.requires_role('admin', 'teacher')
def update_student(sid):
    data = request.get_json() or {}
    updateable = [
        'name', 'email', 'course', 'age', 'phone', 'address',
        'guardian_name', 'guardian_contact', 'department', 'admission_date', 'class_section',
    ]
    fields = {k: data[k] for k in updateable if k in data}
    if not fields:
        return jsonify({'error': 'No valid fields to update'}), 400

    if 'age' in fields:
        try:
            fields['age'] = int(fields['age'])
        except (TypeError, ValueError):
            return jsonify({'error': 'age must be an integer'}), 400

    if 'admission_date' in fields:
        parsed_date = parse_date(fields['admission_date'])
        if not parsed_date:
            return jsonify({'error': 'admission_date must be a valid date in YYYY-MM-DD or RFC 1123 format'}), 400
        fields['admission_date'] = parsed_date

    app.c = app.cur()
    app.c.execute('SELECT id FROM students WHERE id = %s', (sid,))
    if not app.c.fetchone():
        return jsonify({'error': 'Student ID invalid'}), 404

    sql = 'UPDATE students SET ' + ', '.join(f'{k}=%s' for k in fields) + ' WHERE id=%s'
    app.c.execute(sql, list(fields.values()) + [sid])
    app.mysql.connection.commit()
    return jsonify({'message': 'Student profile updated'}), 200


@app.route('/students/<int:sid>', methods=['DELETE'])
@app.requires_role('admin')
def delete_student(sid):
    app.c = app.cur()
    app.c.execute('SELECT id FROM students WHERE id = %s', (sid,))
    if not app.c.fetchone():
        return jsonify({'error': 'Student ID invalid'}), 404
    app.c.execute('DELETE FROM students WHERE id = %s', (sid,))
    app.mysql.connection.commit()
    return jsonify({'message': 'Student profile deleted'}), 200
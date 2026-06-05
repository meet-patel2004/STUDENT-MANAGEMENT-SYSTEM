import app
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

@app.route('/students/<int:sid>/attendance', methods=['POST'])
@app.requires_role('admin', 'teacher')
def mark_attendance(sid):
    app.c = app.cur()
    app.c.execute('SELECT id FROM students WHERE id = %s', (sid,))
    if not app.c.fetchone():
        return jsonify({'error': 'Student ID invalid'}), 404

    data = request.get_json() or {}
    date = data.get('date')
    status = data.get('status', 'present').lower()
    note = data.get('note', '').strip() or None

    if not date:
        return jsonify({'error': 'date required (YYYY-MM-DD)'}), 400
    if status not in app.VALID_ATTENDANCE_STATUSES:
        return jsonify({'error': f'status must be one of {app.VALID_ATTENDANCE_STATUSES}'}), 400

    try:
        app.c.execute(
            '''INSERT INTO attendance (student_id, date, status, note)
               VALUES (%s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE status = %s, note = %s''',
            (sid, date, status, note, status, note),
        )
        app.mysql.connection.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Attendance recorded'}), 201


@app.route('/students/<int:sid>/attendance', methods=['GET'])
@jwt_required()
def get_attendance(sid):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    course = request.args.get('course', '').strip()
    department = request.args.get('department', '').strip()

    c = app.cur()
    c.execute('SELECT id FROM students WHERE id = %s', (sid,))
    if not c.fetchone():
        return jsonify({'error': 'Student ID invalid'}), 404

    where = ['student_id = %s']
    params = [sid]
    if start_date:
        where.append('date >= %s')
        params.append(start_date)
    if end_date:
        where.append('date <= %s')
        params.append(end_date)

    join_clause = 'JOIN students s ON s.id = attendance.student_id '
    if course:
        where.append('s.course LIKE %s')
        params.append(f'%{course}%')
    if department:
        where.append('s.department LIKE %s')
        params.append(f'%{department}%')

    where_sql = ' AND '.join(where)
    c.execute(
        f'SELECT attendance.date, attendance.status, attendance.note, s.course, s.department FROM attendance {join_clause} WHERE {where_sql} ORDER BY attendance.date DESC',
        params,
    )
    records = c.fetchall()

    total = len(records)
    present = sum(1 for r in records if r['status'] == 'present')
    pct = round((present / total * 100), 2) if total else 0

    return jsonify(
        {
            'student_id': sid,
            'records': records,
            'total_days': total,
            'present': present,
            'attendance_percent': pct,
        }
    ), 200


@app.route('/attendance/class-report', methods=['GET'])
@jwt_required()
def class_attendance_report():
    date = request.args.get('date')
    course = request.args.get('course', '').strip()
    department = request.args.get('department', '').strip()

    where, params = [], []
    if date:
        where.append('attendance.date = %s')
        params.append(date)
    if course:
        where.append('students.course LIKE %s')
        params.append(f'%{course}%')
    if department:
        where.append('students.department LIKE %s')
        params.append(f'%{department}%')

    where_sql = 'WHERE ' + ' AND '.join(where) if where else ''
    c = app.cur()
    c.execute(
        f'''SELECT attendance.date, students.course, students.department, attendance.status, COUNT(*) AS count
            FROM attendance
            JOIN students ON attendance.student_id = students.id
            {where_sql}
            GROUP BY attendance.date, students.course, students.department, attendance.status
            ORDER BY attendance.date DESC''',
        params,
    )

    report = []
    for row in c.fetchall():
        report.append(row)

    return jsonify({'report': report}), 200


@app.route('/attendance/daily-report', methods=['GET'])
@jwt_required()
def daily_attendance_report():
    date = request.args.get('date') or datetime.utcnow().strftime('%Y-%m-%d')
    c = app.cur()
    c.execute(
        'SELECT status, COUNT(*) AS count FROM attendance WHERE date = %s GROUP BY status',
        (date,),
    )
    summary = {row['status']: row['count'] for row in c.fetchall()}

    c.execute(
        '''SELECT students.course, attendance.status, COUNT(*) AS count
           FROM attendance
           JOIN students ON attendance.student_id = students.id
           WHERE attendance.date = %s
           GROUP BY students.course, attendance.status''',
        (date,),
    )
    by_class = c.fetchall()

    return jsonify({'date': date, 'summary': summary, 'by_class': by_class}), 200


@app.route('/attendance/analytics', methods=['GET'])
@jwt_required()
def attendance_analytics():
    c = app.cur()
    c.execute('SELECT status, COUNT(*) AS count FROM attendance GROUP BY status')
    counts = {row['status']: row['count'] for row in c.fetchall()}
    total = sum(counts.values())
    present = counts.get('present', 0)
    attendance_rate = round((present / total * 100), 2) if total else 0
    alerts = []
    if counts.get('absent', 0) > total * 0.15:
        alerts.append('High absence rate detected')
    if counts.get('late', 0) > total * 0.1:
        alerts.append('Frequent late arrivals detected')

    return jsonify({'counts': counts, 'attendance_rate': attendance_rate, 'alerts': alerts}), 200
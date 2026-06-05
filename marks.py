import app
from flask import request, jsonify
from flask_jwt_extended import jwt_required


@app.route('/students/<int:sid>/marks', methods=['POST'])
@app.requires_role('admin', 'teacher')
def add_marks(sid):
    data = request.get_json() or {}
    subject = data.get('subject')
    marks_val = data.get('marks')
    exam_date = data.get('exam_date')
    semester = data.get('semester', '').strip() or None
    assessment_type = data.get('assessment_type', 'exam').strip().lower()
    exam_type = data.get('exam_type', '').strip() or None
    credits = float(data.get('credits', 0) or 0)
    comments = data.get('comments', '').strip() or None

    if not subject or marks_val is None or not exam_date:
        return jsonify({'error': 'subject, marks, and exam_date required'}), 400
    if assessment_type not in app.VALID_ASSESSMENT_TYPES:
        return jsonify({'error': f'assessment_type must be one of {app.VALID_ASSESSMENT_TYPES}'}), 400

    marks_val = float(marks_val)
    if not (0 <= marks_val <= 100):
        return jsonify({'error': 'marks must be 0-100'}), 400

    grade = app.grade_for(marks_val)
    c = app.cur()
    c.execute('SELECT id FROM students WHERE id = %s', (sid,))
    if not c.fetchone():
        return jsonify({'error': 'Student ID invalid'}), 404

    c.execute(
        '''INSERT INTO marks (student_id, subject, marks, grade, exam_date, semester, assessment_type, exam_type, credits, comments)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
        (sid, subject.strip(), marks_val, grade, exam_date, semester, assessment_type, exam_type, credits, comments),
    )
    app.mysql.connection.commit()
    return jsonify({'message': 'Marks added', 'grade': grade}), 201


@app.route('/students/<int:sid>/marks', methods=['GET'])
@jwt_required()
def get_marks(sid):
    c = app.cur()
    c.execute('SELECT id FROM students WHERE id = %s', (sid,))
    if not c.fetchone():
        return jsonify({'error': 'Student ID invalid'}), 404

    c.execute(
        '''SELECT subject, marks, grade, exam_date, semester, assessment_type, exam_type, credits, comments
           FROM marks WHERE student_id = %s ORDER BY exam_date DESC''',
        (sid,),
    )
    records = c.fetchall()

    avg = round(sum(float(r['marks']) for r in records) / len(records), 2) if records else 0
    subject_stats = []
    if records:
        c.execute(
            '''SELECT subject,
                      AVG(marks) AS average,
                      MAX(marks) AS best,
                      MIN(marks) AS worst,
                      COUNT(*) AS attempts
               FROM marks WHERE student_id = %s GROUP BY subject ORDER BY subject''',
            (sid,),
        )
        for row in c.fetchall():
            row['average'] = round(float(row['average']), 2)
            subject_stats.append(row)

    return jsonify(
        {
            'student_id': sid,
            'marks': records,
            'average': avg,
            'overall_grade': app.grade_for(avg) if records else 'N/A',
            'subject_performance': subject_stats,
        }
    ), 200
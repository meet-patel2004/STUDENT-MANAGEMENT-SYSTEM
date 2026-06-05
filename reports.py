import app
from flask import jsonify, request, send_file
from flask_jwt_extended import jwt_required
from helper import cur, gpa_for, grade_for


@app.route('/students/<int:sid>/report', methods=['GET'])
@jwt_required()
def student_report(sid):
    c = app.cur()
    c.execute('SELECT * FROM students WHERE id = %s', (sid,))
    student = c.fetchone()
    if not student:
        return jsonify({'error': 'Student ID invalid'}), 404

    c.execute('SELECT status, COUNT(*) AS count FROM attendance WHERE student_id = %s GROUP BY status', (sid,))
    attendance_summary = {row['status']: row['count'] for row in c.fetchall()}

    c.execute('SELECT AVG(marks) AS avg_marks FROM marks WHERE student_id = %s', (sid,))
    avg_row = c.fetchone()
    average = round(float(avg_row['avg_marks']), 2) if avg_row and avg_row['avg_marks'] is not None else 0

    return jsonify(
        {
            'student': student,
            'attendance_summary': attendance_summary,
            'average_marks': average,
            'overall_grade': grade_for(average) if average else 'N/A',
        }
    ), 200


@app.route('/students/<int:sid>/performance', methods=['GET'])
@jwt_required()
def student_performance(sid):
    c = app.cur()
    c.execute('SELECT * FROM students WHERE id = %s', (sid,))
    student = c.fetchone()
    if not student:
        return jsonify({'error': 'Student ID invalid'}), 404

    c.execute('SELECT * FROM marks WHERE student_id = %s ORDER BY exam_date DESC', (sid,))
    records = c.fetchall()
    avg_marks = round(sum(float(r['marks']) for r in records) / len(records), 2) if records else 0
    gpa = app.gpa_for(records)
    cgpa = gpa

    subject_performance = []
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
        subject_performance.append(row)

    return jsonify(
        {
            'student': student,
            'average_marks': avg_marks,
            'grade': app.grade_for(avg_marks) if records else 'N/A',
            'gpa': gpa,
            'cgpa': cgpa,
            'subject_performance': subject_performance,
            'recent_results': records[:10],
        }
    ), 200


@app.route('/students/<int:sid>/transcript', methods=['GET'])
@jwt_required()
def student_transcript(sid):
    c = app.cur()
    c.execute('SELECT * FROM students WHERE id = %s', (sid,))
    student = c.fetchone()
    if not student:
        return jsonify({'error': 'Student ID invalid'}), 404

    c.execute('SELECT DISTINCT semester FROM marks WHERE student_id = %s ORDER BY semester', (sid,))
    semesters = [row['semester'] for row in c.fetchall() if row['semester']]

    transcript = []
    all_records = []
    for semester in semesters:
        c.execute(
            '''SELECT subject, marks, grade, credits, assessment_type, exam_type, exam_date, comments
               FROM marks WHERE student_id = %s AND semester = %s ORDER BY exam_date''',
            (sid, semester),
        )
        semester_records = c.fetchall()
        semester_gpa = app.gpa_for(semester_records)
        credits = sum(float(r.get('credits') or 0) for r in semester_records)
        transcript.append({
            'semester': semester,
            'gpa': semester_gpa,
            'credits': credits,
            'records': semester_records,
        })
        all_records.extend(semester_records)

    cgpa = app.gpa_for(all_records)

    return jsonify(
        {
            'student': student,
            'transcript': transcript,
            'cgpa': cgpa,
        }
    ), 200


@app.route('/students/<int:sid>/ranking', methods=['GET'])
@jwt_required()
def student_ranking(sid):
    c = app.cur()
    c.execute('SELECT department FROM students WHERE id = %s', (sid,))
    student = c.fetchone()
    if not student:
        return jsonify({'error': 'Student ID invalid'}), 404

    department = student['department']
    c.execute(
        '''SELECT students.id, students.name, AVG(marks.marks) AS avg_marks
           FROM students
           JOIN marks ON students.id = marks.student_id
           WHERE students.department = %s
           GROUP BY students.id ORDER BY avg_marks DESC''',
        (department,),
    )

    ranking = []
    for idx, row in enumerate(c.fetchall(), start=1):
        ranking.append({'rank': idx, 'student_id': row['id'], 'name': row['name'], 'average_marks': float(row['avg_marks'])})

    student_rank = next((r for r in ranking if r['student_id'] == sid), None)
    return jsonify({'department': department, 'rank': student_rank, 'ranking': ranking}), 200


@app.route('/exam-types', methods=['GET'])
@jwt_required()
def exam_types():
    c = cur()
    c.execute('SELECT DISTINCT exam_type FROM marks WHERE exam_type IS NOT NULL AND exam_type != ""')
    return jsonify({'exam_types': [row['exam_type'] for row in c.fetchall()]}), 200


@app.route('/semesters', methods=['GET'])
@jwt_required()
def semesters():
    c = cur()
    c.execute('SELECT DISTINCT semester FROM marks WHERE semester IS NOT NULL AND semester != ""')
    return jsonify({'semesters': [row['semester'] for row in c.fetchall()]}), 200

@app.route('/students/<int:sid>/report-card', methods=['GET'])
@jwt_required()
def student_report_card(sid):
    c = cur()
    c.execute('SELECT * FROM students WHERE id = %s', (sid,))
    student = c.fetchone()
    if not student:
        return jsonify({'error': 'Student ID invalid'}), 404

    c.execute('SELECT * FROM attendance WHERE student_id = %s', (sid,))
    attendance_summary = {status: 0 for status in app.VALID_ATTENDANCE_STATUSES}
    for row in c.fetchall():
        attendance_summary[row['status']] = attendance_summary.get(row['status'], 0) + 1

    c.execute('SELECT subject, assessment_type, exam_type, marks, grade, semester, exam_date FROM marks WHERE student_id = %s ORDER BY exam_date', (sid,))
    records = c.fetchall()
    gpa = gpa_for(records)
    cgpa = gpa

    pdf_buffer = app.generate_report_card(student, records, attendance_summary, gpa, cgpa)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'report_card_{sid}.pdf',
    )


@app.route('/reports/dashboard', methods=['GET'])
@jwt_required()
def dashboard_stats():
    c = cur()
    c.execute('SELECT AVG(marks) AS average_grade FROM marks')
    avg_row = c.fetchone()
    average_grade = round(float(avg_row['average_grade']), 2) if avg_row and avg_row['average_grade'] is not None else 0

    c.execute('SELECT COUNT(*) AS total, SUM(CASE WHEN status = "present" THEN 1 ELSE 0 END) AS present FROM attendance')
    attendance_row = c.fetchone()
    total_attendance = attendance_row['total'] or 0
    present_count = attendance_row['present'] or 0
    attendance_rate = round((present_count / total_attendance * 100), 2) if total_attendance else 0

    c.execute('SELECT COUNT(*) AS pass_count FROM marks WHERE marks >= 50')
    pass_count = c.fetchone()['pass_count']
    c.execute('SELECT COUNT(*) AS fail_count FROM marks WHERE marks < 50')
    fail_count = c.fetchone()['fail_count']

    c.execute(
        '''SELECT students.id, students.name, AVG(marks.marks) AS average_marks
           FROM students
           JOIN marks ON students.id = marks.student_id
           GROUP BY students.id ORDER BY average_marks DESC LIMIT 5''',
    )
    top_students = [{'student_id': row['id'], 'name': row['name'], 'average_marks': round(float(row['average_marks']), 2)} for row in c.fetchall()]

    return jsonify(
        {
            'average_grade': average_grade,
            'attendance_rate': attendance_rate,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'top_students': top_students,
        }
    ), 200
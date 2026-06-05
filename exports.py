import app
from flask import request
from flask_jwt_extended import jwt_required



@app.route('/export/students', methods=['GET'])
@jwt_required()
def export_students():
    export_format = request.args.get('format', 'csv')
    c = app.cur()
    c.execute('SELECT id, name, email, course, department, age, phone, admission_date FROM students ORDER BY id')
    rows = c.fetchall()
    headers = ['id', 'name', 'email', 'course', 'department', 'age', 'phone', 'admission_date']
    return app.build_export_response('students', headers, rows, export_format)


@app.route('/export/marks', methods=['GET'])
@jwt_required()
def export_marks():
    export_format = request.args.get('format', 'csv')
    c = app.cur()
    c.execute(
        '''SELECT marks.id, marks.student_id, students.name AS student_name, marks.subject, marks.marks, marks.grade,
                  marks.exam_date, marks.semester, marks.assessment_type, marks.exam_type, marks.credits, marks.comments
           FROM marks
           JOIN students ON marks.student_id = students.id
           ORDER BY marks.id''')
    rows = c.fetchall()
    headers = ['id', 'student_id', 'student_name', 'subject', 'marks', 'grade', 'exam_date', 'semester', 'assessment_type', 'exam_type', 'credits', 'comments']
    return app.build_export_response('marks', headers, rows, export_format)


@app.route('/export/attendance', methods=['GET'])
@jwt_required()
def export_attendance():
    export_format = request.args.get('format', 'csv')
    c = app.cur()
    c.execute(
        '''SELECT attendance.id, attendance.student_id, students.name AS student_name, students.course, attendance.date,
                  attendance.status, attendance.note
           FROM attendance
           JOIN students ON attendance.student_id = students.id
           ORDER BY attendance.date DESC''')
    rows = c.fetchall()
    headers = ['id', 'student_id', 'student_name', 'course', 'date', 'status', 'note']
    return app.build_export_response('attendance', headers, rows, export_format)
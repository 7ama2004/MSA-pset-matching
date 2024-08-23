from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)

class Student(db.Model):
    kerb = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dorm = db.Column(db.String(100), nullable=False)
    enrollments = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'
    
class Class(db.Model):
    number = db.Column(db.String(50), primary_key=True)
    enrollments = db.relationship('Enrollment', backref='class_', lazy=True)

    def __repr__(self):
        return f'<Student {self.name}>'

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_kerb = db.Column(db.String(10), db.ForeignKey('student.kerb'), nullable=False)
    class_number = db.Column(db.String(10), db.ForeignKey('class.number'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json
    new_student = Student(
        kerb=data['kerb'],
        name=data['name'],
        dorm=data['dorm'],
        enrollments=data['enrollments']
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully!'})

@app.route('/get_student/<string:kerb>', methods=['GET'])
def get_student(kerb):
    student = Student.query.get(kerb)
    if student:
        return jsonify({
            'kerb': student.kerb,
            'name': student.name,
            'dorm': student.dorm,
            'enrollments': student.enrollments
        })
    return jsonify({'message': 'Student not found!'})

@app.route('/update_student/<string:kerb>', methods=['PUT'])
def update_student(kerb):
    data = request.json
    student = Student.query.get(kerb)
    if student:
        student.name = data.get('name', student.name)
        student.dorm = data.get('dorm', student.dorm)
        student.enrollments = data.get('enrollments', student.enrollments)
        db.session.commit()
        return jsonify({'message': 'Student updated successfully!'})
    return jsonify({'message': 'Student not found!'})

@app.route('/delete_student/<string:kerb>', methods=['DELETE'])
def delete_student(kerb):
    student = Student.query.get(kerb)
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted successfully!'})
    return jsonify({'message': 'Student not found!'})



@app.route('/add_class', methods=['POST'])
def add_class():
    number = request.form['number']
    name = request.form['name']
    instructor = request.form['instructor']
    schedule = request.form['schedule']

    new_class = Class(number=number, name=name, instructor=instructor, schedule=schedule)
    db.session.add(new_class)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/enroll', methods=['POST'])
def enroll():
    student_kerb = request.form['student_kerb']
    class_number = request.form['class_number']

    new_enrollment = Enrollment(student_kerb=student_kerb, class_number=class_number)
    db.session.add(new_enrollment)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)

class Student(db.Model):
    kerb = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dorm = db.Column(db.String(100), nullable=False)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)

    def __repr__(self):
        return f'<Student {self.name}>'
    
class Class(db.Model):
    number = db.Column(db.String(50), primary_key=True)
    enrollments = db.relationship('Enrollment', backref='class_', lazy=True)

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
    # Use .get() method to avoid KeyError and provide default values
    data = request.json
    print(data)
    kerb = data['kerb']
    name = data['name']
    dorm = data['dorm']
    student = Student.query.get(kerb)

    if student:
        print('fraud detected')
        session['error_message'] = 'This student already exists.'
        return jsonify({'message': 'This student already exists.', 'kerb': kerb})
    
    # classes = classes.split()
    new_student = Student(kerb=kerb, name=name, dorm=dorm)
    print('new student', new_student.enrollments)
    db.session.add(new_student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully.', 'kerb': kerb})

@app.route('/dashboard')
def show_classes():
    classes = Class.query.all()
    return render_template('dashboard.html', classes=classes)

# @app.route('/add_student', methods=['POST'])
# def add_student():
    kerb = request.form['kerb']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']

    student = Student.query.get(kerb)
    if student:
        session['error_message'] = 'This student already exists.'  # Set error message in session
        # raise Error
        return redirect(url_for('index'))

    new_student = Student(kerb=kerb, first_name=first_name, last_name=last_name, email=email)
    try:
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('index'))
    except IntegrityError:
        db.session.rollback()
        session['error_message'] = 'Error occurred while adding student.'
        return redirect(url_for('index'))

@app.route('/get_student/<string:kerb>', methods=['GET'])
def get_student(kerb):
    student = Student.query.get(kerb)
    if student:
        return jsonify({
            'kerb': student.kerb,
            'name': student.name,
            'dorm': student.dorm,
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
    data = request.json
    class_number = data.get('class_number')
    title = data.get('title')

    if Class.query.get(class_number):
        return jsonify({'success': False, 'message': 'Class number already exists.'})

    new_class = Class(number=class_number)
    db.session.add(new_class)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/enroll', methods=['POST'])
def enroll():
    student_kerb = request.form['student_kerb']
    class_number = request.form['class_number']

    new_enrollment = Enrollment(student_kerb=student_kerb, class_number=class_number)
    db.session.add(new_enrollment)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/remove_enrollment/<int:id>')
def remove_enrollment(id):
    enrollment = Enrollment.query.get_or_404(id)
    db.session.delete(enrollment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/check_kerb', methods=['POST'])
def check_kerb():
    data = request.json
    kerb = data['kerb']
    student = Student.query.get(kerb)
    return jsonify({'exists': student is not None})

@app.route('/dashboard')
def dashboard():
    kerb = request.args.get('kerb')
    print(f"Received kerb: {kerb}")  # Debugging line
    return render_template('dashboard.html', kerb=kerb)

@app.route('/update_class', methods=['POST'])
def update_class():
    data = request.json
    print(data)

    number = data.get('class_number')
    field = data.get('field')
    value = data.get('value')

    class_ = Class.query.get_or_404(class_number)

    if field == 'title':
        class_.title = value
    else:
        return jsonify({'success': False})

    db.session.commit()
    return jsonify({'success': True})

@app.route('/signup')
def signup():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)

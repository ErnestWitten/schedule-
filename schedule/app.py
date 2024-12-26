from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Модель сотрудника
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    schedules = db.relationship('Schedule', backref='employee', lazy=True)


# Модель расписания
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Тип дня (work, day off, vacation, etc.)
    hours = db.Column(db.Integer, default=0)


@app.route('/')
def index():
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)


@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    if name:
        new_employee = Employee(name=name)
        try:
            db.session.add(new_employee)
            db.session.commit()
        except Exception as e:
            print(f"Error adding employee: {e}")
    return redirect(url_for('index'))


@app.route('/employee/<int:employee_id>')
def employee_schedule(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    schedules = Schedule.query.filter_by(employee_id=employee.id).order_by(Schedule.date).all()
    return render_template('employee.html', employee=employee, schedules=schedules)


@app.route('/add_schedule/<int:employee_id>', methods=['POST'])
def add_schedule(employee_id):
    date_str = request.form['date']
    schedule_type = request.form['type']
    hours = request.form['hours']
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    new_schedule = Schedule(employee_id=employee_id, date=date, type=schedule_type, hours=int(hours))
    try:
        db.session.add(new_schedule)
        db.session.commit()
    except Exception as e:
        print(f"Error adding schedule: {e}")

    return redirect(url_for('employee_schedule', employee_id=employee_id))


@app.route('/report/<int:employee_id>')
def report(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    schedules = Schedule.query.filter_by(employee_id=employee_id, type='work').all()
    total_hours = sum(schedule.hours for schedule in schedules)
    return render_template('report.html', employee=employee, total_hours=total_hours)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

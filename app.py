from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conference.db'  # База данных SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модели базы данных
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    event = db.relationship('Event', backref='finances')

# Создание базы данных
with app.app_context():
    db.create_all()

# Маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        participant = Participant(name=name, email=email)
        db.session.add(participant)
        db.session.commit()
        flash('Участник успешно зарегистрирован!', 'success')
        return redirect(url_for('participants'))
    return render_template('register.html')

@app.route('/participants')
def participants():
    participants = Participant.query.all()
    return render_template('participants.html', participants=participants)

@app.route('/edit_participant/<int:id>', methods=['GET', 'POST'])
def edit_participant(id):
    participant = Participant.query.get_or_404(id)
    if request.method == 'POST':
        participant.name = request.form['name']
        participant.email = request.form['email']
        db.session.commit()
        flash('Участник успешно обновлен!', 'success')
        return redirect(url_for('participants'))
    return render_template('edit_participant.html', participant=participant)

@app.route('/delete_participant/<int:id>', methods=['POST'])
def delete_participant(id):
    if request.method == 'POST':
        participant = Participant.query.get_or_404(id)
        db.session.delete(participant)
        db.session.commit()
        flash('Участник успешно удален!', 'success')
        return redirect(url_for('participants'))
    else:
        flash('Недопустимый метод запроса.', 'error')
        return redirect(url_for('participants'))

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        date_str = request.form['date']

        if not date_str:
            flash('Поле даты не может быть пустым.', 'error')
            return redirect(url_for('add_event'))

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Некорректный формат даты. Используйте формат ГГГГ-ММ-ДД.', 'error')
            return redirect(url_for('add_event'))

        event = Event(name=name, date=date)
        db.session.add(event)
        db.session.commit()
        flash('Мероприятие успешно добавлено!', 'success')
        return redirect(url_for('events'))

    return render_template('add_event.html')

@app.route('/events')
def events():
    events = Event.query.all()
    return render_template('events.html', events=events)

@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    event = Event.query.get_or_404(id)
    if request.method == 'POST':
        event.name = request.form['name']
        date_str = request.form['date']

        if not date_str:
            flash('Поле даты не может быть пустым.', 'error')
            return redirect(url_for('edit_event', id=id))

        try:
            event.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Некорректный формат даты. Используйте формат ГГГГ-ММ-ДД.', 'error')
            return redirect(url_for('edit_event', id=id))

        db.session.commit()
        flash('Мероприятие успешно обновлено!', 'success')
        return redirect(url_for('events'))

    return render_template('edit_event.html', event=event)

@app.route('/delete_event/<int:id>', methods=['POST'])
def delete_event(id):
    if request.method == 'POST':
        event = Event.query.get_or_404(id)
        db.session.delete(event)
        db.session.commit()
        flash('Мероприятие успешно удалено!', 'success')
        return redirect(url_for('events'))
    else:
        flash('Недопустимый метод запроса.', 'error')
        return redirect(url_for('events'))

@app.route('/add_finance', methods=['GET', 'POST'])
def add_finance():
    if request.method == 'POST':
        event_id = request.form['event_id']
        amount = float(request.form['amount'])
        description = request.form['description']
        finance = Finance(event_id=event_id, amount=amount, description=description)
        db.session.add(finance)
        db.session.commit()
        flash('Финансовая запись успешно добавлена!', 'success')
        return redirect(url_for('finances'))
    events = Event.query.all()
    return render_template('add_finance.html', events=events)

@app.route('/finances')
def finances():
    finances = Finance.query.all()
    return render_template('finances.html', finances=finances)

@app.route('/edit_finance/<int:id>', methods=['GET', 'POST'])
def edit_finance(id):
    finance = Finance.query.get_or_404(id)
    if request.method == 'POST':
        finance.event_id = request.form['event_id']
        finance.amount = float(request.form['amount'])
        finance.description = request.form['description']
        db.session.commit()
        flash('Финансовая запись успешно обновлена!', 'success')
        return redirect(url_for('finances'))
    events = Event.query.all()
    return render_template('edit_finance.html', finance=finance, events=events)

@app.route('/delete_finance/<int:id>', methods=['POST'])
def delete_finance(id):
    if request.method == 'POST':
        finance = Finance.query.get_or_404(id)
        db.session.delete(finance)
        db.session.commit()
        flash('Финансовая запись успешно удалена!', 'success')
        return redirect(url_for('finances'))
    else:
        flash('Недопустимый метод запроса.', 'error')
        return redirect(url_for('finances'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    flash('Вы успешно вышли из системы!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
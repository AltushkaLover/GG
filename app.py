from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import random
import string
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

USERS_FILE = 'users.json'


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


def generate_password(complexity='medium', length=12):
    """Генерация пароля по уровню сложности"""
    if complexity == 'simple':
        # Только буквы
        characters = string.ascii_letters
        length = max(6, min(20, length))
    elif complexity == 'medium':
        # Буквы + цифры
        characters = string.ascii_letters + string.digits
        length = max(8, min(25, length))
    elif complexity == 'strong':
        # Буквы + цифры + специальные символы
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        length = max(10, min(30, length))
    elif complexity == 'very_strong':
        # Все символы + больше специальных
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        length = max(12, min(40, length))
    else:
        characters = string.ascii_letters + string.digits
        length = 12

    password = ''.join(random.choice(characters) for _ in range(length))
    return password


@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not password:
            flash('Все поля обязательны', 'error')
            return render_template('register.html')

        if len(username) < 3:
            flash('Имя пользователя должно содержать минимум 3 символа', 'error')
            return render_template('register.html')

        if len(password) < 4:
            flash('Пароль должен содержать минимум 4 символа', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')

        users = load_users()

        if any(user['username'] == username for user in users):
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('register.html')

        new_user = {
            'username': username,
            'password': password,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        users.append(new_user)
        save_users(users)

        flash('Регистрация успешна! Теперь вы можете войти', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        users = load_users()
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)

        if user:
            session['username'] = user['username']
            flash(f'Добро пожаловать, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


@app.route('/generate', methods=['POST'])
@login_required
def generate():
    try:
        data = request.get_json()
        complexity = data.get('complexity', 'medium')
        length = int(data.get('length', 12))

        password = generate_password(complexity, length)

        return jsonify({
            'success': True,
            'password': password
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

from flask import Flask, render_template, request, jsonify
import random
import string

app = Flask(__name__)


def generate_password(length, use_uppercase, use_numbers, use_special):
    """
    Генерация пароля на основе выбранных параметров
    """
    characters = string.ascii_lowercase

    if use_uppercase:
        characters += string.ascii_uppercase
    if use_numbers:
        characters += string.digits
    if use_special:
        characters += string.punctuation

    # Гарантируем, что пароль будет содержать хотя бы один символ из каждой выбранной категории
    password = []

    if use_uppercase:
        password.append(random.choice(string.ascii_uppercase))
    if use_numbers:
        password.append(random.choice(string.digits))
    if use_special:
        password.append(random.choice(string.punctuation))

    # Заполняем оставшуюся длину случайными символами
    remaining_length = length - len(password)
    if remaining_length > 0:
        password.extend(random.choices(characters, k=remaining_length))

    # Перемешиваем символы
    random.shuffle(password)

    return ''.join(password)


def generate_by_complexity(complexity, length=None):
    """
    Генерация пароля по уровню сложности
    """
    if complexity == "easy":
        # Только буквы нижнего регистра
        length = length or 8
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    elif complexity == "medium":
        # Буквы обоих регистров и цифры
        length = length or 12
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=length))

    elif complexity == "hard":
        # Все символы
        length = length or 16
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choices(characters, k=length))

    elif complexity == "custom":
        # Пользовательские настройки
        length = request.json.get('length', 12)
        use_uppercase = request.json.get('uppercase', True)
        use_numbers = request.json.get('numbers', True)
        use_special = request.json.get('special', False)
        return generate_password(length, use_uppercase, use_numbers, use_special)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        complexity = data.get('complexity', 'medium')
        length = data.get('length')

        if complexity == 'custom':
            password = generate_by_complexity(complexity)
        else:
            password = generate_by_complexity(complexity, length)

        return jsonify({
            'success': True,
            'password': password,
            'length': len(password)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/batch-generate', methods=['POST'])
def batch_generate():
    try:
        data = request.json
        complexity = data.get('complexity', 'medium')
        count = data.get('count', 5)
        length = data.get('length')

        passwords = []
        for _ in range(count):
            if complexity == 'custom':
                password = generate_by_complexity(complexity)
            else:
                password = generate_by_complexity(complexity, length)
            passwords.append(password)

        return jsonify({
            'success': True,
            'passwords': passwords
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, jsonify, request
import json

app = Flask(__name__)


def load_data(category_name: str) -> list:
    try:
        with open(category_name+'.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as exception:
        print(f'Error on loading data: {exception}')
        return []
    except Exception as exception:
        print(f'Error on loading data: {exception}')
        return []


def save_data(data: dict, category_name: str) -> bool:
    try:
        with open(category_name+'.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            return True
    except Exception as exception:
        print(f'Error on saving data: {exception}')
        return False


@app.route('/')
def root():
    return 'Hello from School Manager!'


@app.route('/estudantes', methods=['GET'])
def get_estudantes():
    data = load_data('estudantes')
    return jsonify(data)


# port 500 is already used in macOS
app.run(host='localhost', port=5001, debug=True)
